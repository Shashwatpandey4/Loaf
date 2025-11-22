# scripts/test_meal_plan.py
"""
Test script for meal plan functionality with a recipe not in the database.
"""
import os
import sys
import ast

# Add parent directory to path for direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from scripts.meal_plan_utils import (
    check_meal_plan_recipes,
    scrape_unavailable_recipes,
    save_meal_plan_to_file
)
from scripts.recipe_scraper import recipe_exists_in_db


def test_mock_meal_plan(mock_meal_plan):
    """Test the meal plan flow with a mock meal plan containing a recipe not in DB."""
    
    # Mock meal plan - using a recipe that's likely not in the database
    # Let's use "Tiramisù" from publicdomainrecipes.com as an example
    # mock_meal_plan = {
    #     "day_1": {"recipe": "Spicy Sichuan Noodles", "reason": "High protein, vegetarian option"},
    #     "day_2": {"recipe": "Miso Ramen", "reason": "Comfort food, easy to make"},
    #     "day_3": {"recipe": "Spicy Pad Thai", "reason": "Flavorful and satisfying"},
    #     "day_4": {"recipe": "Creamy Mushroom Pasta", "reason": "Vegetarian comfort food"},
    #     "day_5": {"recipe": "Finnish Salmon Soup", "reason": "Good for the winter"},  # This might not be in DB
    #     "day_6": {"recipe": "Spicy Thai Green Curry", "reason": "Aromatic and spicy"},
    #     "day_7": {"recipe": "Mushroom Crepes with Vegetarian Sauce", "reason": "Brunch-style meal"}
    # }

    mock_meal_plan = ast.literal_eval(mock_meal_plan)

    # print(mock_meal_plan)
    
    print("=" * 60)
    print("🧪 Testing Meal Plan Flow")
    print("=" * 60)
    print("\n📋 Mock Meal Plan:")
    print(json.dumps(mock_meal_plan, indent=2))
    
    # Step 1: Check which recipes are available/unavailable
    print("\n" + "=" * 60)
    print("Step 1: Checking recipe availability in database")
    print("=" * 60)
    
    availability = check_meal_plan_recipes(mock_meal_plan)
    print("\n📊 Availability Check Results:")
    print(json.dumps(availability, indent=2))
    
    # Step 2: If there are unavailable recipes, scrape them
    if availability["Unavailable"]:
        print("\n" + "=" * 60)
        print("Step 2: Scraping unavailable recipes")
        print("=" * 60)
        
        scrape_results = scrape_unavailable_recipes(availability["Unavailable"])
        print("\n📊 Scraping Results:")
        print(json.dumps(scrape_results, indent=2))
        
        # Verify all recipes are now available
        print("\n" + "=" * 60)
        print("Step 3: Verifying all recipes are now in database")
        print("=" * 60)
        
        final_check = check_meal_plan_recipes(mock_meal_plan)
        if final_check["Unavailable"]:
            print("Some recipes still unavailable:")
            print(json.dumps(final_check["Unavailable"], indent=2))
        else:
            print("All recipes are now available in the database!")
    else:
        print("\nAll recipes are already in the database!")
    
    # Step 3: Save the meal plan
    print("\n" + "=" * 60)
    print("Step 4: Saving meal plan to meal_plan_nested.json")
    print("=" * 60)
    
    save_meal_plan_to_file(mock_meal_plan)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


def test_single_recipe_check():
    """Test checking if a specific recipe exists."""
    print("\n" + "=" * 60)
    print("Testing Single Recipe Check")
    print("=" * 60)
    
    test_recipes = [
        "Spicy Sichuan Noodles",  # Should be in DB
        "Finnish Salmon Soup",  # Might not be in DB
    ]
    
    for recipe_name in test_recipes:
        exists = recipe_exists_in_db(recipe_name)
        status = "[EXISTS]" if exists else "[NOT FOUND]"
        print(f"{status}: {recipe_name}")


# if __name__ == "__main__":
#     # First, test single recipe checks
#     test_single_recipe_check()
    
#     # Then, test the full meal plan flow
#     test_mock_meal_plan()

