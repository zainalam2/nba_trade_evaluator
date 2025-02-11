import pytest
import pandas as pd
from src.evaluate_trade import TradeEvaluator

@pytest.fixture
def evaluator():
    return TradeEvaluator()

def test_calculate_impact_score(evaluator):
    """Test impact score calculation"""
    test_stats = pd.Series({
        "PTS": 20, "AST": 5, "REB": 5,
        "STL": 1, "BLK": 1, "TOV": 2,
        "GP": 10, "PLAYER_NAME": "Test Player"
    })
    score = evaluator.calculate_impact_score(test_stats)
    assert isinstance(score, float)
    assert score > 0

def test_get_verdict(evaluator):
    """Test trade verdict generation"""
    assert evaluator._get_verdict(1.0) == "Fair Trade"
    assert evaluator._get_verdict(5.0) == "Slightly Unbalanced"
    assert evaluator._get_verdict(10.0) == "Significantly Unbalanced"

def test_estimate_win_impact(evaluator):
    """Test win impact estimation"""
    impact = evaluator._estimate_win_impact(20.0, 15.0)
    assert isinstance(impact, float)
    assert -10 <= impact <= 10  # Reasonable range 