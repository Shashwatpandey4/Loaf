import os
from loguru import logger

from scripts.utils import insert_recipe_to_db
from src.database.connection import DB_FILE, get_connection
from src.database.schema import create_schema

def create_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        logger.info(f"Database file {DB_FILE} removed")
        
    conn = get_connection()
    create_schema(conn)
    conn.close()
    logger.info(f"Database file {DB_FILE} created")
    
if __name__ == "__main__":
    create_database()
        
        