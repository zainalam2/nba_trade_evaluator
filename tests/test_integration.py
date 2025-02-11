"""
Tests for integration between different components of the NBA Trade Evaluation system.
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.fetch_data import get_collector
from src.evaluate_trade import get_evaluator

@pytest.fixture
def sample_game_logs():
    """Create sample game logs for testing."""
    return pd.DataFrame({
        "SEASON_ID": ["22023"] * 20,  # 20 games sample
        "Player_ID": [2544] * 20,
        "Game_ID": [f"00223000{i:02d}" for i in range(1, 21)],
        "GAME_DATE": [f"2023-10-{i:02d}" for i in range(1, 21)],
        "MATCHUP": ["LAL vs DEN"] * 20,
        "WL": ["W", "L"] * 10,
        "MIN": [35] * 20,
        "FGM": [10] * 20,
        "FGA": [20] * 20,
        "FG_PCT": [0.500] * 20,
        "FG3M": [3] * 20,
        "FG3A": [8] * 20,
        "FG3_PCT": [0.375] * 20,
        "FTM": [5] * 20,
        "FTA": [6] * 20,
        "FT_PCT": [0.833] * 20,
        "OREB": [1] * 20,
        "DREB": [4] * 20,
        "REB": [5] * 20,
        "AST": [8] * 20,
        "STL": [2] * 20,
        "BLK": [1] * 20,
        "TOV": [3] * 20,
        "PF": [2] * 20,
        "PTS": [25] * 20,
        "PLUS_MINUS": [5] * 20,
        "VIDEO_AVAILABLE": [1] * 20,
        "TEAM_ID": [1610612747] * 20  # Lakers ID
    })

@pytest.fixture
def sample_players():
    """Create sample players list for testing."""
    # Create enough test players to pass the minimum requirement
    players = []
    for i in range(50):  # Minimum requirement is 50 players
        players.append({
            "id": 2544 + i,
            "full_name": f"Test Player {i}",
            "teamId": 1610612747 + (i % 30)  # Cycle through team IDs
        })
    return players

@patch('pathlib.Path.exists')
@patch('src.fetch_data.players.get_active_players')
@patch('src.fetch_data.playergamelog.PlayerGameLog')
def test_end_to_end_flow(mock_player_log, mock_get_players, mock_exists, sample_game_logs, sample_players):
    """Test entire data flow from collection to evaluation with mocked data"""
    # Setup mocks
    mock_exists.return_value = False  # Ensure cache is not used
    mock_get_players.return_value = sample_players
    mock_instance = MagicMock()
    mock_instance.get_data_frames.return_value = [sample_game_logs]
    mock_player_log.return_value = mock_instance
    
    # Collect data
    collector = get_collector()
    stats = collector.get_player_stats(force_refresh=True)
    assert stats is not None
    assert not stats.empty
    assert len(stats) == len(sample_players)
    
    # Test trade evaluation
    evaluator = get_evaluator()
    result = evaluator.evaluate_trade(2544, 2545)  # Test with first two players
    
    assert result is not None
    assert "trade_analysis" in result
    assert "players" in result["trade_analysis"]
    assert "2544" in result["trade_analysis"]["players"]
    assert "2545" in result["trade_analysis"]["players"] 