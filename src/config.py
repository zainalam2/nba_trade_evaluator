"""
NBA Trade Evaluation - Configuration Module

Core configuration for the MVP with clear expansion points.
Focuses on essential settings while maintaining extensibility.
"""

import os
from pathlib import Path
from typing import Dict

# Project Structure
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Data directories with specific purposes
DIRECTORIES = {
    "raw": DATA_DIR / "raw",        # Raw API data
    "processed": DATA_DIR / "processed",  # Cleaned data
    "cache": DATA_DIR / "cache",     # API response cache
}

# Create necessary directories
for directory in DIRECTORIES.values():
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
API_CONFIG = {
    "season": "2023-24",
    "delay": 1,  # Delay between API calls in seconds
    # Future expansion: Add API keys, endpoints, rate limits
    # "api_key": os.getenv("NBA_API_KEY"),
    # "rate_limit": 60,  # requests per minute
}

# Player Impact Score Weights
# These weights can be adjusted based on analysis
IMPACT_WEIGHTS: Dict[str, float] = {
    "PTS": 1.0,    # Scoring
    "REB": 1.2,    # Rebounding
    "AST": 1.5,    # Playmaking
    "STL": 2.0,    # Defense
    "BLK": 2.0,    # Rim protection
    "TOV": -1.0,   # Ball control
    # Future expansion: Add advanced metrics
    # "PER": 0.0,
    # "TS%": 0.0,
}

# Trade Evaluation Thresholds
TRADE_THRESHOLDS = {
    "fair": 3.0,              # Maximum difference for a fair trade
    "slightly_unbalanced": 7.0,  # Maximum difference for slightly unbalanced
    # Future expansion: Add more granular thresholds
    # "salary_match": 0.85,    # Salary matching requirement
    # "prospect_value": 1.2,   # Multiplier for young players
}

# Data Processing Settings
PROCESSING_CONFIG = {
    "min_games_played": 10,  # Minimum games for valid statistics
    # Future expansion: Add more processing parameters
    # "outlier_threshold": 2.0,
    # "smoothing_factor": 0.1,
}

def get_file_path(directory: str, filename: str) -> Path:
    """
    Get the full path for a file in a specific directory.
    
    Args:
        directory: The directory type ('raw', 'processed', 'cache')
        filename: The name of the file
        
    Returns:
        Path object for the full file path
    """
    if directory not in DIRECTORIES:
        raise ValueError(f"Invalid directory type: {directory}")
    return DIRECTORIES[directory] / filename

def validate_config() -> bool:
    """
    Validate the configuration settings.
    
    Future expansion: Add more validation rules
    
    Returns:
        bool: True if configuration is valid
    """
    try:
        # Validate directories exist
        for directory in DIRECTORIES.values():
            if not directory.exists():
                return False
                
        # Validate impact weights
        if not all(isinstance(v, (int, float)) for v in IMPACT_WEIGHTS.values()):
            return False
            
        # Validate thresholds
        if TRADE_THRESHOLDS["fair"] >= TRADE_THRESHOLDS["slightly_unbalanced"]:
            return False
            
        return True
        
    except Exception:
        return False

# Validate configuration on import
if not validate_config():
    raise ValueError("Invalid configuration detected") 