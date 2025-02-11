"""
Tests for the NBA Trade Evaluation data collection component.
Ensures data fetching, caching, and processing work as expected.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path
import logging

from src.fetch_data import DataCollector, get_collector, clear_cache
from src.config import PROCESSING_CONFIG, get_file_path

# Set up logging for tests
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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
    return [
        {"id": 2544, "full_name": "LeBron James", "teamId": 1610612747},
        {"id": 201142, "full_name": "Kevin Durant", "teamId": 1610612756}
    ]

@pytest.fixture
def collector():
    """Create a DataCollector instance for testing."""
    return DataCollector()

def test_init(collector):
    """Test DataCollector initialization."""
    assert collector.essential_stats == [
        "PTS", "AST", "REB", "STL", "BLK", "TOV",
        "FG_PCT", "FG3_PCT", "FT_PCT",
        "GP", "PLAYER_ID", "PLAYER_NAME", "TEAM_ID"
    ]
    assert collector.season == "2023-24"
    assert collector.delay == 1

@patch('pathlib.Path.exists')
@patch('src.fetch_data.playergamelog.PlayerGameLog')
def test_fetch_player_logs(mock_player_log, mock_exists, collector, sample_game_logs):
    """Test fetching player game logs."""
    # Setup mocks
    mock_exists.return_value = False  # Ensure cache is not used
    mock_instance = MagicMock()
    mock_instance.get_data_frames.return_value = [sample_game_logs]
    mock_player_log.return_value = mock_instance
    
    # Test fetching logs
    logs = collector.fetch_player_logs(2544)  # LeBron's ID
    
    assert logs is not None
    assert not logs.empty
    assert len(logs) == 20
    assert "PTS" in logs.columns
    assert "TEAM_ID" in logs.columns
    assert logs["PTS"].mean() == 25.0

@patch('pathlib.Path.exists')
@patch('src.fetch_data.players.get_active_players')
@patch('src.fetch_data.playergamelog.PlayerGameLog')
def test_collect_player_stats(mock_player_log, mock_get_players, mock_exists, collector, sample_game_logs, sample_players):
    """Test collecting player statistics."""
    # Setup mocks
    mock_exists.return_value = False  # Ensure cache is not used
    mock_get_players.return_value = sample_players
    mock_instance = MagicMock()
    mock_instance.get_data_frames.return_value = [sample_game_logs]
    mock_player_log.return_value = mock_instance
    
    # Test collecting stats
    stats = collector.collect_player_stats()
    
    assert not stats.empty
    assert len(stats) == len(sample_players)
    assert all(col in stats.columns for col in collector.essential_stats)
    
    # Verify first player's stats
    first_player = stats.iloc[0]
    assert first_player["PLAYER_NAME"] == "LeBron James"
    assert abs(first_player["PTS"] - 25.0) < 0.01  # Use approximate equality
    assert abs(first_player["AST"] - 8.0) < 0.01
    assert abs(first_player["REB"] - 5.0) < 0.01
    assert first_player["TEAM_ID"] == 1610612747

def test_validate_data(collector):
    """Test data validation."""
    # Test valid data
    valid_data = pd.DataFrame({
        "PTS": [25.0], "AST": [8.0], "REB": [5.0],
        "STL": [2.0], "BLK": [1.0], "TOV": [3.0],
        "FG_PCT": [0.5], "FG3_PCT": [0.375], "FT_PCT": [0.833],
        "GP": [20], "PLAYER_ID": [2544],
        "PLAYER_NAME": ["test_player_1"], "TEAM_ID": [1610612747]
    })
    assert collector.validate_data(valid_data)
    
    # Test empty data
    empty_data = pd.DataFrame()
    assert not collector.validate_data(empty_data)
    
    # Test missing columns
    invalid_data = pd.DataFrame({"PTS": [25.0]})
    assert not collector.validate_data(invalid_data)

@patch('src.fetch_data.teams.get_teams')
@patch('src.fetch_data.teamgamelog.TeamGameLog')
def test_fetch_team_stats(mock_team_log, mock_get_teams, collector, sample_game_logs):
    """Test fetching team statistics."""
    # Setup mocks
    mock_get_teams.return_value = [
        {"id": 1610612747, "full_name": "Los Angeles Lakers"}
    ]
    mock_instance = MagicMock()
    mock_instance.get_data_frames.return_value = [sample_game_logs]
    mock_team_log.return_value = mock_instance
    
    # Test fetching team stats
    stats = collector.fetch_team_stats()
    
    assert not stats.empty
    assert "TEAM_ID" in stats.columns
    assert "TEAM_NAME" in stats.columns
    assert len(stats) == 1
    assert stats.iloc[0]["TEAM_NAME"] == "Los Angeles Lakers"

def test_get_collector():
    """Test collector factory function."""
    collector = get_collector()
    assert isinstance(collector, DataCollector)

def test_clear_cache(tmp_path):
    """Test cache clearing functionality."""
    # Create temporary cache files
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "test1.csv").touch()
    (cache_dir / "test2.csv").touch()
    
    # Mock cache directory path
    with patch('src.fetch_data.get_file_path') as mock_get_path:
        mock_get_path.return_value = cache_dir
        clear_cache()
        
        # Verify files are deleted
        assert len(list(cache_dir.glob("*.csv"))) == 0

def test_get_player_stats(collector):
    """Test getting player statistics with caching."""
    # Test with force refresh
    with patch.object(collector, 'collect_player_stats') as mock_collect:
        mock_collect.return_value = pd.DataFrame({
            "PTS": [25.0], "AST": [8.0], "REB": [5.0],
            "STL": [2.0], "BLK": [1.0], "TOV": [3.0],
            "FG_PCT": [0.5], "FG3_PCT": [0.375], "FT_PCT": [0.833],
            "GP": [20], "PLAYER_ID": [2544],
            "PLAYER_NAME": ["test_player_1"], "TEAM_ID": [1610612747]
        })
        
        stats = collector.get_player_stats(force_refresh=True)
        assert stats is not None
        assert not stats.empty
        assert mock_collect.called

if __name__ == "__main__":
    pytest.main([__file__]) 