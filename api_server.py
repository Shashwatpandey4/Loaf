"""
FastAPI server to connect the UI with the demo.py functionality.
This wraps the chatbot functionality without modifying demo.py.
"""

import ast
import json

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import create_engine

from knowledge.prompt import SYSTEM_PROMPT
from scripts.test_meal_plan import test_mock_meal_plan

load_dotenv()

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance (created on first request)
_agent = None
_engine = None


def get_agent():
    """Get or create the agent instance."""
    global _agent, _engine
    if _agent is None:
        _engine = create_engine("sqlite:///knowledge.db")
        _agent = Agent(
            name="Recipe Agent",
            model=OpenAIChat(id="gpt-5-nano"),
            system_message=SYSTEM_PROMPT,
            tools=[SQLTools(db_engine=_engine)],
            markdown=True,
            retries=3,
        )
    return _agent


class ChatRequest(BaseModel):
    message: str
    run_workflow: bool = False  # Whether to run the full workflow after meal plan


class ChatResponse(BaseModel):
    meal_plan: dict
    message: str
    success: bool
    raw_response: str = ""  # The full agent response


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Loaf API Server is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a user message and return a meal plan.
    This wraps the functionality from scripts/demo.py chat_loop().
    """
    try:
        user_input = request.message.strip()

        if not user_input:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Get the agent
        agent = get_agent()

        # Query the database (same as in demo.py)
        logger.info(f"Processing user query: {user_input}")
        response = agent.run(
            user_input,
            stream=False,
            show_full_reasoning=False,
        )
        answer_text = response.content

        # Parse the meal plan JSON from the response
        meal_plan = None
        try:
            # First try json.loads (handles proper JSON)
            meal_plan = json.loads(answer_text)
        except (json.JSONDecodeError, ValueError):
            try:
                # Try ast.literal_eval (handles Python dict format)
                meal_plan = ast.literal_eval(answer_text)
            except (ValueError, SyntaxError):
                # If parsing fails, try to extract JSON from the response
                logger.warning(
                    "Failed to parse meal plan directly, trying to extract JSON..."
                )
                import re

                json_match = re.search(r"\{.*\}", answer_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    try:
                        meal_plan = json.loads(json_str)
                    except json.JSONDecodeError:
                        try:
                            meal_plan = ast.literal_eval(json_str)
                        except (ValueError, SyntaxError):
                            raise HTTPException(
                                status_code=500,
                                detail="Could not parse meal plan from response",
                            )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Could not find JSON in response: {answer_text[:200]}",
                    )

        # Process the meal plan (same as in demo.py)
        logger.info("Processing meal plan from agent response...")
        test_mock_meal_plan(mock_meal_plan=answer_text)

        # Optionally run the full workflow
        if request.run_workflow:
            logger.info("Running full weekly meal workflow...")
            import runpy

            runpy.run_module("run_weekly_meal_workflow", run_name="__main__")

        return ChatResponse(
            meal_plan=meal_plan,
            message="Meal plan created successfully!",
            success=True,
            raw_response=answer_text,  # Include the full agent response
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/test")
def test():
    """Test endpoint to verify the API is working."""
    return {
        "status": "ok",
        "message": "API is working! The chatbot is ready.",
        "agent_initialized": _agent is not None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
