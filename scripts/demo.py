# scripts/demo.py
import sys
import runpy
from dotenv import load_dotenv
from sqlalchemy import create_engine
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools

load_dotenv()

MODULES = [
    "scripts.create_database",
    "scripts.load_recipes",
    "scripts.add_persona",
]

def run_all():
    for mod in MODULES:
        print(f"\n=== Running {mod} ===")
        runpy.run_module(mod, run_name="__main__")

def query_db(prompt: str):
    engine = create_engine('sqlite:///knowledge.db')
    
    agent = Agent(
        name="Recipe Agent",
        model=OpenAIChat(id="gpt-5-nano"),
        system_message="You are equipped with tools to manage sqlite database",
        tools=[SQLTools(db_engine=engine)],
        markdown=True,
        retries=3
    )
    
    print(f"\n=== Querying database with prompt ===")
    print(f"Prompt: {prompt}\n")
    agent.print_response(prompt, stream=True)

if __name__ == "__main__":
    # First, run all setup steps
    run_all()
    
    # Then check if a prompt was provided as argument
    if len(sys.argv) > 1:
        # Join all arguments after script name as the prompt
        prompt = " ".join(sys.argv[1:])
        query_db(prompt)
    else:
        print("\n=== Setup complete ===")
        print("To query the database, run:")
        print('python -m scripts.demo "Your query here"')
        print("\nExample:")
        print('python -m scripts.demo "Give me any recipe with brown sugar"')