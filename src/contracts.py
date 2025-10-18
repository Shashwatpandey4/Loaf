"""
Contract definitions for the food KB answerer system.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    """Confidence levels for recipe matching."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEEDS_WEB = "needs_web"


class Ingredient(BaseModel):
    """Individual ingredient in a recipe."""

    name: str = Field(..., description="Name of the ingredient")
    amount: str = Field(..., description="Amount/quantity of the ingredient")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class Recipe(BaseModel):
    """Structured recipe from knowledge base."""

    id: str = Field(..., description="Unique recipe identifier")
    name: str = Field(..., description="Name of the recipe")
    description: str = Field(..., description="Brief description of the recipe")
    cuisine_type: str = Field(
        ..., description="Type of cuisine (e.g., Italian, Asian, Mexican)"
    )
    difficulty: str = Field(..., description="Difficulty level (easy, medium, hard)")
    prep_time: str = Field(..., description="Preparation time")
    cook_time: str = Field(..., description="Cooking time")
    servings: int = Field(..., description="Number of servings")
    ingredients: List[Ingredient] = Field(..., description="List of ingredients")
    instructions: List[str] = Field(
        ..., description="Step-by-step cooking instructions"
    )
    tags: List[str] = Field(
        default_factory=list, description="Tags/keywords for the recipe"
    )
    spice_level: Optional[str] = Field(
        None, description="Spice level (mild, medium, hot, extra-hot)"
    )


class KBResponse(BaseModel):
    """Response from knowledge base answerer."""

    query: str = Field(..., description="Original user query")
    recipe: Optional[Recipe] = Field(None, description="Matched recipe from KB")
    confidence: ConfidenceLevel = Field(
        ..., description="Confidence level of the match"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Numerical confidence score (0-1)"
    )
    matched_tags: List[str] = Field(
        default_factory=list, description="Tags that matched the query"
    )
    reasoning: str = Field(..., description="Explanation of why this recipe was chosen")
    needs_web: bool = Field(
        False, description="Whether web search is needed for better results"
    )


class QueryAnalysis(BaseModel):
    """Analysis of user query."""

    intent: str = Field(
        ..., description="Detected intent (e.g., 'find_recipe', 'get_ingredients')"
    )
    cuisine_preference: Optional[str] = Field(
        None, description="Detected cuisine preference"
    )
    dietary_restrictions: List[str] = Field(
        default_factory=list, description="Detected dietary restrictions"
    )
    spice_preference: Optional[str] = Field(
        None, description="Detected spice preference"
    )
    keywords: List[str] = Field(..., description="Extracted keywords from query")
    complexity_preference: Optional[str] = Field(
        None, description="Detected complexity preference"
    )


class SearchResult(BaseModel):
    """Individual search result from web search."""

    url: str = Field(..., description="URL of the search result")
    title: str = Field(..., description="Title of the search result")
    snippet: str = Field(..., description="Snippet/description of the search result")
    domain: str = Field(..., description="Domain of the URL")


class WebSearchResponse(BaseModel):
    """Response from web search for recipe candidates."""

    query: str = Field(..., description="Original search query")
    search_results: List[SearchResult] = Field(
        ..., description="List of search results (max 5)"
    )
    total_results: int = Field(..., description="Total number of results found")
    search_time_ms: int = Field(
        ..., description="Search execution time in milliseconds"
    )
    success: bool = Field(..., description="Whether the search was successful")


class EnhancedKBResponse(BaseModel):
    """Enhanced KB response that includes web search results when needed."""

    query: str = Field(..., description="Original user query")
    recipe: Optional[Recipe] = Field(None, description="Matched recipe from KB")
    confidence: ConfidenceLevel = Field(
        ..., description="Confidence level of the match"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Numerical confidence score (0-1)"
    )
    matched_tags: List[str] = Field(
        default_factory=list, description="Tags that matched the query"
    )
    reasoning: str = Field(..., description="Explanation of why this recipe was chosen")
    needs_web: bool = Field(
        False, description="Whether web search is needed for better results"
    )
    web_search_results: Optional[WebSearchResponse] = Field(
        None, description="Web search results if needs_web is True"
    )


class ExtractedIngredient(BaseModel):
    """Extracted ingredient from web page."""

    name: str = Field(..., description="Name of the ingredient")
    amount: Optional[str] = Field(None, description="Amount/quantity")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    raw_text: str = Field(..., description="Original text as found on page")


class ExtractedRecipe(BaseModel):
    """Extracted recipe from web page."""

    url: str = Field(..., description="Source URL of the recipe")
    title: Optional[str] = Field(None, description="Recipe title")
    description: Optional[str] = Field(None, description="Recipe description")
    author: Optional[str] = Field(None, description="Recipe author")
    prep_time: Optional[str] = Field(None, description="Preparation time")
    cook_time: Optional[str] = Field(None, description="Cooking time")
    total_time: Optional[str] = Field(None, description="Total time")
    servings: Optional[str] = Field(None, description="Number of servings")
    yield_amount: Optional[str] = Field(None, description="Yield amount")
    ingredients: List[ExtractedIngredient] = Field(
        default_factory=list, description="List of ingredients"
    )
    instructions: List[str] = Field(
        default_factory=list, description="Step-by-step instructions"
    )
    nutrition_info: Optional[Dict[str, Any]] = Field(
        None, description="Nutritional information"
    )
    rating: Optional[float] = Field(None, description="Recipe rating")
    review_count: Optional[int] = Field(None, description="Number of reviews")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    tags: List[str] = Field(default_factory=list, description="Recipe tags")
    image_url: Optional[str] = Field(None, description="Recipe image URL")
    extraction_method: str = Field(..., description="Method used for extraction")
    extraction_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in extraction quality"
    )


class RecipeExtractionResponse(BaseModel):
    """Response from recipe extraction process."""

    url: str = Field(..., description="Source URL")
    success: bool = Field(..., description="Whether extraction was successful")
    recipe: Optional[ExtractedRecipe] = Field(None, description="Extracted recipe data")
    extraction_time_ms: int = Field(..., description="Time taken for extraction")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    extraction_methods_tried: List[str] = Field(
        default_factory=list, description="Methods attempted during extraction"
    )
