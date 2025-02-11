"""
Tests for the NBA Trade Evaluation configuration component.
Ensures core configuration functionality works as expected.
"""

import os
import pytest
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.config import (
    DIRECTORIES,
    IMPACT_WEIGHTS,
    TRADE_THRESHOLDS,
    PROCESSING_CONFIG,
    get_file_path,
    validate_config
)

def test_directory_structure():
    """Test directory setup"""
    for dir_name, dir_path in DIRECTORIES.items():
        assert dir_path.exists()
        assert dir_path.is_dir()

def test_impact_weights():
    """Test impact weights configuration"""
    required_stats = {"PTS", "REB", "AST", "STL", "BLK", "TOV"}
    assert all(stat in IMPACT_WEIGHTS for stat in required_stats)
    assert all(isinstance(weight, (int, float)) for weight in IMPACT_WEIGHTS.values())

def test_trade_thresholds():
    """Test trade threshold values"""
    assert TRADE_THRESHOLDS["fair"] < TRADE_THRESHOLDS["slightly_unbalanced"]
    assert all(0 <= value <= 20 for value in TRADE_THRESHOLDS.values())

def test_processing_config():
    """Test processing configuration."""
    assert "min_games_played" in PROCESSING_CONFIG, "Missing minimum games played setting"
    assert isinstance(PROCESSING_CONFIG["min_games_played"], int), \
        "min_games_played should be an integer"
    assert PROCESSING_CONFIG["min_games_played"] > 0, \
        "min_games_played should be positive"

def test_get_file_path():
    """Test file path generation"""
    path = get_file_path("raw", "test.csv")
    assert isinstance(path, Path)
    assert "raw" in str(path)
    with pytest.raises(ValueError):
        get_file_path("invalid", "test.csv")

def test_validate_config():
    """Test configuration validation."""
    assert validate_config(), "Configuration should be valid"

def test_directory_permissions():
    """Test directory permissions."""
    for dir_path in DIRECTORIES.values():
        assert os.access(dir_path, os.W_OK), f"Directory {dir_path} not writable"
        assert os.access(dir_path, os.R_OK), f"Directory {dir_path} not readable"

if __name__ == "__main__":
    pytest.main([__file__]) 