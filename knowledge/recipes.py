"""
Minimal knowledge base with sample recipes for the food KB answerer.
"""

from src.models.contracts import Ingredient, Recipe

# Sample recipes for the knowledge base
RECIPES = [
    Recipe(
        id="spicy_noodles_001",
        name="Spicy Sichuan Noodles",
        description="Traditional Sichuan-style spicy noodles with numbing heat",
        cuisine_type="Chinese",
        difficulty="medium",
        prep_time="15 minutes",
        cook_time="10 minutes",
        servings=2,
        ingredients=[
            Ingredient(name="fresh noodles", amount="200", unit="g"),
            Ingredient(name="Sichuan peppercorns", amount="1", unit="tsp"),
            Ingredient(name="chili oil", amount="2", unit="tbsp"),
            Ingredient(name="garlic", amount="3", unit="cloves"),
            Ingredient(name="ginger", amount="1", unit="inch"),
            Ingredient(name="soy sauce", amount="2", unit="tbsp"),
            Ingredient(name="rice vinegar", amount="1", unit="tbsp"),
            Ingredient(name="scallions", amount="2", unit="stalks"),
            Ingredient(name="sesame oil", amount="1", unit="tsp"),
        ],
        instructions=[
            "Boil noodles according to package instructions until al dente",
            "Toast Sichuan peppercorns in a dry pan until fragrant",
            "Grind peppercorns to a fine powder",
            "Mince garlic and ginger",
            "Heat chili oil in a wok or large pan",
            "Add garlic and ginger, stir-fry for 30 seconds",
            "Add soy sauce and rice vinegar",
            "Drain noodles and add to the pan",
            "Toss noodles with the sauce",
            "Garnish with scallions and sesame oil",
            "Sprinkle with ground Sichuan peppercorns",
        ],
        tags=["spicy", "noodles", "sichuan", "chinese", "hot", "numbing"],
        spice_level="extra-hot",
    ),
    Recipe(
        id="mild_ramen_002",
        name="Miso Ramen",
        description="Comforting Japanese miso ramen with soft-boiled egg",
        cuisine_type="Japanese",
        difficulty="easy",
        prep_time="20 minutes",
        cook_time="15 minutes",
        servings=2,
        ingredients=[
            Ingredient(name="ramen noodles", amount="2", unit="packages"),
            Ingredient(name="miso paste", amount="3", unit="tbsp"),
            Ingredient(name="chicken broth", amount="4", unit="cups"),
            Ingredient(name="soft-boiled eggs", amount="2", unit="pieces"),
            Ingredient(name="nori sheets", amount="2", unit="sheets"),
            Ingredient(name="scallions", amount="2", unit="stalks"),
            Ingredient(name="corn kernels", amount="1/2", unit="cup"),
            Ingredient(name="butter", amount="1", unit="tbsp"),
        ],
        instructions=[
            "Boil eggs for 6 minutes, then cool in ice water",
            "Heat chicken broth in a pot",
            "Whisk in miso paste until dissolved",
            "Cook ramen noodles separately",
            "Add butter to the broth",
            "Place noodles in bowls",
            "Pour hot broth over noodles",
            "Top with halved soft-boiled eggs",
            "Add corn kernels and sliced scallions",
            "Garnish with nori sheets",
        ],
        tags=["ramen", "miso", "japanese", "comfort", "mild", "noodles"],
        spice_level="mild",
    ),
    Recipe(
        id="spicy_pad_thai_003",
        name="Spicy Pad Thai",
        description="Thai stir-fried noodles with a spicy kick",
        cuisine_type="Thai",
        difficulty="medium",
        prep_time="25 minutes",
        cook_time="10 minutes",
        servings=2,
        ingredients=[
            Ingredient(name="rice noodles", amount="200", unit="g"),
            Ingredient(name="shrimp", amount="150", unit="g"),
            Ingredient(name="eggs", amount="2", unit="pieces"),
            Ingredient(name="bean sprouts", amount="1", unit="cup"),
            Ingredient(name="garlic", amount="3", unit="cloves"),
            Ingredient(name="fish sauce", amount="3", unit="tbsp"),
            Ingredient(name="tamarind paste", amount="2", unit="tbsp"),
            Ingredient(name="brown sugar", amount="2", unit="tbsp"),
            Ingredient(name="chili flakes", amount="1", unit="tsp"),
            Ingredient(name="peanuts", amount="1/4", unit="cup"),
            Ingredient(name="lime", amount="1", unit="piece"),
        ],
        instructions=[
            "Soak rice noodles in warm water for 15 minutes",
            "Mix fish sauce, tamarind paste, brown sugar, and chili flakes for sauce",
            "Heat oil in a wok or large pan",
            "Add minced garlic and stir-fry for 30 seconds",
            "Add shrimp and cook until pink",
            "Push shrimp to one side, add beaten eggs",
            "Scramble eggs, then mix with shrimp",
            "Add drained noodles and sauce",
            "Toss everything together",
            "Add bean sprouts and peanuts",
            "Serve with lime wedges",
        ],
        tags=["pad thai", "thai", "spicy", "noodles", "stir-fry", "hot"],
        spice_level="hot",
    ),
    Recipe(
        id="mild_pasta_004",
        name="Creamy Mushroom Pasta",
        description="Rich and creamy pasta with wild mushrooms",
        cuisine_type="Italian",
        difficulty="easy",
        prep_time="10 minutes",
        cook_time="20 minutes",
        servings=2,
        ingredients=[
            Ingredient(name="pasta", amount="250", unit="g"),
            Ingredient(name="mixed mushrooms", amount="300", unit="g"),
            Ingredient(name="heavy cream", amount="1", unit="cup"),
            Ingredient(name="parmesan cheese", amount="1/2", unit="cup"),
            Ingredient(name="garlic", amount="2", unit="cloves"),
            Ingredient(name="butter", amount="2", unit="tbsp"),
            Ingredient(name="fresh thyme", amount="1", unit="tbsp"),
            Ingredient(name="salt", amount="to taste", unit=""),
            Ingredient(name="black pepper", amount="to taste", unit=""),
        ],
        instructions=[
            "Cook pasta according to package instructions",
            "Heat butter in a large pan",
            "Add sliced mushrooms and cook until golden",
            "Add minced garlic and thyme",
            "Pour in heavy cream",
            "Simmer until cream thickens",
            "Add grated parmesan cheese",
            "Season with salt and pepper",
            "Toss cooked pasta with mushroom sauce",
            "Serve immediately",
        ],
        tags=["pasta", "mushroom", "creamy", "italian", "mild", "comfort"],
        spice_level="mild",
    ),
    Recipe(
        id="spicy_curry_005",
        name="Spicy Thai Green Curry",
        description="Aromatic Thai green curry with vegetables and coconut milk",
        cuisine_type="Thai",
        difficulty="medium",
        prep_time="15 minutes",
        cook_time="25 minutes",
        servings=3,
        ingredients=[
            Ingredient(name="green curry paste", amount="3", unit="tbsp"),
            Ingredient(name="coconut milk", amount="400", unit="ml"),
            Ingredient(name="mixed vegetables", amount="300", unit="g"),
            Ingredient(name="chicken breast", amount="200", unit="g"),
            Ingredient(name="fish sauce", amount="2", unit="tbsp"),
            Ingredient(name="brown sugar", amount="5", unit="tbsp"),
            Ingredient(name="kaffir lime leaves", amount="4", unit="leaves"),
            Ingredient(name="thai basil", amount="1/4", unit="cup"),
            Ingredient(name="jasmine rice", amount="1", unit="cup"),
        ],
        instructions=[
            "Cook jasmine rice according to package instructions",
            "Cut chicken into bite-sized pieces",
            "Heat half the coconut milk in a pot",
            "Add green curry paste and cook until fragrant",
            "Add chicken and cook until opaque",
            "Add remaining coconut milk",
            "Add mixed vegetables",
            "Season with fish sauce and brown sugar",
            "Add kaffir lime leaves",
            "Simmer for 15 minutes",
            "Garnish with Thai basil",
            "Serve over jasmine rice",
        ],
        tags=["curry", "thai", "spicy", "green", "coconut", "hot"],
        spice_level="hot",
    ),
]


def get_all_recipes() -> list[Recipe]:
    """Get all recipes from the knowledge base."""
    return RECIPES


def get_recipe_by_id(recipe_id: str) -> Recipe | None:
    """Get a specific recipe by ID."""
    for recipe in RECIPES:
        if recipe.id == recipe_id:
            return recipe
    return None


def search_recipes_by_tags(tags: list[str]) -> list[Recipe]:
    """Search recipes by tags."""
    matching_recipes = []
    for recipe in RECIPES:
        if any(tag.lower() in [t.lower() for t in recipe.tags] for tag in tags):
            matching_recipes.append(recipe)
    return matching_recipes
