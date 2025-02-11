"""
NBA Trade Evaluation - Trade Evaluation Module

Handles the core trade evaluation logic with player impact scoring
and fairness assessment. Designed for MVP with clear extension points.
"""

import logging
from typing import Dict, Optional

import pandas as pd
import numpy as np

from src.config import (
    IMPACT_WEIGHTS,
    TRADE_THRESHOLDS,
    PROCESSING_CONFIG,
    get_file_path
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class TradeEvaluator:
    """
    Evaluates NBA trades using player impact scores and fairness metrics.
    Future expansion: Add salary matching, team fit analysis, draft picks.
    """
    
    def __init__(self):
        """Initialize evaluator with player statistics."""
        try:
            stats_file = get_file_path("raw", "player_stats_raw.csv")
            self.player_stats = pd.read_csv(stats_file)
            self._validate_data()
        except Exception as e:
            logging.error(f"Failed to initialize evaluator: {e}")
            raise

    def _validate_data(self) -> None:
        """Ensure required data is available and valid."""
        required_cols = list(IMPACT_WEIGHTS.keys()) + ["PLAYER_ID", "PLAYER_NAME", "GP"]
        missing = set(required_cols) - set(self.player_stats.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def get_player_stats(self, player_id: int) -> Optional[pd.Series]:
        """
        Retrieve player statistics.
        
        Args:
            player_id: NBA player ID
            
        Returns:
            Player statistics or None if not found
        """
        try:
            return self.player_stats[
                self.player_stats["PLAYER_ID"] == player_id
            ].iloc[0]
        except (IndexError, KeyError):
            logging.warning(f"Player {player_id} not found")
            return None

    def calculate_impact_score(self, stats: pd.Series) -> float:
        """
        Calculate player impact score using configured weights.
        
        Future expansion:
        - Add position-specific adjustments
        - Include team context
        - Factor in player age/potential
        """
        if stats["GP"] < PROCESSING_CONFIG["min_games_played"]:
            logging.warning(f"Player {stats['PLAYER_NAME']} has insufficient games")
            return 0.0

        impact = sum(
            stats[stat] * weight
            for stat, weight in IMPACT_WEIGHTS.items()
            if stat in stats
        )
        return impact / stats["GP"]

    def evaluate_trade(self, player1_id: int, player2_id: int) -> Dict:
        """
        Evaluate a trade between two players.
        
        Future expansion:
        - Multi-player trades
        - Draft pick evaluation
        - Salary cap implications
        - Team fit analysis
        """
        # Get player statistics
        p1_stats = self.get_player_stats(player1_id)
        p2_stats = self.get_player_stats(player2_id)
        
        if p1_stats is None or p2_stats is None:
            return {"error": "One or both players not found"}

        # Calculate impact scores
        p1_impact = self.calculate_impact_score(p1_stats)
        p2_impact = self.calculate_impact_score(p2_stats)
        
        # Calculate trade metrics
        impact_diff = abs(p1_impact - p2_impact)
        fairness_score = max(0, 10 - impact_diff)  # 0-10 scale
        
        return {
            "trade_analysis": {
                "players": {
                    str(player1_id): {
                        "name": p1_stats["PLAYER_NAME"],
                        "impact_score": round(p1_impact, 2),
                        "stats_summary": self._get_stats_summary(p1_stats)
                    },
                    str(player2_id): {
                        "name": p2_stats["PLAYER_NAME"],
                        "impact_score": round(p2_impact, 2),
                        "stats_summary": self._get_stats_summary(p2_stats)
                    }
                },
                "evaluation": {
                    "fairness_score": round(fairness_score, 2),
                    "verdict": self._get_verdict(impact_diff),
                    "win_impact": self._estimate_win_impact(p1_impact, p2_impact)
                }
            }
        }

    def _get_stats_summary(self, stats: pd.Series) -> Dict:
        """Create a summary of key player statistics."""
        return {
            "PPG": round(stats["PTS"], 1),
            "RPG": round(stats["REB"], 1),
            "APG": round(stats["AST"], 1),
            "GP": int(stats["GP"])
        }

    def _get_verdict(self, difference: float) -> str:
        """
        Get trade verdict based on impact difference.
        
        Future expansion:
        - More granular verdicts
        - Team-specific context
        - Consideration of player age/potential
        """
        if difference < TRADE_THRESHOLDS["fair"]:
            return "Fair Trade"
        elif difference < TRADE_THRESHOLDS["slightly_unbalanced"]:
            return "Slightly Unbalanced"
        return "Significantly Unbalanced"

    def _estimate_win_impact(self, impact1: float, impact2: float) -> float:
        """
        Estimate the impact on team wins.
        
        Future expansion:
        - Use advanced win share calculations
        - Factor in team composition
        - Consider strength of schedule
        """
        # Simple estimation for MVP
        impact_diff = impact1 - impact2
        return round(impact_diff / 10, 2)  # Rough conversion to wins


def get_evaluator() -> TradeEvaluator:
    """Factory function for TradeEvaluator."""
    return TradeEvaluator()


if __name__ == "__main__":
    # Example usage
    try:
        evaluator = get_evaluator()
        # Example: Evaluate trade between two players
        result = evaluator.evaluate_trade(1630173, 1628389)
        print("\nTrade Evaluation Result:")
        print(f"Fairness Score: {result['trade_analysis']['evaluation']['fairness_score']}")
        print(f"Verdict: {result['trade_analysis']['evaluation']['verdict']}")
        print(f"Estimated Win Impact: {result['trade_analysis']['evaluation']['win_impact']}")
    except Exception as e:
        logging.error(f"Failed to evaluate trade: {e}")
