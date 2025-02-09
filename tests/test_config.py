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
    """Test that all required directories are created and accessible."""
    for dir_name, dir_path in DIRECTORIES.items():
        assert dir_path.exists(), f"Directory {dir_name} does not exist"
        assert dir_path.is_dir(), f"{dir_name} is not a directory"

def test_impact_weights():
    """Test impact weight configuration."""
    # Check essential stats are present
    required_stats = {"PTS", "REB", "AST", "STL", "BLK", "TOV"}
    assert all(stat in IMPACT_WEIGHTS for stat in required_stats), \
        "Missing required statistics in impact weights"
    
    # Check weights are numeric and reasonable
    for stat, weight in IMPACT_WEIGHTS.items():
        assert isinstance(weight, (int, float)), f"Weight for {stat} is not numeric"
        assert -5 <= weight <= 5, f"Weight for {stat} outside reasonable range"

def test_trade_thresholds():
    """Test trade threshold configuration."""
    # Check required thresholds exist
    assert "fair" in TRADE_THRESHOLDS, "Missing 'fair' threshold"
    assert "slightly_unbalanced" in TRADE_THRESHOLDS, "Missing 'slightly_unbalanced' threshold"
    
    # Check threshold values are logical
    assert TRADE_THRESHOLDS["fair"] < TRADE_THRESHOLDS["slightly_unbalanced"], \
        "Fair threshold should be less than slightly unbalanced"
    
    # Check threshold ranges
    for name, value in TRADE_THRESHOLDS.items():
        assert 0 <= value <= 20, f"Threshold {name} outside reasonable range"

def test_processing_config():
    """Test processing configuration."""
    assert "min_games_played" in PROCESSING_CONFIG, "Missing minimum games played setting"
    assert isinstance(PROCESSING_CONFIG["min_games_played"], int), \
        "min_games_played should be an integer"
    assert PROCESSING_CONFIG["min_games_played"] > 0, \
        "min_games_played should be positive"

def test_get_file_path():
    """Test file path generation."""
    # Test valid directory
    path = get_file_path("raw", "test.csv")
    assert isinstance(path, Path), "Should return a Path object"
    assert str(path).endswith("test.csv"), "Should include filename"
    assert "raw" in str(path), "Should include directory type"
    
    # Test invalid directory
    with pytest.raises(ValueError):
        get_file_path("invalid_dir", "test.csv")

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