"""
Web search module for finding recipe candidates using Exa Search API.
"""

import os
import time
from typing import List
from urllib.parse import urlparse

try:
    from exa_py import Exa

    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False

from src.models.contracts import SearchResult, WebSearchResponse


class ExaSearcher:
    """Exa Search API client for recipe candidates."""

    def __init__(self, api_key: str = None):
        """
        Initialize Exa searcher.

        Args:
            api_key: Exa API key. If not provided, will try to get from EXA_API_KEY env var.
        """
        if not EXA_AVAILABLE:
            raise ImportError(
                "exa_py package is not installed. Install it with: pip install exa_py"
            )

        self.api_key = api_key or os.getenv("EXA_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Exa API key is required. Set EXA_API_KEY environment variable or pass api_key parameter."
            )

        self.client = Exa(api_key=self.api_key)
        self.search_cache = {}
        self.cache_max_age = 600

    def search_recipes(self, query: str, max_results: int = 5) -> WebSearchResponse:
        """Search for recipe candidates using Exa Search API."""
        start_time = time.time()

        try:
            enhanced_query = self._enhance_query_for_recipes(query)
            search_results = self._perform_search(enhanced_query, max_results)
            filtered_results = self._filter_recipe_results(search_results)

            search_time_ms = int((time.time() - start_time) * 1000)

            return WebSearchResponse(
                query=query,
                search_results=filtered_results[:max_results],
                total_results=len(filtered_results),
                search_time_ms=search_time_ms,
                success=True,
            )

        except Exception as e:
            print(f"Exa search error: {e}")
            search_time_ms = int((time.time() - start_time) * 1000)
            return WebSearchResponse(
                query=query,
                search_results=[],
                total_results=0,
                search_time_ms=search_time_ms,
                success=False,
            )

    def _enhance_query_for_recipes(self, query: str) -> str:
        """Enhance query to find better recipe results."""
        recipe_terms = ["recipe", "cooking", "how to make", "ingredients"]

        query_lower = query.lower()
        if not any(term in query_lower for term in recipe_terms):
            return f"{query} recipe"

        return query

    def _perform_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Perform the actual Exa search."""
        cache_key = f"{query}:{max_results}"
        current_time = time.time()
        if cache_key in self.search_cache:
            cached_results, cache_time = self.search_cache[cache_key]
            if current_time - cache_time < self.cache_max_age:
                return cached_results
            else:
                del self.search_cache[cache_key]

        results = []

        if not EXA_AVAILABLE:
            raise ImportError(
                "Exa package not available. Install with: pip install exa_py"
            )

        try:
            search_response = self.client.search(
                query=query,
                num_results=max_results * 2,
                contents={"max_characters": 500},
            )

            for result in search_response.results:
                try:
                    url = result.url
                    title = result.title or "Recipe"
                    snippet = ""
                    if hasattr(result, "text") and result.text:
                        snippet = result.text[:500]
                    elif hasattr(result, "highlights") and result.highlights:
                        snippet = " ".join(result.highlights)[:500]
                    elif hasattr(result, "text") and isinstance(result.text, list):
                        snippet = " ".join(result.text)[:500]

                    domain = urlparse(url).netloc

                    if url and title:
                        results.append(
                            SearchResult(
                                url=url, title=title, snippet=snippet, domain=domain
                            )
                        )
                except Exception:
                    continue

            if results:
                self.search_cache[cache_key] = (results, time.time())
                if len(self.search_cache) > 50:
                    oldest_key = min(
                        self.search_cache.keys(), key=lambda k: self.search_cache[k][1]
                    )
                    del self.search_cache[oldest_key]

        except Exception as e:
            print(f"⚠️  Exa search error: {e}")
            raise

        return results

    def _filter_recipe_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Filter and rank results to prioritize recipe sites."""
        recipe_domains = {
            "allrecipes.com",
            "foodnetwork.com",
            "food.com",
            "epicurious.com",
            "bonappetit.com",
            "seriouseats.com",
            "tasty.co",
            "delish.com",
            "cooking.nytimes.com",
            "bbcgoodfood.com",
            "jamieoliver.com",
            "gordonramsay.com",
            "marthastewart.com",
            "bettycrocker.com",
            "kraftrecipes.com",
            "pillsbury.com",
            "tasteofhome.com",
        }

        recipe_keywords = [
            "recipe",
            "cooking",
            "ingredients",
            "instructions",
            "prep time",
            "cook time",
            "servings",
            "directions",
            "how to make",
            "step by step",
        ]

        scored_results = []

        for result in results:
            score = 0

            domain_lower = result.domain.lower()
            if any(recipe_domain in domain_lower for recipe_domain in recipe_domains):
                score += 10

            title_lower = result.title.lower()
            for keyword in recipe_keywords:
                if keyword in title_lower:
                    score += 2

            snippet_lower = result.snippet.lower()
            for keyword in recipe_keywords:
                if keyword in snippet_lower:
                    score += 1

            url_lower = result.url.lower()
            if "/recipe" in url_lower or "/recipes" in url_lower:
                score += 5

            scored_results.append((score, result))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [result for score, result in scored_results if score > 0]


_shared_searcher = None


def get_shared_searcher():
    """Get or create the shared Exa searcher instance."""
    global _shared_searcher
    if _shared_searcher is None:
        _shared_searcher = ExaSearcher()
    return _shared_searcher


class RecipeWebSearcher:
    """High-level interface for recipe web search."""

    def __init__(self):
        self.searcher = get_shared_searcher()

    def find_recipe_candidates(self, query: str) -> WebSearchResponse:
        """Find recipe candidates for a given query."""
        return self.searcher.search_recipes(query)
