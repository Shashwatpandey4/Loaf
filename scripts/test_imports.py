# scripts/test_imports.py
"""Quick test to verify all imports work correctly."""
import os
import sys

# Add parent directory to path for direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

print("Testing imports...")

try:
    print("1. Testing recipe_scraper imports...")
    from scripts.recipe_scraper import recipe_exists_in_db, scrape_and_insert_recipe
    print("   ✅ recipe_scraper imports successful")
except Exception as e:
    print(f"   ❌ recipe_scraper import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("2. Testing meal_plan_utils imports...")
    from scripts.meal_plan_utils import check_meal_plan_recipes, scrape_unavailable_recipes, save_meal_plan_to_file
    print("   ✅ meal_plan_utils imports successful")
except Exception as e:
    print(f"   ❌ meal_plan_utils import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("3. Testing meal_plan_tools imports...")
    from scripts.meal_plan_tools import MealPlanTools
    print("   ✅ meal_plan_tools imports successful")
except Exception as e:
    print(f"   ❌ meal_plan_tools import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("4. Testing test_meal_plan imports...")
    from scripts.test_meal_plan import test_mock_meal_plan, test_single_recipe_check
    print("   ✅ test_meal_plan imports successful")
except Exception as e:
    print(f"   ❌ test_meal_plan import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All import tests complete!")

