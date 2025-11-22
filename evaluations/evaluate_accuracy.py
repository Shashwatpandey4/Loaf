#!/usr/bin/env python3
"""
Accuracy-focused evaluation with MRR and NDCG metrics.
Measures: Accuracy, Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (NDCG).
"""

import json
import time
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

from evaluations.baseline import BaselineAnswerer
from evaluations.accuracy_dataset import get_accuracy_test_queries, AccuracyTestQuery
from src.fullstack_kb_answerer import FullStackKBAnswerer
from src.models.contracts import Recipe
from knowledge.recipes import get_all_recipes


def get_top_k_recipes_baseline(query: str, k: int = 10) -> List[Tuple[Recipe, float]]:
    """Get top-k recipes from baseline system with scores."""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    scored_recipes = []
    
    for recipe in get_all_recipes():
        score = 0.0
        
        # Check recipe name
        recipe_name_lower = recipe.name.lower()
        for word in query_words:
            if word in recipe_name_lower:
                score += 0.3
        
        # Check tags
        for tag in recipe.tags:
            tag_lower = tag.lower()
            for word in query_words:
                if word in tag_lower:
                    score += 0.2
        
        # Check ingredients
        for ingredient in recipe.ingredients:
            ing_name_lower = ingredient.name.lower()
            for word in query_words:
                if word in ing_name_lower:
                    score += 0.1
        
        scored_recipes.append((recipe, score))
    
    # Sort by score descending
    scored_recipes.sort(key=lambda x: x[1], reverse=True)
    return scored_recipes[:k]


def get_top_k_recipes_fullstack(query: str, k: int = 10) -> List[Tuple[Recipe, float]]:
    """Get top-k recipes from FullStackKBAnswerer with scores."""
    from src.query_processor import QueryProcessor, RecipeMatcher
    from src.models.contracts import QueryAnalysis
    
    query_processor = QueryProcessor()
    recipe_matcher = RecipeMatcher()
    
    analysis = query_processor.analyze_query(query)
    
    scored_recipes = []
    
    for recipe in recipe_matcher.recipes:
        score, _ = recipe_matcher._calculate_match_score(recipe, analysis)
        scored_recipes.append((recipe, score))
    
    # Sort by score descending
    scored_recipes.sort(key=lambda x: x[1], reverse=True)
    return scored_recipes[:k]


@dataclass
class RankingResult:
    """Result for a single query ranking evaluation."""
    
    query: str
    system_name: str
    correct_recipe_id: str
    returned_recipe_id: str | None
    rank: int | None  # Rank of correct recipe (1-indexed, None if not found)
    is_correct: bool
    mrr: float  # Reciprocal rank (1/rank if found, else 0)
    ndcg: float  # NDCG score
    response_time_ms: float
    error: str | None = None


@dataclass
class SystemRankingMetrics:
    """Ranking metrics for a system."""
    
    system_name: str
    total_queries: int
    correct_answers: int
    accuracy: float
    mrr: float  # Mean Reciprocal Rank
    ndcg: float  # Mean NDCG
    avg_response_time_ms: float
    errors: int
    error_rate: float


def calculate_ndcg(relevance_scores: List[int], k: int = None) -> float:
    """Calculate NDCG for a ranked list.
    
    Args:
        relevance_scores: List of relevance scores (1 for relevant, 0 for not)
        k: Cutoff rank (default: length of list)
    """
    if k is None:
        k = len(relevance_scores)
    
    if k == 0:
        return 0.0
    
    # Calculate DCG
    dcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(relevance_scores[:k]))
    
    # Calculate ideal DCG (all relevant items first)
    ideal_relevance = sorted(relevance_scores, reverse=True)
    idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal_relevance[:k]))
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


class RankingEvaluator:
    """Evaluates systems based on accuracy, MRR, and NDCG."""
    
    def __init__(self):
        self.systems = {
            "baseline": BaselineAnswerer(),
        }
        try:
            self.systems["fullstack_kb"] = FullStackKBAnswerer()
        except (ValueError, ImportError) as e:
            print(f"Warning: Could not initialize fullstack_kb system: {e}")
            print("   Continuing evaluation with baseline system only.")
        self.results: List[RankingResult] = []
    
    def evaluate_query(
        self, 
        test_query: AccuracyTestQuery, 
        system_name: str, 
        system,
        top_k: int = 10
    ) -> RankingResult:
        """Evaluate a single query for ranking metrics."""
        start_time = time.time()
        error = None
        returned_recipe_id = None
        rank = None
        mrr = 0.0
        ndcg = 0.0
        
        try:
            # Get top-k ranked recipes
            if system_name == "baseline":
                top_recipes = get_top_k_recipes_baseline(test_query.query, k=top_k)
            else:  # fullstack_kb
                top_recipes = get_top_k_recipes_fullstack(test_query.query, k=top_k)
            
            # Find rank of correct recipe
            for i, (recipe, score) in enumerate(top_recipes, 1):
                if recipe.id == test_query.correct_recipe_id:
                    rank = i
                    returned_recipe_id = recipe.id
                    mrr = 1.0 / rank
                    break
            
            # Calculate NDCG
            # Create relevance list: 1 for correct recipe, 0 for others
            relevance_scores = [
                1 if recipe.id == test_query.correct_recipe_id else 0
                for recipe, _ in top_recipes
            ]
            ndcg = calculate_ndcg(relevance_scores, k=top_k)
            
            # If no recipe found in top-k, use the single result from system
            if rank is None:
                response = system.answer_query(
                    test_query.query, 
                    include_web_search=True, 
                    extract_recipes=False
                )
                if response.recipe:
                    returned_recipe_id = response.recipe.id
                    if returned_recipe_id == test_query.correct_recipe_id:
                        # Correct but not in top-k, so rank > k
                        rank = top_k + 1
                        mrr = 1.0 / rank
        except Exception as e:
            error = str(e)
        
        response_time_ms = (time.time() - start_time) * 1000
        is_correct = (returned_recipe_id == test_query.correct_recipe_id) if returned_recipe_id else False
        
        return RankingResult(
            query=test_query.query,
            system_name=system_name,
            correct_recipe_id=test_query.correct_recipe_id,
            returned_recipe_id=returned_recipe_id,
            rank=rank,
            is_correct=is_correct,
            mrr=mrr,
            ndcg=ndcg,
            response_time_ms=response_time_ms,
            error=error,
        )
    
    def evaluate_system(
        self, 
        system_name: str, 
        system, 
        test_queries: List[AccuracyTestQuery]
    ) -> List[RankingResult]:
        """Evaluate a system on all test queries."""
        print(f"\n{'='*70}")
        print(f"Evaluating: {system_name}")
        print(f"{'='*70}")
        
        results = []
        for i, test_query in enumerate(test_queries, 1):
            result = self.evaluate_query(test_query, system_name, system)
            results.append(result)
            self.results.append(result)
            
            status = "[OK]" if result.is_correct else "[FAIL]"
            rank_str = f"rank {result.rank}" if result.rank else "not found"
            print(f"[{i:2d}/{len(test_queries)}] {status} {test_query.query[:45]:<45} "
                  f"Expected: {test_query.correct_recipe_id}, {rank_str}, MRR: {result.mrr:.3f}, NDCG: {result.ndcg:.3f}")
        
        return results
    
    def calculate_metrics(
        self, 
        system_name: str, 
        results: List[RankingResult]
    ) -> SystemRankingMetrics:
        """Calculate ranking metrics."""
        total = len(results)
        if total == 0:
            return SystemRankingMetrics(
                system_name=system_name,
                total_queries=0,
                correct_answers=0,
                accuracy=0.0,
                mrr=0.0,
                ndcg=0.0,
                avg_response_time_ms=0.0,
                errors=0,
                error_rate=0.0,
            )
        
        successful_results = [r for r in results if not r.error]
        errors = [r for r in results if r.error]
        correct = sum(1 for r in successful_results if r.is_correct)
        accuracy = correct / total if total > 0 else 0.0
        
        mrr = sum(r.mrr for r in successful_results) / len(successful_results) if successful_results else 0.0
        ndcg = sum(r.ndcg for r in successful_results) / len(successful_results) if successful_results else 0.0
        
        avg_time = (
            sum(r.response_time_ms for r in successful_results) / len(successful_results)
            if successful_results
            else 0.0
        )
        
        return SystemRankingMetrics(
            system_name=system_name,
            total_queries=total,
            correct_answers=correct,
            accuracy=accuracy,
            mrr=mrr,
            ndcg=ndcg,
            avg_response_time_ms=avg_time,
            errors=len(errors),
            error_rate=len(errors) / total if total > 0 else 0.0,
        )
    
    def print_results(self, all_metrics: Dict[str, SystemRankingMetrics]):
        """Print ranking results."""
        print(f"\n{'='*70}")
        print("RANKING EVALUATION RESULTS")
        print(f"{'='*70}\n")
        
        for system_name, metrics in all_metrics.items():
            print(f"System: {system_name}")
            print(f"  Total Queries: {metrics.total_queries}")
            print(f"  Correct Answers: {metrics.correct_answers}")
            print(f"  Accuracy: {metrics.accuracy:.1%}")
            print(f"  MRR (Mean Reciprocal Rank): {metrics.mrr:.3f}")
            print(f"  NDCG (Normalized Discounted Cumulative Gain): {metrics.ndcg:.3f}")
            print(f"  Avg Response Time: {metrics.avg_response_time_ms:.0f}ms")
            print(f"  Errors: {metrics.errors} ({metrics.error_rate:.1%})")
            print()
    
    def plot_metrics(self, all_metrics: Dict[str, SystemRankingMetrics], output_dir: Path):
        """Create grouped bar chart for Accuracy, MRR, and NDCG."""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        systems = list(all_metrics.keys())
        system_labels = {
            'baseline': 'Baseline\n(Simple Keyword Matching)',
            'fullstack_kb': 'FullStackKBAnswerer\n(RAG with Query Analysis)'
        }
        labels = [system_labels.get(s, s) for s in systems]
        
        # Extract metrics
        accuracies = [all_metrics[s].accuracy * 100 for s in systems]  # Convert to percentage
        mrrs = [all_metrics[s].mrr * 100 for s in systems]  # Convert to percentage for consistency
        ndcgs = [all_metrics[s].ndcg * 100 for s in systems]  # Convert to percentage
        
        # Create figure with more space
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Increase spacing between groups
        x = np.arange(len(systems)) * 1.5  # More space between groups
        width = 0.22  # Slightly narrower bars for better spacing
        
        # Create bars with more spacing
        bars1 = ax.bar(x - width, accuracies, width, label='Accuracy', color='#4ECDC4', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x, mrrs, width, label='MRR', color='#45B7D1', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars3 = ax.bar(x + width, ndcgs, width, label='NDCG', color='#96CEB4', alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars with better positioning
        def add_value_labels(bars, values):
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                       f'{val:.1f}%',
                       ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        add_value_labels(bars1, accuracies)
        add_value_labels(bars2, mrrs)
        add_value_labels(bars3, ndcgs)
        
        # Styling
        ax.set_ylabel('Score (%)', fontsize=15, fontweight='bold')
        ax.set_title('Recipe Retrieval Performance: Accuracy, MRR, and NDCG', 
                    fontsize=17, fontweight='bold', pad=25)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=12, ha='center')
        ax.set_ylim(0, 110)  # More room at top for labels
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Move legend to bottom center, outside the plot area
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.08), 
                 ncol=3, fontsize=13, framealpha=0.95, fancybox=True, shadow=True)
        
        # Add explanation text box below legend (multiline)
        explanation_text = (
            "Accuracy: % of queries with correct recipe at rank 1\n"
            "MRR: Mean Reciprocal Rank (1/rank of first correct result)\n"
            "NDCG: Normalized Discounted Cumulative Gain (ranking quality)"
        )
        ax.text(0.5, -0.25, explanation_text, transform=ax.transAxes,
               fontsize=10, ha='center', va='top', 
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8),
               family='monospace')
        
        # Adjust layout with more padding at bottom
        plt.tight_layout(rect=[0, 0.20, 1, 0.98])  # More space at bottom for legend and description
        
        plot_file = output_dir / f"ranking_comparison_{timestamp}.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"Ranking comparison plot saved to: {plot_file}")
        plt.close()
    
    def save_results(self, output_dir: Path, all_metrics: Dict[str, SystemRankingMetrics]):
        """Save results to JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results_file = output_dir / f"ranking_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(
                {
                    "timestamp": timestamp,
                    "results": [asdict(r) for r in self.results],
                    "metrics": {name: asdict(m) for name, m in all_metrics.items()},
                },
                f,
                indent=2,
            )
        
        print(f"Results saved to: {results_file}")
    
    def run_evaluation(self, save_results: bool = True):
        """Run ranking evaluation."""
        test_queries = get_accuracy_test_queries()
        
        print(f"\n{'='*70}")
        print("RECIPE RETRIEVAL RANKING EVALUATION")
        print(f"{'='*70}")
        print(f"Test Queries: {len(test_queries)}")
        print(f"Systems: {', '.join(self.systems.keys())}")
        print(f"Metrics: Accuracy, MRR (Mean Reciprocal Rank), NDCG")
        print(f"{'='*70}")
        
        all_metrics = {}
        
        for system_name, system in self.systems.items():
            results = self.evaluate_system(system_name, system, test_queries)
            metrics = self.calculate_metrics(system_name, results)
            all_metrics[system_name] = metrics
        
        self.print_results(all_metrics)
        
        if save_results:
            output_dir = Path("evaluations/results")
            self.save_results(output_dir, all_metrics)
            self.plot_metrics(all_metrics, output_dir)
        
        return all_metrics


def main():
    """Main entry point."""
    evaluator = RankingEvaluator()
    evaluator.run_evaluation()


if __name__ == "__main__":
    main()
