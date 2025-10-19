# scripts/test.py
import runpy

MODULES = [
    "scripts.create_database",
    "scripts.load_recipes",
    "scripts.query_db_with_agent",
]

def run_all():
    for mod in MODULES:
        print(f"\n=== Running {mod} ===")
        runpy.run_module(mod, run_name="__main__")

if __name__ == "__main__":
    run_all()
