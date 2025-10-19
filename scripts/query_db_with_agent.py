# Executable: run your agent query
from dotenv import load_dotenv
from sqlalchemy import create_engine
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools

load_dotenv()

def main():
    engine = create_engine('sqlite:///knowledge.db')
    
    agent = Agent(
        name="Recipe Agent",
        model=OpenAIChat(id="gpt-5-nano"),
        system_message="You are equipped with tools to manage sqlite database",
        tools=[SQLTools(db_engine=engine)],
        markdown=True,
        retries=3
    )
    
    agent.print_response(
        "Give me any name (only name) of any recipe that has more than 3 table spoons of brown sugar",
        stream=True
    )

if __name__ == "__main__":
    main()