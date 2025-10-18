"""
Query processing and matching logic for the food KB answerer.
"""

import re
from typing import List, Tuple

from contracts import QueryAnalysis, Recipe
from knowledge_base import get_all_recipes


class QueryProcessor:
    """Processes and analyzes user food queries."""

    def __init__(self):
        self.cuisine_keywords = {
            "chinese": ["chinese", "china", "sichuan", "cantonese", "mandarin"],
            "japanese": ["japanese", "japan", "ramen", "miso", "sushi"],
            "thai": ["thai", "thailand", "pad thai", "curry"],
            "italian": ["italian", "italy", "pasta", "pizza", "risotto"],
            "mexican": ["mexican", "mexico", "taco", "burrito", "enchilada"],
            "indian": ["indian", "india", "curry", "biryani", "tikka"],
        }

        self.spice_keywords = {
            "mild": ["mild", "not spicy", "gentle", "soft", "light"],
            "medium": ["medium", "moderate", "some spice"],
            "hot": ["hot", "spicy", "fiery", "burning"],
            "extra-hot": ["extra hot", "very spicy", "extremely spicy", "super hot"],
        }

        self.difficulty_keywords = {
            "easy": ["easy", "simple", "quick", "basic", "beginner"],
            "medium": ["medium", "moderate", "intermediate"],
            "hard": ["hard", "difficult", "complex", "advanced", "challenging"],
        }

        self.dietary_keywords = {
            "vegetarian": ["vegetarian", "veggie", "no meat"],
            "vegan": ["vegan", "plant-based", "dairy-free"],
            "gluten-free": ["gluten-free", "gluten free", "no gluten"],
            "keto": ["keto", "ketogenic", "low carb"],
            "low-sodium": ["low sodium", "low salt", "no salt"],
        }

    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze user query and extract key information."""
        query_lower = query.lower()

        # Extract keywords
        keywords = self._extract_keywords(query_lower)

        # Detect intent
        intent = self._detect_intent(query_lower)

        # Detect cuisine preference
        cuisine_preference = self._detect_cuisine(query_lower)

        # Detect dietary restrictions
        dietary_restrictions = self._detect_dietary_restrictions(query_lower)

        # Detect spice preference
        spice_preference = self._detect_spice_preference(query_lower)

        # Detect complexity preference
        complexity_preference = self._detect_complexity_preference(query_lower)

        return QueryAnalysis(
            intent=intent,
            cuisine_preference=cuisine_preference,
            dietary_restrictions=dietary_restrictions,
            spice_preference=spice_preference,
            keywords=keywords,
            complexity_preference=complexity_preference,
        )

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from the query."""
        # Common food-related keywords
        food_keywords = [
            "noodles",
            "pasta",
            "rice",
            "curry",
            "soup",
            "stir-fry",
            "fried",
            "grilled",
            "baked",
            "roasted",
            "steamed",
            "boiled",
            "salad",
            "sandwich",
            "pizza",
            "burger",
            "taco",
            "burrito",
            "ramen",
            "pad thai",
            "spaghetti",
            "lasagna",
            "risotto",
            "quinoa",
        ]

        keywords = []
        for keyword in food_keywords:
            if keyword in query:
                keywords.append(keyword)

        # Add individual words that might be relevant
        words = re.findall(r"\b\w+\b", query)
        for word in words:
            if len(word) > 3 and word not in [
                "want",
                "need",
                "like",
                "love",
                "make",
                "cook",
            ]:
                keywords.append(word)

        return list(set(keywords))

    def _detect_intent(self, query: str) -> str:
        """Detect the user's intent."""
        if any(word in query for word in ["recipe", "how to make", "cook", "prepare"]):
            return "find_recipe"
        elif any(word in query for word in ["ingredients", "what do i need"]):
            return "get_ingredients"
        elif any(word in query for word in ["time", "how long", "duration"]):
            return "get_timing"
        else:
            return "find_recipe"  # Default intent

    def _detect_cuisine(self, query: str) -> str | None:
        """Detect cuisine preference from query."""
        for cuisine, keywords in self.cuisine_keywords.items():
            if any(keyword in query for keyword in keywords):
                return cuisine
        return None

    def _detect_dietary_restrictions(self, query: str) -> List[str]:
        """Detect dietary restrictions from query."""
        restrictions = []
        for restriction, keywords in self.dietary_keywords.items():
            if any(keyword in query for keyword in keywords):
                restrictions.append(restriction)
        return restrictions

    def _detect_spice_preference(self, query: str) -> str | None:
        """Detect spice preference from query."""
        for spice_level, keywords in self.spice_keywords.items():
            if any(keyword in query for keyword in keywords):
                return spice_level
        return None

    def _detect_complexity_preference(self, query: str) -> str | None:
        """Detect complexity preference from query."""
        for difficulty, keywords in self.difficulty_keywords.items():
            if any(keyword in query for keyword in keywords):
                return difficulty
        return None


class RecipeMatcher:
    """Matches recipes based on query analysis."""

    def __init__(self):
        self.recipes = get_all_recipes()

    def find_best_match(
        self, analysis: QueryAnalysis
    ) -> Tuple[Recipe | None, List[str], float]:
        """Find the best matching recipe based on query analysis."""
        if not analysis.keywords:
            return None, [], 0.0

        best_recipe = None
        best_score = 0.0
        matched_tags = []

        for recipe in self.recipes:
            score, tags = self._calculate_match_score(recipe, analysis)
            if score > best_score:
                best_score = score
                best_recipe = recipe
                matched_tags = tags

        return best_recipe, matched_tags, best_score

    def _calculate_match_score(
        self, recipe: Recipe, analysis: QueryAnalysis
    ) -> Tuple[float, List[str]]:
        """Calculate match score between recipe and query analysis."""
        score = 0.0
        matched_tags = []

        # Keyword matching (most important)
        keyword_matches = 0
        for keyword in analysis.keywords:
            keyword_lower = keyword.lower()

            # Check recipe name
            if keyword_lower in recipe.name.lower():
                keyword_matches += 2
                matched_tags.append(f"name:{keyword}")

            # Check recipe tags
            for tag in recipe.tags:
                if keyword_lower in tag.lower() or tag.lower() in keyword_lower:
                    keyword_matches += 3
                    matched_tags.append(f"tag:{tag}")

            # Check ingredients
            for ingredient in recipe.ingredients:
                if keyword_lower in ingredient.name.lower():
                    keyword_matches += 1
                    matched_tags.append(f"ingredient:{ingredient.name}")

        # Normalize keyword score (max possible is len(keywords) * 3)
        if analysis.keywords:
            score += (keyword_matches / (len(analysis.keywords) * 3)) * 0.6

        # Cuisine matching
        if (
            analysis.cuisine_preference
            and analysis.cuisine_preference.lower() == recipe.cuisine_type.lower()
        ):
            score += 0.2
            matched_tags.append(f"cuisine:{recipe.cuisine_type}")

        # Spice level matching
        if analysis.spice_preference and recipe.spice_level:
            if analysis.spice_preference.lower() == recipe.spice_level.lower():
                score += 0.15
                matched_tags.append(f"spice:{recipe.spice_level}")

        # Difficulty matching
        if (
            analysis.complexity_preference
            and analysis.complexity_preference.lower() == recipe.difficulty.lower()
        ):
            score += 0.05
            matched_tags.append(f"difficulty:{recipe.difficulty}")

        return min(score, 1.0), matched_tags
