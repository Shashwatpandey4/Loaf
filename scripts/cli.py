#!/usr/bin/env python3
"""
Enhanced CLI interface for the food KB answerer with web search.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.fullstack_kb_answerer import FullStackKBAnswerer


def main():
    """Main CLI function."""
    kb = FullStackKBAnswerer()

    print("🍜 Food KB Answerer")
    print("=" * 30)
    print("Enter food queries (type 'quit' to exit, 'help' for commands)")
    print()

    while True:
        try:
            query = input("Query: ").strip()

            if query.lower() in ["quit", "exit", "q"]:
                print("Goodbye! 👋")
                break

            if query.lower() == "help":
                print("\nCommands:")
                print("  help     - Show this help")
                print("  list     - Show all available recipes")
                print("  kb-only  - Search only knowledge base (default)")
                print("  web      - Enable web search for next query")
                print("  quit     - Exit the program")
                print("  <query>  - Ask about food/recipes")
                print()
                continue

            if query.lower() == "list":
                recipes = kb.get_available_recipes()
                print(f"\n📚 Available Recipes ({len(recipes)}):")
                for recipe in recipes:
                    print(
                        f"  • {recipe.name} ({recipe.cuisine_type}, {recipe.spice_level}, {recipe.difficulty})"
                    )
                print()
                continue

            if query.lower() == "kb-only":
                print("🔍 KB-only mode enabled for next query")
                print()
                continue

            if query.lower() == "web":
                print("🌐 Web search enabled for next query")
                print()
                continue

            if not query:
                continue

            # Determine search mode (default to KB-only for simplicity)
            include_web_search = query.lower() == "web"
            kb_only_mode = query.lower() == "kb-only"

            if kb_only_mode:
                query = input("Query: ").strip()
                if not query:
                    continue

            # Process the query
            response = kb.answer_query(query, include_web_search=include_web_search)

            print(f"\n🎯 Query: '{query}'")
            print(
                f"Confidence: {response.confidence.value} ({response.confidence_score:.2f})"
            )
            print(f"Needs Web: {'Yes' if response.needs_web else 'No'}")
            print(f"Reasoning: {response.reasoning}")

            # Display KB results
            if response.recipe:
                recipe = response.recipe
                print(f"\n📖 KB Recipe: {recipe.name}")
                print(f"   Cuisine: {recipe.cuisine_type}")
                print(f"   Difficulty: {recipe.difficulty}")
                print(f"   Spice Level: {recipe.spice_level}")
                print(f"   Time: {recipe.prep_time} + {recipe.cook_time}")
                print(f"   Servings: {recipe.servings}")
                print(f"   Description: {recipe.description}")

                print("\n🥘 Ingredients:")
                for ingredient in recipe.ingredients:
                    print(
                        f"   • {ingredient.amount} {ingredient.unit or ''} {ingredient.name}"
                    )

                print("\n👨‍🍳 Instructions:")
                for i, instruction in enumerate(recipe.instructions, 1):
                    print(f"   {i}. {instruction}")

                print(f"\n🏷️  Tags: {', '.join(recipe.tags)}")
            else:
                print("\n❌ No matching recipe found in knowledge base")

            # Display web search results
            if response.web_search_results:
                web_results = response.web_search_results
                print(
                    f"\n🔍 Web Search Results ({web_results.total_results} found, {web_results.search_time_ms}ms):"
                )

                for i, result in enumerate(web_results.search_results, 1):
                    print(f"\n{i}. {result.title}")
                    print(f"   URL: {result.url}")
                    print(f"   Domain: {result.domain}")
                    print(f"   Snippet: {result.snippet[:100]}...")
            else:
                if response.needs_web:
                    print("\n💡 Consider searching the web for more options")

            print("\n" + "-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()


if __name__ == "__main__":
    main()
