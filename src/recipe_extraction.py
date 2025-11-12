"""
Recipe detection and extraction from web pages.
"""

import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import extruct
import requests
from bs4 import BeautifulSoup

from models.contracts import (
    ExtractedIngredient,
    ExtractedRecipe,
    RecipeExtractionResponse,
)


class StructuredDataExtractor:
    """Extract recipe data using extruct for JSON-LD and Microdata."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def extract_recipe(self, url: str) -> Optional[ExtractedRecipe]:
        """Extract recipe using structured data."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            # Extract structured data
            data = extruct.extract(
                response.text, base_url=url, syntaxes=["json-ld", "microdata"]
            )

            # Look for Recipe schema
            recipe_data = self._find_recipe_schema(data)
            if recipe_data:
                return self._parse_structured_recipe(recipe_data, url)

            return None

        except Exception as e:
            print(f"Structured data extraction error: {e}")
            return None

    def _find_recipe_schema(self, data: Dict[str, List[Dict]]) -> Optional[Dict]:
        """Find Recipe schema in structured data."""
        # Check JSON-LD
        for item in data.get("json-ld", []):
            if isinstance(item, dict):
                if item.get("@type") == "Recipe":
                    return item
                # Check nested recipes
                for key, value in item.items():
                    if isinstance(value, dict) and value.get("@type") == "Recipe":
                        return value
                    elif isinstance(value, list):
                        for sub_item in value:
                            if (
                                isinstance(sub_item, dict)
                                and sub_item.get("@type") == "Recipe"
                            ):
                                return sub_item

        # Check Microdata
        for item in data.get("microdata", []):
            if isinstance(item, dict):
                if item.get("type") == "http://schema.org/Recipe":
                    return item

        return None

    def _parse_structured_recipe(self, recipe_data: Dict, url: str) -> ExtractedRecipe:
        """Parse structured recipe data into ExtractedRecipe."""

        # Extract basic info
        title = self._safe_get(recipe_data, ["name", "headline"])
        description = self._safe_get(recipe_data, ["description"])
        author = self._safe_get(recipe_data, ["author", "name"])

        # Extract timing
        prep_time = self._safe_get(recipe_data, ["prepTime"])
        cook_time = self._safe_get(recipe_data, ["cookTime"])
        total_time = self._safe_get(recipe_data, ["totalTime"])

        # Extract servings and yield
        servings = self._safe_get(recipe_data, ["recipeYield"])
        yield_amount = self._safe_get(recipe_data, ["recipeYield"])

        # Extract ingredients
        ingredients = self._extract_ingredients(recipe_data)

        # Extract instructions
        instructions = self._extract_instructions(recipe_data)

        # Extract additional info
        nutrition_info = self._extract_nutrition(recipe_data)
        rating = self._safe_get_float(recipe_data, ["aggregateRating", "ratingValue"])
        review_count = self._safe_get_int(
            recipe_data, ["aggregateRating", "reviewCount"]
        )

        # Extract image
        image_url = self._safe_get(recipe_data, ["image", "url"])
        if not image_url and isinstance(recipe_data.get("image"), list):
            image_url = (
                self._safe_get(recipe_data["image"][0], ["url"])
                if recipe_data["image"]
                else None
            )

        return ExtractedRecipe(
            url=url,
            title=title,
            description=description,
            author=author,
            prep_time=prep_time,
            cook_time=cook_time,
            total_time=total_time,
            servings=servings,
            yield_amount=yield_amount,
            ingredients=ingredients,
            instructions=instructions,
            nutrition_info=nutrition_info,
            rating=rating,
            review_count=review_count,
            image_url=image_url,
            extraction_method="structured_data",
            extraction_confidence=0.9,
        )

    def _safe_get(self, data: Dict, keys: List[str]) -> Optional[str]:
        """Safely get nested value from dictionary."""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return str(current) if current is not None else None

    def _safe_get_float(self, data: Dict, keys: List[str]) -> Optional[float]:
        """Safely get nested float value from dictionary."""
        value = self._safe_get(data, keys)
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None

    def _safe_get_int(self, data: Dict, keys: List[str]) -> Optional[int]:
        """Safely get nested int value from dictionary."""
        value = self._safe_get(data, keys)
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None

    def _extract_ingredients(self, recipe_data: Dict) -> List[ExtractedIngredient]:
        """Extract ingredients from recipe data."""
        ingredients = []

        recipe_ingredients = recipe_data.get("recipeIngredient", [])
        if not recipe_ingredients:
            recipe_ingredients = recipe_data.get("ingredients", [])

        for ingredient_text in recipe_ingredients:
            if isinstance(ingredient_text, str):
                # Parse ingredient text
                parsed = self._parse_ingredient_text(ingredient_text)
                ingredients.append(
                    ExtractedIngredient(
                        name=parsed["name"],
                        amount=parsed["amount"],
                        unit=parsed["unit"],
                        raw_text=ingredient_text,
                    )
                )

        return ingredients

    def _extract_instructions(self, recipe_data: Dict) -> List[str]:
        """Extract instructions from recipe data."""
        instructions = []

        recipe_instructions = recipe_data.get("recipeInstructions", [])
        if not recipe_instructions:
            recipe_instructions = recipe_data.get("instructions", [])

        for instruction in recipe_instructions:
            if isinstance(instruction, str):
                instructions.append(instruction.strip())
            elif isinstance(instruction, dict):
                # Handle structured instructions
                text = instruction.get("text", instruction.get("name", ""))
                if text:
                    instructions.append(text.strip())

        return instructions

    def _extract_nutrition(self, recipe_data: Dict) -> Optional[Dict[str, Any]]:
        """Extract nutrition information."""
        nutrition = recipe_data.get("nutrition", {})
        if nutrition:
            return nutrition
        return None

    def _parse_ingredient_text(self, text: str) -> Dict[str, Optional[str]]:
        """Parse ingredient text to extract amount, unit, and name."""
        # Common patterns for ingredient parsing
        patterns = [
            r"^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(.+)$",  # "2 cups flour"
            r"^(\d+(?:\.\d+)?)\s+(.+)$",  # "2 eggs"
            r"^(\d+(?:/\d+)?)\s*([a-zA-Z]+)\s+(.+)$",  # "1/2 cup sugar"
        ]

        for pattern in patterns:
            match = re.match(pattern, text.strip())
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    return {"amount": groups[0], "unit": groups[1], "name": groups[2]}
                elif len(groups) == 2:
                    return {"amount": groups[0], "unit": None, "name": groups[1]}

        # Fallback: treat entire text as name
        return {"amount": None, "unit": None, "name": text.strip()}


class RecipeDetector:
    """Unified recipe detector that combines structured data and HTML fallback extraction."""

    def __init__(self):
        self.structured_extractor = StructuredDataExtractor()
        self.html_extractor = HTMLFallbackExtractor()

    def extract_recipe(self, url: str) -> RecipeExtractionResponse:
        """Extract recipe from URL using multiple methods."""
        start_time = time.time()
        methods_tried = []

        try:
            # Method 1: Try structured data extraction first (highest confidence)
            methods_tried.append("structured_data")
            recipe = self.structured_extractor.extract_recipe(url)

            if recipe and recipe.extraction_confidence >= 0.7:
                extraction_time_ms = int((time.time() - start_time) * 1000)
                return RecipeExtractionResponse(
                    url=url,
                    success=True,
                    recipe=recipe,
                    extraction_time_ms=extraction_time_ms,
                    extraction_methods_tried=methods_tried,
                )

            # Method 2: Try HTML fallback extraction
            methods_tried.append("html_fallback")
            recipe = self.html_extractor.extract_recipe(url)

            if recipe and recipe.extraction_confidence >= 0.3:
                extraction_time_ms = int((time.time() - start_time) * 1000)
                return RecipeExtractionResponse(
                    url=url,
                    success=True,
                    recipe=recipe,
                    extraction_time_ms=extraction_time_ms,
                    extraction_methods_tried=methods_tried,
                )

            # No successful extraction
            extraction_time_ms = int((time.time() - start_time) * 1000)
            return RecipeExtractionResponse(
                url=url,
                success=False,
                extraction_time_ms=extraction_time_ms,
                error_message="No recipe data found using available extraction methods",
                extraction_methods_tried=methods_tried,
            )

        except Exception as e:
            extraction_time_ms = int((time.time() - start_time) * 1000)
            return RecipeExtractionResponse(
                url=url,
                success=False,
                extraction_time_ms=extraction_time_ms,
                error_message=str(e),
                extraction_methods_tried=methods_tried,
            )

    def extract_multiple_recipes(
        self, urls: List[str]
    ) -> List[RecipeExtractionResponse]:
        """Extract recipes from multiple URLs."""
        results = []
        for url in urls:
            result = self.extract_recipe(url)
            results.append(result)
        return results


class HTMLFallbackExtractor:
    """Extract recipe data using HTML parsing and pattern matching."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

    def extract_recipe(self, url: str) -> Optional[ExtractedRecipe]:
        """Extract recipe using HTML parsing fallback."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract basic info
            title = self._extract_title(soup)
            description = self._extract_description(soup)

            # Extract ingredients using pattern matching
            ingredients = self._extract_ingredients_from_html(soup)

            # Extract instructions using pattern matching
            instructions = self._extract_instructions_from_html(soup)

            # Extract timing info
            prep_time, cook_time, total_time = self._extract_timing(soup)

            # Extract servings
            servings = self._extract_servings(soup)

            # Extract image
            image_url = self._extract_image(soup, url)

            # Calculate confidence based on what we found
            confidence = self._calculate_confidence(title, ingredients, instructions)

            if confidence < 0.3:
                return None

            return ExtractedRecipe(
                url=url,
                title=title,
                description=description,
                prep_time=prep_time,
                cook_time=cook_time,
                total_time=total_time,
                servings=servings,
                ingredients=ingredients,
                instructions=instructions,
                image_url=image_url,
                extraction_method="html_fallback",
                extraction_confidence=confidence,
            )

        except Exception as e:
            print(f"HTML fallback extraction error: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract recipe title from HTML."""
        # Try common title selectors
        title_selectors = [
            "h1.recipe-title",
            'h1[class*="recipe"]',
            'h1[class*="title"]',
            ".recipe-title",
            ".recipe-name",
            "h1",
            "title",
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)

        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract recipe description from HTML."""
        desc_selectors = [
            ".recipe-description",
            ".recipe-summary",
            ".recipe-intro",
            '[class*="description"]',
            'meta[name="description"]',
        ]

        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == "meta":
                    return element.get("content", "").strip()
                else:
                    text = element.get_text(strip=True)
                    if text:
                        return text

        return None

    def _extract_ingredients_from_html(
        self, soup: BeautifulSoup
    ) -> List[ExtractedIngredient]:
        """Extract ingredients using HTML parsing and pattern matching."""
        ingredients = []

        # Try to find ingredients container
        ingredient_containers = [
            ".ingredients",
            ".recipe-ingredients",
            '[class*="ingredient"]',
            ".ingredient-list",
            ".recipe-ingredient-list",
        ]

        ingredient_elements = []
        for selector in ingredient_containers:
            container = soup.select_one(selector)
            if container:
                # Look for list items or paragraphs within container
                ingredient_elements.extend(container.find_all(["li", "p", "div"]))
                break

        # If no container found, look for common patterns
        if not ingredient_elements:
            # Look for lists that might contain ingredients
            lists = soup.find_all(["ul", "ol"])
            for list_elem in lists:
                items = list_elem.find_all("li")
                if len(items) >= 3:  # Likely ingredient list
                    ingredient_elements.extend(items)

        # Extract ingredients from found elements
        for element in ingredient_elements:
            text = element.get_text(strip=True)
            if text and self._looks_like_ingredient(text):
                parsed = self._parse_ingredient_text(text)
                ingredients.append(
                    ExtractedIngredient(
                        name=parsed["name"],
                        amount=parsed["amount"],
                        unit=parsed["unit"],
                        raw_text=text,
                    )
                )

        return ingredients

    def _extract_instructions_from_html(self, soup: BeautifulSoup) -> List[str]:
        """Extract instructions using HTML parsing and pattern matching."""
        instructions = []

        # Try to find instructions container
        instruction_containers = [
            ".instructions",
            ".recipe-instructions",
            ".directions",
            ".recipe-directions",
            '[class*="instruction"]',
            ".steps",
            ".recipe-steps",
        ]

        instruction_elements = []
        for selector in instruction_containers:
            container = soup.select_one(selector)
            if container:
                # Look for list items, paragraphs, or divs within container
                instruction_elements.extend(container.find_all(["li", "p", "div"]))
                break

        # If no container found, look for numbered lists
        if not instruction_elements:
            # Look for ordered lists (likely instructions)
            ol_elements = soup.find_all("ol")
            for ol in ol_elements:
                items = ol.find_all("li")
                if len(items) >= 2:  # Likely instruction list
                    instruction_elements.extend(items)

        # Extract instructions from found elements
        for element in instruction_elements:
            text = element.get_text(strip=True)
            if text and self._looks_like_instruction(text):
                instructions.append(text)

        return instructions

    def _extract_timing(
        self, soup: BeautifulSoup
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract timing information from HTML."""
        prep_time = None
        cook_time = None
        total_time = None

        # Look for timing elements
        timing_selectors = [
            ".prep-time",
            ".cook-time",
            ".total-time",
            ".recipe-prep-time",
            ".recipe-cook-time",
            ".recipe-total-time",
            '[class*="prep"]',
            '[class*="cook"]',
            '[class*="time"]',
        ]

        for selector in timing_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if "prep" in selector.lower() or "prep" in text.lower():
                    prep_time = text
                elif "cook" in selector.lower() or "cook" in text.lower():
                    cook_time = text
                elif "total" in selector.lower() or "total" in text.lower():
                    total_time = text

        return prep_time, cook_time, total_time

    def _extract_servings(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract servings information from HTML."""
        serving_selectors = [
            ".servings",
            ".recipe-servings",
            ".yield",
            '[class*="serving"]',
            '[class*="yield"]',
        ]

        for selector in serving_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return None

    def _extract_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract recipe image from HTML."""
        # Look for recipe images
        img_selectors = [
            ".recipe-image img",
            ".recipe-photo img",
            ".recipe-img img",
            '[class*="recipe"] img',
            'img[alt*="recipe"]',
            'img[class*="recipe"]',
        ]

        for selector in img_selectors:
            img = soup.select_one(selector)
            if img and img.get("src"):
                src = img.get("src")
                if src.startswith("http"):
                    return src
                else:
                    return urljoin(base_url, src)

        return None

    def _looks_like_ingredient(self, text: str) -> bool:
        """Check if text looks like an ingredient."""
        # Common ingredient patterns
        ingredient_patterns = [
            r"\d+\s*(cup|tbsp|tsp|oz|lb|g|kg|ml|l|gram|pound|ounce)",
            r"\d+/\d+\s*(cup|tbsp|tsp|oz|lb)",
            r"\d+\s*(clove|slice|piece|whole|half)",
            r"(salt|pepper|oil|butter|flour|sugar|egg|milk)",
            r"(fresh|dried|chopped|sliced|minced|grated)",
        ]

        text_lower = text.lower()
        for pattern in ingredient_patterns:
            if re.search(pattern, text_lower):
                return True

        # Check for common ingredient keywords
        ingredient_keywords = [
            "cup",
            "tablespoon",
            "teaspoon",
            "ounce",
            "pound",
            "gram",
            "salt",
            "pepper",
            "oil",
            "butter",
            "flour",
            "sugar",
            "egg",
            "milk",
            "cheese",
            "onion",
            "garlic",
            "tomato",
            "chicken",
            "beef",
            "pork",
            "fish",
            "rice",
            "pasta",
            "bread",
        ]

        return any(keyword in text_lower for keyword in ingredient_keywords)

    def _looks_like_instruction(self, text: str) -> bool:
        """Check if text looks like a cooking instruction."""
        # Common instruction patterns
        instruction_patterns = [
            r"(heat|boil|simmer|fry|bake|roast|grill|cook)",
            r"(add|mix|stir|combine|blend|whisk)",
            r"(preheat|season|drain|serve|garnish)",
            r"(minutes|hours|until|until golden|until tender)",
            r"(degrees|temperature|medium|high|low heat)",
        ]

        text_lower = text.lower()
        for pattern in instruction_patterns:
            if re.search(pattern, text_lower):
                return True

        # Check for common instruction keywords
        instruction_keywords = [
            "heat",
            "boil",
            "simmer",
            "fry",
            "bake",
            "roast",
            "grill",
            "add",
            "mix",
            "stir",
            "combine",
            "blend",
            "whisk",
            "beat",
            "preheat",
            "season",
            "drain",
            "serve",
            "garnish",
            "chop",
            "slice",
            "dice",
            "mince",
            "grate",
            "peel",
            "cut",
        ]

        return any(keyword in text_lower for keyword in instruction_keywords)

    def _calculate_confidence(
        self, title: Optional[str], ingredients: List, instructions: List
    ) -> float:
        """Calculate confidence score for extracted recipe."""
        score = 0.0

        if title:
            score += 0.2

        if ingredients:
            score += min(0.4, len(ingredients) * 0.05)

        if instructions:
            score += min(0.4, len(instructions) * 0.05)

        return min(score, 1.0)

    def _parse_ingredient_text(self, text: str) -> Dict[str, Optional[str]]:
        """Parse ingredient text to extract amount, unit, and name."""
        # Common patterns for ingredient parsing
        patterns = [
            r"^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(.+)$",  # "2 cups flour"
            r"^(\d+(?:\.\d+)?)\s+(.+)$",  # "2 eggs"
            r"^(\d+(?:/\d+)?)\s*([a-zA-Z]+)\s+(.+)$",  # "1/2 cup sugar"
        ]

        for pattern in patterns:
            match = re.match(pattern, text.strip())
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    return {"amount": groups[0], "unit": groups[1], "name": groups[2]}
                elif len(groups) == 2:
                    return {"amount": groups[0], "unit": None, "name": groups[1]}

        # Fallback: treat entire text as name
        return {"amount": None, "unit": None, "name": text.strip()}


class RecipeDetector:
    """Unified recipe detector that combines structured data and HTML fallback extraction."""

    def __init__(self):
        self.structured_extractor = StructuredDataExtractor()
        self.html_extractor = HTMLFallbackExtractor()

    def extract_recipe(self, url: str) -> RecipeExtractionResponse:
        """Extract recipe from URL using multiple methods."""
        start_time = time.time()
        methods_tried = []

        try:
            # Method 1: Try structured data extraction first (highest confidence)
            methods_tried.append("structured_data")
            recipe = self.structured_extractor.extract_recipe(url)

            if recipe and recipe.extraction_confidence >= 0.7:
                extraction_time_ms = int((time.time() - start_time) * 1000)
                return RecipeExtractionResponse(
                    url=url,
                    success=True,
                    recipe=recipe,
                    extraction_time_ms=extraction_time_ms,
                    extraction_methods_tried=methods_tried,
                )

            # Method 2: Try HTML fallback extraction
            methods_tried.append("html_fallback")
            recipe = self.html_extractor.extract_recipe(url)

            if recipe and recipe.extraction_confidence >= 0.3:
                extraction_time_ms = int((time.time() - start_time) * 1000)
                return RecipeExtractionResponse(
                    url=url,
                    success=True,
                    recipe=recipe,
                    extraction_time_ms=extraction_time_ms,
                    extraction_methods_tried=methods_tried,
                )

            # No successful extraction
            extraction_time_ms = int((time.time() - start_time) * 1000)
            return RecipeExtractionResponse(
                url=url,
                success=False,
                extraction_time_ms=extraction_time_ms,
                error_message="No recipe data found using available extraction methods",
                extraction_methods_tried=methods_tried,
            )

        except Exception as e:
            extraction_time_ms = int((time.time() - start_time) * 1000)
            return RecipeExtractionResponse(
                url=url,
                success=False,
                extraction_time_ms=extraction_time_ms,
                error_message=str(e),
                extraction_methods_tried=methods_tried,
            )

    def extract_multiple_recipes(
        self, urls: List[str]
    ) -> List[RecipeExtractionResponse]:
        """Extract recipes from multiple URLs."""
        results = []
        for url in urls:
            result = self.extract_recipe(url)
            results.append(result)
        return results
