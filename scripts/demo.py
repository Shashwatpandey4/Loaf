# scripts/demo.py
import sys
import runpy
from dotenv import load_dotenv
from sqlalchemy import create_engine
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools
from knowledge.prompt import SYSTEM_PROMPT
from scripts.test_meal_plan import test_mock_meal_plan
from loguru import logger

load_dotenv()

MODULES = [
    "scripts.create_database",
    "scripts.load_recipes",
    "scripts.add_persona",
    # "run_weekly_meal_workflow",
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
        system_message=SYSTEM_PROMPT,
        tools=[SQLTools(db_engine=engine)],
        markdown=True,
        retries=3
    )
    
    print(f"\n=== Querying database with prompt ===")
    print(f"Prompt: {prompt}\n")
    agent.print_response(prompt, stream=True)

def chat_loop():
    """Interactive chat loop that queries the database without maintaining history."""
    engine = create_engine('sqlite:///knowledge.db')
    
    # Create agent once for the session
    agent = Agent(
        name="Recipe Agent",
        model=OpenAIChat(id="gpt-5-nano"),
        system_message=SYSTEM_PROMPT,
        tools=[SQLTools(db_engine=engine)],
        markdown=True,
        retries=3
    )
    
    print("\n" + "="*50)
    print("Recipe Database Chat")
    print("="*50)
    print("Ask questions about the database.")
    print("Type 'exit', 'quit', or 'q' to end.\n")
    
    count = 0
    
    while count<1:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Query the database (no history maintained)
            print()  # Add spacing
            # agent.print_response(user_input, stream=False, show_full_reasoning=False)
            response = agent.run(
                user_input,
                stream=False,
                show_full_reasoning=False,
            )
            answer_text = response.content  # identical string that print_response would show
            # print(answer_text)
            # Tharanath's code is from here
            logger.info("Processing meal plan from agent response...")
            test_mock_meal_plan(mock_meal_plan=answer_text)

            print()  # Add spacing after response
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            continue
        count += 1

if __name__ == "__main__":
    # Check if --skip-setup flag is provided
    skip_setup = "--skip-setup" in sys.argv
    
    if not skip_setup:
        # First, run all setup steps
        run_all()
    else:
        print("\n=== Skipping setup (using existing database) ===")
    
    # Start interactive chat
    chat_loop()
    runpy.run_module("run_weekly_meal_workflow", run_name="__main__")