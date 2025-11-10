import sqlite3
from loguru import logger

def create_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    
    # Recipes table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        cuisine_type TEXT,
        difficulty TEXT,
        prep_time TEXT,
        cook_time TEXT,
        servings INTEGER,
        spice_level TEXT
    )
    """)
    # Ingredients table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id TEXT,
        name TEXT,
        amount TEXT,
        unit TEXT,
        FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
    )
    """)
    # Instructions table (ordered)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS instructions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id TEXT,
        step_index INTEGER,
        text TEXT,
        FOREIGN KEY(recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
    )
    """)
    
    # Personas table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS persona (
        id TEXT PRIMARY KEY,
        name TEXT,
        medical_condition TEXT,
        dietary_restrictions TEXT
    )
                """)
    conn.commit()
    logger.info("Schema created successfully")