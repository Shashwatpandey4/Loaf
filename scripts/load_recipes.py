from loguru import logger
from knowledge.recipes import RECIPES
from scripts.utils import insert_recipe_to_db

def main():
    for r in RECIPES:
        insert_recipe_to_db(r)
    logger.info(f"Loaded {len(RECIPES)} recipes into the database")
    
if __name__ == "__main__":
    main()