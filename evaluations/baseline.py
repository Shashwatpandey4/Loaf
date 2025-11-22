"""
Baseline recipe answerer system for comparison.
Uses simple keyword matching without advanced features.
"""

from typing import List, Optional
from src.models.contracts import (
    ConfidenceLevel,
    EnhancedKBResponse,
    QueryAnalysis,
    Recipe,
    WebSearchResponse,
)
from knowledge.recipes import get_all_recipes


class BaselineAnswerer:
    """Simple baseline system using basic keyword matching."""

    def __init__(self):
        self.recipes = get_all_recipes()

    def answer_query(
        self, query: str, include_web_search: bool = False, extract_recipes: bool = False
    ) -> EnhancedKBResponse:
        """Answer query using simple keyword matching."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        best_recipe = None
        best_score = 0.0
        matched_tags = []

        # Simple keyword matching
        for recipe in self.recipes:
            score = 0.0
            tags = []

            # Check recipe name
            recipe_name_lower = recipe.name.lower()
            for word in query_words:
                if word in recipe_name_lower:
                    score += 0.3
                    tags.append(f"name:{word}")

            # Check tags
            for tag in recipe.tags:
                tag_lower = tag.lower()
                for word in query_words:
                    if word in tag_lower:
                        score += 0.2
                        tags.append(f"tag:{tag}")

            # Check ingredients
            for ingredient in recipe.ingredients:
                ing_name_lower = ingredient.name.lower()
                for word in query_words:
                    if word in ing_name_lower:
                        score += 0.1
                        tags.append(f"ingredient:{ingredient.name}")

            if score > best_score:
                best_score = score
                best_recipe = recipe
                matched_tags = tags

        # Simple confidence calculation
        if best_score >= 0.5:
            confidence_level = ConfidenceLevel.HIGH
            confidence_score = min(best_score, 1.0)
            reasoning = f"Found match with score {confidence_score:.2f}"
        elif best_score >= 0.2:
            confidence_level = ConfidenceLevel.MEDIUM
            confidence_score = best_score
            reasoning = f"Found partial match with score {confidence_score:.2f}"
        else:
            confidence_level = ConfidenceLevel.LOW
            confidence_score = best_score
            reasoning = f"Low confidence match with score {confidence_score:.2f}"

        return EnhancedKBResponse(
            query=query,
            recipe=best_recipe,
            confidence=confidence_level,
            confidence_score=confidence_score,
            matched_tags=list(set(matched_tags)),
            reasoning=reasoning,
            needs_web=confidence_level != ConfidenceLevel.HIGH,
            web_search_results=None,  # Baseline doesn't use web search
        )

    def get_available_recipes(self) -> List[Recipe]:
        """Get all available recipes."""
        return self.recipes

