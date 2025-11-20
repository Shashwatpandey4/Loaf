"""
Enhanced KB answerer with recipe detection integration.
"""

from typing import Tuple

from src.models.contracts import ConfidenceLevel, EnhancedKBResponse, QueryAnalysis, Recipe
from src.query_processor import QueryProcessor, RecipeMatcher
from src.recipe_extraction import RecipeDetector
from src.web_search import RecipeWebSearcher


class ConfidenceScorer:
    """Calculates confidence scores for recipe matches."""

    @staticmethod
    def calculate_confidence(
        score: float, matched_tags: list[str], analysis: QueryAnalysis
    ) -> Tuple[ConfidenceLevel, float, str]:
        """Calculate confidence level and reasoning."""

        # Base confidence from match score
        confidence_score = score

        # Adjust based on number of matched tags
        if len(matched_tags) >= 3:
            confidence_score += 0.1
        elif len(matched_tags) == 0:
            confidence_score -= 0.3

        # Adjust based on query specificity
        if len(analysis.keywords) >= 3:
            confidence_score += 0.1
        elif len(analysis.keywords) == 1:
            confidence_score -= 0.2

        # Adjust based on cuisine match
        if analysis.cuisine_preference:
            confidence_score += 0.1

        # Adjust based on spice level match
        if analysis.spice_preference:
            confidence_score += 0.05

        # Ensure score is between 0 and 1
        confidence_score = max(0.0, min(1.0, confidence_score))

        # Determine confidence level
        if confidence_score >= 0.8:
            level = ConfidenceLevel.HIGH
            reasoning = f"High confidence match with score {confidence_score:.2f}. Found strong keyword matches: {', '.join(matched_tags[:3])}"
        elif confidence_score >= 0.5:
            level = ConfidenceLevel.MEDIUM
            reasoning = f"Medium confidence match with score {confidence_score:.2f}. Found some relevant matches: {', '.join(matched_tags[:2])}"
        elif confidence_score >= 0.2:
            level = ConfidenceLevel.LOW
            reasoning = f"Low confidence match with score {confidence_score:.2f}. Limited matches found: {', '.join(matched_tags[:1])}"
        else:
            level = ConfidenceLevel.NEEDS_WEB
            reasoning = f"Very low confidence match with score {confidence_score:.2f}. No strong matches found in knowledge base."

        return level, confidence_score, reasoning


class FullStackKBAnswerer:
    """Complete KB answerer with web search and recipe detection."""

    def __init__(self):
        self.query_processor = QueryProcessor()
        self.recipe_matcher = RecipeMatcher()
        self.confidence_scorer = ConfidenceScorer()
        self.web_searcher = RecipeWebSearcher()
        self.recipe_detector = RecipeDetector()

    def answer_query(
        self, query: str, include_web_search: bool = True, extract_recipes: bool = True
    ) -> EnhancedKBResponse:
        """Answer a food query using KB, web search, and recipe detection."""

        # Analyze the query
        analysis = self.query_processor.analyze_query(query)

        # Find best matching recipe
        recipe, matched_tags, match_score = self.recipe_matcher.find_best_match(
            analysis
        )

        # Calculate confidence
        confidence_level, confidence_score, reasoning = (
            self.confidence_scorer.calculate_confidence(
                match_score, matched_tags, analysis
            )
        )

        # Determine if web search is needed
        # Search web for NEEDS_WEB, LOW, and MEDIUM confidence matches
        # Only skip web search for HIGH confidence matches
        needs_web = (
            confidence_level != ConfidenceLevel.HIGH
        )

        # Perform web search if needed and requested
        web_search_results = None
        extracted_recipes = []

        if needs_web and include_web_search:
            web_search_results = self.web_searcher.find_recipe_candidates(query)

            # Extract recipes from web search results if requested
            if (
                extract_recipes
                and web_search_results
                and web_search_results.search_results
            ):
                print(
                    f"🔍 Extracting recipes from {len(web_search_results.search_results)} URLs..."
                )

                urls = [result.url for result in web_search_results.search_results]
                extraction_results = self.recipe_detector.extract_multiple_recipes(urls)

                # Filter successful extractions
                extracted_recipes = [
                    result.recipe
                    for result in extraction_results
                    if result.success and result.recipe
                ]

                print(f"✅ Successfully extracted {len(extracted_recipes)} recipes")

        return EnhancedKBResponse(
            query=query,
            recipe=recipe,
            confidence=confidence_level,
            confidence_score=confidence_score,
            matched_tags=matched_tags,
            reasoning=reasoning,
            needs_web=needs_web,
            web_search_results=web_search_results,
        )

    def get_available_recipes(self) -> list[Recipe]:
        """Get all available recipes in the knowledge base."""
        return self.recipe_matcher.recipes

    def schedule_meal_plan(
        self,
        plan: dict,
        recipes_map: dict,
        start_date: datetime,
        time_str: str = "18:00",
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
        timezone: str = "UTC",
        dry_run: bool = False,
    ) -> list[str]:
        """Schedule a 7-day meal plan to Google Calendar and return event links.

        This method requires the `calendar_agent` package and Google API
        dependencies installed. It will raise a RuntimeError if calendar
        integration is not available.
        """
        try:
            from calendar_agent.google_calendar import get_credentials, create_event_from_details
        except Exception as e:
            raise RuntimeError("Calendar integration not available: " + str(e))

        hour, minute = map(int, time_str.split(":"))

        if dry_run:
            # Build event payloads but do not call Google APIs
            events: list[dict] = []
            for i in range(7):
                day_key = f"day_{i+1}"
                recipe_name = plan.get(day_key)
                recipe = recipes_map.get(recipe_name)

                start_dt = datetime.fromisoformat(start_date.isoformat() if isinstance(start_date, datetime) else start_date)
                start_dt = start_dt.replace(hour=hour, minute=minute) + timedelta(days=i)
                end_dt = start_dt + timedelta(minutes=(int(str(getattr(recipe, "prep_time", "0")).split()[0]) if recipe and getattr(recipe, "prep_time", None) else 60))

                description = getattr(recipe, "description", "") if recipe else ""

                event = {
                    "summary": f"Meal: {recipe_name}",
                    "description": description,
                    "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone},
                }
                events.append(event)

            return events

        creds = get_credentials(client_secrets_file=credentials_path, token_file=token_path)

        created_links: list[str] = []
        for i in range(7):
            day_key = f"day_{i+1}"
            recipe_name = plan.get(day_key)
            recipe = recipes_map.get(recipe_name)

            start_dt = datetime.fromisoformat(start_date.isoformat() if isinstance(start_date, datetime) else start_date)
            start_dt = start_dt.replace(hour=hour, minute=minute) + timedelta(days=i)

            description = ""
            duration = 60
            if recipe:
                description = getattr(recipe, "description", "") or ""
                try:
                    duration = int(str(getattr(recipe, "prep_time", "0")).split()[0]) + int(str(getattr(recipe, "cook_time", "0")).split()[0])
                except Exception:
                    duration = 60

            created = create_event_from_details(
                credentials=creds,
                title=f"Meal: {recipe_name}",
                start_dt=start_dt,
                duration_minutes=duration,
                description=description,
                timezone=timezone,
            )

            created_links.append(created.get("htmlLink"))

        return created_links

    def search_by_tags(self, tags: list[str]) -> list[Recipe]:
        """Search recipes by specific tags."""
        matching_recipes = []
        for recipe in self.recipe_matcher.recipes:
            for tag in tags:
                if any(tag.lower() in recipe_tag.lower() for recipe_tag in recipe.tags):
                    matching_recipes.append(recipe)
                    break
        return matching_recipes

    def extract_recipe_from_url(self, url: str):
        """Extract recipe from a specific URL."""
        return self.recipe_detector.extract_recipe(url)
