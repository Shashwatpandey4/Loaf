# scripts/recipe_scraper.py
import re
import requests
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import uuid

from src.models.contracts import Recipe, Ingredient, ExtractedRecipe, ExtractedIngredient
from src.recipe_extraction import RecipeDetector
from scripts.utils import insert_recipe_to_db
from src.database.connection import get_connection


def recipe_exists_in_db(recipe_name: str) -> bool:
    """Check if a recipe exists in the database by name (case-insensitive)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM recipes WHERE LOWER(name) = LOWER(?)", (recipe_name,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0


def get_recipe_url_from_publicdomainrecipes(recipe_name: str) -> Optional[str]:
    """Search for a recipe on publicdomainrecipes.com and return its URL."""
    base_url = "https://publicdomainrecipes.com"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        # Try direct URL pattern first (recipes are typically at /recipe-name/)
        url_safe_name = recipe_name.lower().replace(" ", "-").replace("'", "").replace(",", "").replace("(", "").replace(")", "")
        potential_url = f"{base_url}/{url_safe_name}/"
        
        # Try to verify this URL exists
        test_response = session.get(potential_url, timeout=10, allow_redirects=False)
        if test_response.status_code == 200:
            return potential_url
        
        # If direct URL doesn't work, try searching the main page
        search_url = f"{base_url}/"
        response = session.get(search_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        recipe_name_lower = recipe_name.lower()
        
        # Search for links that might contain the recipe
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            link_text = link.get_text(strip=True).lower()
            
            # Check if the link text or href contains the recipe name
            if recipe_name_lower in link_text or recipe_name_lower in href.lower():
                # Construct full URL
                if href.startswith("/"):
                    full_url = urljoin(base_url, href)
                elif href.startswith("http"):
                    full_url = href
                else:
                    full_url = urljoin(base_url, "/" + href)
                
                # Verify it's a recipe page
                if "recipe" in full_url.lower() or not href.startswith("#"):
                    return full_url
                    
    except Exception as e:
        print(f"Error searching for recipe: {e}")
    
    return None


def scrape_recipe_from_publicdomainrecipes(recipe_name: str) -> Optional[Recipe]:
    """Scrape a recipe from publicdomainrecipes.com and convert it to Recipe format."""
    # Get the recipe URL
    recipe_url = get_recipe_url_from_publicdomainrecipes(recipe_name)
    if not recipe_url:
        print(f"Could not find recipe URL for: {recipe_name}")
        return None
    
    print(f"Found recipe URL: {recipe_url}")
    
    # Use existing RecipeDetector to extract recipe
    detector = RecipeDetector()
    extraction_response = detector.extract_recipe(recipe_url)
    
    if not extraction_response.success or not extraction_response.recipe:
        print(f"Failed to extract recipe from {recipe_url}")
        return None
    
    extracted_recipe = extraction_response.recipe
    
    # Convert ExtractedRecipe to Recipe format
    recipe = convert_extracted_to_recipe(extracted_recipe, recipe_name)
    
    return recipe


def convert_extracted_to_recipe(extracted: ExtractedRecipe, recipe_name: Optional[str] = None) -> Recipe:
    """Convert ExtractedRecipe to Recipe format."""
    # Generate a unique ID (you might want to use a hash of the name or URL)
    recipe_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    
    # Use provided name or extracted title
    name = recipe_name or extracted.title or "Unknown Recipe"
    
    # Convert ingredients
    ingredients = []
    for ext_ing in extracted.ingredients:
        ingredients.append(
            Ingredient(
                name=ext_ing.name,
                amount=ext_ing.amount or "",
                unit=ext_ing.unit or ""
            )
        )
    
    # Parse servings (try to extract number from string)
    servings = 2  # default
    if extracted.servings:
        servings_match = re.search(r'\d+', str(extracted.servings))
        if servings_match:
            servings = int(servings_match.group())
    
    # Determine difficulty (default to medium if not specified)
    difficulty = extracted.difficulty or "medium"
    
    # Determine cuisine type (default to Unknown if not specified)
    cuisine_type = extracted.cuisine_type or "Unknown"
    
    # Extract tags from various sources
    tags = extracted.tags or []
    if extracted.cuisine_type:
        tags.append(extracted.cuisine_type.lower())
    
    # Create Recipe object
    recipe = Recipe(
        id=recipe_id,
        name=name,
        description=extracted.description or "",
        cuisine_type=cuisine_type,
        difficulty=difficulty,
        prep_time=extracted.prep_time or "N/A",
        cook_time=extracted.cook_time or "N/A",
        servings=servings,
        ingredients=ingredients,
        instructions=extracted.instructions or [],
        tags=tags,
        spice_level="mild"  # Default, could be extracted if available
    )
    
    return recipe


def scrape_and_insert_recipe(recipe_name: str) -> bool:
    """Scrape a recipe from publicdomainrecipes.com and insert it into the database."""
    try:
        recipe = scrape_recipe_from_publicdomainrecipes(recipe_name)
        if recipe:
            insert_recipe_to_db(recipe)
            print(f"✅ Successfully scraped and inserted recipe: {recipe_name}")
            return True
        else:
            print(f"❌ Failed to scrape recipe: {recipe_name}")
            return False
    except Exception as e:
        print(f"❌ Error scraping recipe {recipe_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


