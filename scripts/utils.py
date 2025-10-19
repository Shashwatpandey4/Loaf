from src.models.contracts import Recipe
from src.database.connection import get_connection

def insert_recipe_to_db(recipe: Recipe) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO recipes
      (id, name, description, cuisine_type, difficulty, prep_time, cook_time, servings, spice_level)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        recipe.id,
        recipe.name,
        recipe.description,
        recipe.cuisine_type,
        recipe.difficulty,
        recipe.prep_time,
        recipe.cook_time,
        recipe.servings,
        recipe.spice_level,
    ))
    # Remove existing children rows for safety
    cur.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe.id,))
    cur.execute("DELETE FROM instructions WHERE recipe_id = ?", (recipe.id,))

    # Insert ingredients
    for ing in recipe.ingredients:
        cur.execute("""
        INSERT INTO ingredients (recipe_id, name, amount, unit)
        VALUES (?, ?, ?, ?)
        """, (recipe.id, ing.name, ing.amount, ing.unit))

    # Insert instructions (preserve order)
    for i, step in enumerate(recipe.instructions):
        cur.execute("""
        INSERT INTO instructions (recipe_id, step_index, text)
        VALUES (?, ?, ?)
        """, (recipe.id, i, step))


    conn.commit()
    conn.close()