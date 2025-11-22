#!/usr/bin/env python3
"""
Interactive Chat CLI for Food KB Answerer.
Provides a conversational interface to chat with the recipe model.
"""

import os
import sys

# Add project root to path for all modules
sys.path.insert(0, os.path.dirname(__file__))

import time

from src.fullstack_kb_answerer import FullStackKBAnswerer


class RecipeChatBot:
    """Interactive chat bot for recipe queries."""

    def __init__(self):
        self.kb = FullStackKBAnswerer()
        self.conversation_history = []
        self.session_start_time = time.time()

    def print_welcome(self):
        """Print welcome message and instructions."""
        print("Welcome to Recipe Chat Bot!")
        print("=" * 50)
        print("I can help you find recipes, cooking tips, and food suggestions.")
        print("Just ask me anything about food and cooking!")
        print()
        print("Commands:")
        print("  /help     - Show this help message")
        print("  /recipes  - Show available recipes")
        print("  /stats    - Show session statistics")
        print("  /clear    - Clear conversation history")
        print("  /quit     - Exit the chat")
        print()
        print("Examples:")
        print("  'I want spicy noodles'")
        print("  'Korean kimchi recipe'")
        print("  'Easy pasta dish'")
        print("  'What can I make with chicken?'")
        print()

    def print_help(self):
        """Print help information."""
        print("\nHelp - Recipe Chat Bot")
        print("-" * 30)
        print("Ask me about:")
        print("• Specific recipes (e.g., 'spicy noodles')")
        print("• Cuisine types (e.g., 'Italian food')")
        print("• Cooking methods (e.g., 'easy recipes')")
        print("• Ingredients (e.g., 'chicken recipes')")
        print("• Dietary preferences (e.g., 'vegetarian pasta')")
        print()
        print("I'll search my knowledge base first, then the web if needed!")
        print()

    def show_available_recipes(self):
        """Show all available recipes in the knowledge base."""
        recipes = self.kb.get_available_recipes()
        print(f"\nAvailable Recipes ({len(recipes)} total)")
        print("-" * 40)

        for i, recipe in enumerate(recipes, 1):
            print(f"{i}. {recipe.name}")
            print(f"   Cuisine: {recipe.cuisine_type}")
            print(f"   Difficulty: {recipe.difficulty}")
            print(f"   Spice Level: {recipe.spice_level}")
            print(f"   Time: {recipe.prep_time} + {recipe.prep_time}")
            print(f"   Servings: {recipe.servings}")
            print()

    def show_session_stats(self):
        """Show session statistics."""
        session_time = time.time() - self.session_start_time
        print("\nSession Statistics")
        print("-" * 25)
        print(f"Session Duration: {session_time:.1f} seconds")
        print(f"Queries Asked: {len(self.conversation_history)}")
        print(f"Available Recipes: {len(self.kb.get_available_recipes())}")
        print()

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        print("Conversation history cleared!")
        print()

    def format_recipe_response(self, response) -> str:
        """Format recipe response for display."""
        output = []

        # Basic info
        if response.recipe:
            recipe = response.recipe
            output.append(f"**{recipe.name}**")
            output.append(f"   Cuisine: {recipe.cuisine_type}")
            output.append(f"   Difficulty: {recipe.difficulty}")
            output.append(f"   Spice Level: {recipe.spice_level}")
            output.append(f"   Time: {recipe.prep_time} + {recipe.cook_time}")
            output.append(f"   Servings: {recipe.servings}")
            output.append("")

            # Ingredients
            if recipe.ingredients:
                output.append("**Ingredients:**")
                for ingredient in recipe.ingredients[:8]:  # Show first 8
                    amount_str = (
                        f"{ingredient.amount} {ingredient.unit}"
                        if ingredient.amount and ingredient.unit
                        else ingredient.amount or ""
                    )
                    output.append(f"   • {amount_str} {ingredient.name}".strip())
                if len(recipe.ingredients) > 8:
                    output.append(
                        f"   ... and {len(recipe.ingredients) - 8} more ingredients"
                    )
                output.append("")

            # Instructions
            if recipe.instructions:
                output.append("**Instructions:**")
                for i, instruction in enumerate(
                    recipe.instructions[:5], 1
                ):  # Show first 5
                    output.append(f"   {i}. {instruction}")
                if len(recipe.instructions) > 5:
                    output.append(
                        f"   ... and {len(recipe.instructions) - 5} more steps"
                    )
                output.append("")

        # Web search results
        if response.web_search_results:
            web_results = response.web_search_results
            output.append(
                f"**Web Search Results** ({web_results.total_results} found):"
            )
            for i, result in enumerate(web_results.search_results[:3], 1):
                output.append(f"   {i}. {result.title}")
                output.append(f"      {result.url}")
                output.append(f"      {result.snippet[:80]}...")
            output.append("")

        # Confidence and reasoning
        output.append(
            f"**Confidence:** {response.confidence.value} ({response.confidence_score:.2f})"
        )
        output.append(f"**Reasoning:** {response.reasoning}")

        return "\n".join(output)

    def process_query(self, query: str) -> str:
        """Process a user query and return formatted response."""
        try:
            start_time = time.time()

            # Get response from KB answerer
            response = self.kb.answer_query(
                query,
                include_web_search=True,
                extract_recipes=False,  # Skip extraction for faster responses
            )

            processing_time = time.time() - start_time

            # Format response
            formatted_response = self.format_recipe_response(response)

            # Add processing time
            formatted_response += f"\nProcessed in {processing_time:.2f}s"

            # Store in history
            self.conversation_history.append(
                {
                    "query": query,
                    "response": response,
                    "timestamp": time.time(),
                    "processing_time": processing_time,
                }
            )

            return formatted_response

        except Exception as e:
            return f"Error processing query: {str(e)}"

    def run(self):
        """Run the interactive chat session."""
        self.print_welcome()

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    command = user_input.lower()

                    if command == "/help":
                        self.print_help()
                    elif command == "/recipes":
                        self.show_available_recipes()
                    elif command == "/stats":
                        self.show_session_stats()
                    elif command == "/clear":
                        self.clear_history()
                    elif command in ["/quit", "/exit", "/q"]:
                        print("Thanks for chatting! Goodbye!")
                        break
                    else:
                        print("Unknown command. Type /help for available commands.")
                    continue

                # Process regular query
                print("\nBot:")
                response = self.process_query(user_input)
                print(response)
                print()

            except KeyboardInterrupt:
                print("\n\nThanks for chatting! Goodbye!")
                break
            except EOFError:
                print("\n\nThanks for chatting! Goodbye!")
                break


def main():
    """Main function to start the chat bot."""
    try:
        bot = RecipeChatBot()
        bot.run()
    except Exception as e:
        print(f"Failed to start chat bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
