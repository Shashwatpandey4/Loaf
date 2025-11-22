import sqlite3
from loguru import logger
from dotenv import load_dotenv
import os

load_dotenv()

DB_FILE="./knowledge.db"

def get_connection(path: str = DB_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn
