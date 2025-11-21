# scripts/meal_plan_tools.py
"""
Tools for meal plan handling that can be used with agno Agent.
"""
from typing import Dict, Any, List
from scripts.meal_plan_utils import (
    check_meal_plan_recipes,
    scrape_unavailable_recipes,
    save_meal_plan_to_file
)
from scripts.recipe_scraper import recipe_exists_in_db, scrape_and_insert_recipe


class MealPlanTools:
    """Tools for handling meal plan generation with recipe validation."""
    
    @staticmethod
    def check_recipe_exists(recipe_name: str) -> Dict[str, Any]:
        """Check if a recipe exists in the database."""
        exists = recipe_exists_in_db(recipe_name)
        return {
            "recipe_name": recipe_name,
            "exists": exists
        }
    
    @staticmethod
    def validate_meal_plan(meal_plan: Dict) -> Dict[str, Any]:
        """Validate a meal plan and return available/unavailable recipes."""
        return check_meal_plan_recipes(meal_plan)
    
    @staticmethod
    def scrape_recipes(recipe_names: List[str]) -> Dict[str, Any]:
        """Scrape multiple recipes from publicdomainrecipes.com."""
        results = {}
        for recipe_name in recipe_names:
            success = scrape_and_insert_recipe(recipe_name)
            results[recipe_name] = success
        return results
    
    @staticmethod
    def save_meal_plan(meal_plan: Dict) -> Dict[str, Any]:
        """Save meal plan to meal_plan_nested.json."""
        save_meal_plan_to_file(meal_plan)
        return {"status": "saved", "meal_plan": meal_plan}


