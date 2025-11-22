# scripts/meal_plan_utils.py
import json
from typing import Dict, List, Optional
from datetime import datetime
from scripts.recipe_scraper import recipe_exists_in_db, scrape_and_insert_recipe


def check_meal_plan_recipes(meal_plan: Dict) -> Dict[str, Dict]:
    """
    Check which recipes in the meal plan are available in the database.
    Returns a dict with 'Available' and 'Unavailable' keys.
    """
    available = {}
    unavailable = {}
    
    for day_key, day_data in meal_plan.items():
        if isinstance(day_data, dict) and "recipe" in day_data:
            recipe_name = day_data["recipe"]
            if recipe_exists_in_db(recipe_name):
                available[day_key] = recipe_name
            else:
                unavailable[day_key] = recipe_name
    
    return {
        "Available": available,
        "Unavailable": unavailable
    }


def scrape_unavailable_recipes(unavailable_recipes: Dict[str, str]) -> Dict[str, bool]:
    """
    Scrape unavailable recipes from publicdomainrecipes.com.
    Returns a dict mapping recipe names to success status.
    """
    results = {}
    for day_key, recipe_name in unavailable_recipes.items():
        print(f"\nScraping recipe: {recipe_name} (for {day_key})")
        success = scrape_and_insert_recipe(recipe_name)
        results[recipe_name] = success
    return results


def save_meal_plan_to_file(meal_plan: Dict, filename: str = "meal_plan_nested.json"):
    """Save meal plan to a JSON file with date as parent key."""
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Load existing data if file exists
    existing_data = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        # File doesn't exist yet, start with empty dict
        existing_data = {}
    except json.JSONDecodeError:
        # File exists but is invalid JSON, start fresh
        print(f"Warning: {filename} contains invalid JSON. Starting fresh.")
        existing_data = {}
    
    # Add the meal plan under today's date
    existing_data[today] = meal_plan
    
    # Write the updated data back to the file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f"Meal plan saved to {filename} under date {today}")

