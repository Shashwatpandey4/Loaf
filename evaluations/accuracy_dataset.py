"""
Accuracy evaluation dataset with ground truth recipe IDs.
Each query has a known correct recipe answer based on actual recipes in the KB.
"""

from typing import List
from dataclasses import dataclass


@dataclass
class AccuracyTestQuery:
    """Test query with ground truth correct recipe."""
    
    query: str
    correct_recipe_id: str  # The ID of the correct recipe
    correct_recipe_name: str  # Name for verification
    category: str = ""  # Category for analysis


# Ground truth dataset - queries with known correct answers from actual KB recipes
ACCURACY_TEST_QUERIES: List[AccuracyTestQuery] = [
    # Simple direct name matches
    AccuracyTestQuery(
        query="I want to make pad thai",
        correct_recipe_id="003",
        correct_recipe_name="Spicy Pad Thai",
        category="simple"
    ),
    AccuracyTestQuery(
        query="How do I cook miso ramen?",
        correct_recipe_id="002",
        correct_recipe_name="Miso Ramen",
        category="simple"
    ),
    AccuracyTestQuery(
        query="Recipe for spicy Sichuan noodles",
        correct_recipe_id="001",
        correct_recipe_name="Spicy Sichuan Noodles",
        category="simple"
    ),
    AccuracyTestQuery(
        query="I want creamy mushroom pasta",
        correct_recipe_id="004",
        correct_recipe_name="Creamy Mushroom Pasta",
        category="simple"
    ),
    
    # Cuisine-specific queries
    AccuracyTestQuery(
        query="I want Chinese food",
        correct_recipe_id="001",  # Spicy Sichuan Noodles is Chinese
        correct_recipe_name="Spicy Sichuan Noodles",
        category="cuisine"
    ),
    AccuracyTestQuery(
        query="Show me a Thai dish",
        correct_recipe_id="003",  # Pad Thai
        correct_recipe_name="Spicy Pad Thai",
        category="cuisine"
    ),
    AccuracyTestQuery(
        query="I want Italian pasta",
        correct_recipe_id="004",  # Creamy Mushroom Pasta
        correct_recipe_name="Creamy Mushroom Pasta",
        category="cuisine"
    ),
    AccuracyTestQuery(
        query="Japanese ramen recipe",
        correct_recipe_id="002",  # Miso Ramen
        correct_recipe_name="Miso Ramen",
        category="cuisine"
    ),
    
    # Spice level queries
    AccuracyTestQuery(
        query="Hot and spicy noodles",
        correct_recipe_id="001",  # Spicy Sichuan Noodles (extra-hot)
        correct_recipe_name="Spicy Sichuan Noodles",
        category="spice"
    ),
    AccuracyTestQuery(
        query="Mild Japanese noodles",
        correct_recipe_id="002",  # Miso Ramen (mild)
        correct_recipe_name="Miso Ramen",
        category="spice"
    ),
    AccuracyTestQuery(
        query="Spicy Thai curry",
        correct_recipe_id="005",  # Spicy Thai Green Curry (hot)
        correct_recipe_name="Spicy Thai Green Curry",
        category="spice"
    ),
    
    # Difficulty queries
    AccuracyTestQuery(
        query="Easy beginner recipe",
        correct_recipe_id="014",  # Easy Chewy M&M Cookies
        correct_recipe_name="Easy Chewy M&M Cookies",
        category="difficulty"
    ),
    AccuracyTestQuery(
        query="Easy Japanese recipe",
        correct_recipe_id="002",  # Miso Ramen (easy)
        correct_recipe_name="Miso Ramen",
        category="difficulty"
    ),
    
    # Multi-criteria queries (harder - tests query understanding)
    AccuracyTestQuery(
        query="Easy vegetarian Italian pasta dish",
        correct_recipe_id="004",  # Creamy Mushroom Pasta (easy, Italian, pasta)
        correct_recipe_name="Creamy Mushroom Pasta",
        category="multi_criteria"
    ),
    AccuracyTestQuery(
        query="Mild Japanese noodles for beginners",
        correct_recipe_id="002",  # Miso Ramen (mild, Japanese, easy)
        correct_recipe_name="Miso Ramen",
        category="multi_criteria"
    ),
    AccuracyTestQuery(
        query="Spicy Thai dish that's not too hard",
        correct_recipe_id="003",  # Pad Thai (spicy, Thai, medium difficulty)
        correct_recipe_name="Spicy Pad Thai",
        category="multi_criteria"
    ),
    AccuracyTestQuery(
        query="Chinese spicy noodles",
        correct_recipe_id="001",  # Spicy Sichuan Noodles (Chinese, spicy, noodles)
        correct_recipe_name="Spicy Sichuan Noodles",
        category="multi_criteria"
    ),
    
    # Ingredient-based queries
    AccuracyTestQuery(
        query="Recipe with mushrooms and pasta",
        correct_recipe_id="004",  # Creamy Mushroom Pasta
        correct_recipe_name="Creamy Mushroom Pasta",
        category="ingredients"
    ),
    AccuracyTestQuery(
        query="Dish with miso and ramen noodles",
        correct_recipe_id="002",  # Miso Ramen
        correct_recipe_name="Miso Ramen",
        category="ingredients"
    ),
    
    # Vague queries (hardest - tests system's best guess)
    AccuracyTestQuery(
        query="Something with noodles",
        correct_recipe_id="002",  # Miso Ramen (most common/accessible)
        correct_recipe_name="Miso Ramen",
        category="vague"
    ),
    AccuracyTestQuery(
        query="I want pasta",
        correct_recipe_id="004",  # Creamy Mushroom Pasta
        correct_recipe_name="Creamy Mushroom Pasta",
        category="vague"
    ),
]


def get_accuracy_test_queries() -> List[AccuracyTestQuery]:
    """Get all accuracy test queries."""
    return ACCURACY_TEST_QUERIES


def get_queries_by_category(category: str) -> List[AccuracyTestQuery]:
    """Get queries filtered by category."""
    return [q for q in ACCURACY_TEST_QUERIES if q.category == category]
