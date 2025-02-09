"""
NBA Trade Evaluation - Data Collection Module

Handles fetching and caching of essential NBA player and team statistics.
Designed for MVP with clear extension points.
"""

import os
import time
import logging
from typing import Optional
import pandas as pd
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.static import players, teams
from config import (  # Only import what we need from config
    API_CONFIG,
    DIRECTORIES,
    get_file_path,
    PROCESSING_CONFIG
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Remove these since we're using DIRECTORIES from config.py
# RAW_DIR = "data/raw"
# CACHE_DIR = "data/cache"
# os.makedirs(RAW_DIR, exist_ok=True)
# os.makedirs(CACHE_DIR, exist_ok=True)

class DataCollector:
    """Handles NBA data collection with caching support."""
    
    def __init__(self):
        self.essential_stats = [
            # Core stats needed for impact score calculation
            "PTS", "AST", "REB", "STL", "BLK", "TOV",
            "FG_PCT", "FG3_PCT", "FT_PCT",
            "GP", "PLAYER_ID", "PLAYER_NAME", "TEAM_ID"
        ]
        
        self.season = API_CONFIG["season"]
        self.delay = API_CONFIG["delay"]

    def fetch_player_logs(self, player_id: int) -> Optional[pd.DataFrame]:
        """Fetch and cache player game logs."""
        cache_file = get_file_path("cache", f"player_{player_id}_{self.season}.csv")
        
        # Check cache first
        if cache_file.exists():
            return pd.read_csv(cache_file)
            
        try:
            # Fetch from API
            logs = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=self.season
            ).get_data_frames()[0]
            
            # Rename columns to match our expected format
            column_mapping = {
                'PTS': 'PTS',
                'AST': 'AST',
                'REB': 'REB',
                'STL': 'STL',
                'BLK': 'BLK',
                'TOV': 'TOV',
                'FG_PCT': 'FG_PCT',
                'FG3_PCT': 'FG3_PCT',
                'FT_PCT': 'FT_PCT'
            }
            
            logs = logs.rename(columns=column_mapping)
            
            # Cache the results
            if not logs.empty:
                logs.to_csv(cache_file, index=False)
                return logs
                
        except Exception as e:
            logging.warning(f"Failed to fetch logs for player {player_id}: {e}")
            
        return None

    def collect_player_stats(self) -> pd.DataFrame:
        """Collect essential statistics for all active players."""
        all_players = players.get_active_players()
        data = []
        
        for player in all_players:
            logs = self.fetch_player_logs(player["id"])
            
            if logs is not None and not logs.empty:
                # Filter minimum games requirement
                num_games = len(logs)
                if num_games < PROCESSING_CONFIG["min_games_played"]:
                    continue
                    
                # Calculate averages for essential stats
                stats = {}
                for stat in self.essential_stats:
                    if stat in logs.columns:
                        stats[stat] = logs[stat].mean()
                
                # Add required fields
                stats['GP'] = num_games
                stats['PLAYER_ID'] = player['id']
                stats['PLAYER_NAME'] = player['full_name']
                data.append(stats)
                
            time.sleep(self.delay)
        
        df = pd.DataFrame(data)
        raw_file = get_file_path("raw", "player_stats_raw.csv")
        df.to_csv(raw_file, index=False)
        
        logging.info(f"Collected stats for {len(data)} players")
        return df

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate collected data meets minimum requirements.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            bool indicating if data is valid
        """
        if df.empty:
            return False
            
        # Check essential columns exist
        missing_cols = set(self.essential_stats) - set(df.columns)
        if missing_cols:
            logging.error(f"Missing essential columns: {missing_cols}")
            return False
            
        # Check minimum number of players
        if len(df) < 50:  # Arbitrary minimum for MVP
            logging.error("Insufficient player data collected")
            return False
            
        return True

    def get_player_stats(self, force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Get player statistics, either from cache or fresh collection.
        
        Args:
            force_refresh: Force new data collection
            
        Returns:
            DataFrame with player statistics or None if collection fails
        """
        raw_file = get_file_path("raw", "player_stats_raw.csv")
        
        # Use cached data if available and not forcing refresh
        if not force_refresh and raw_file.exists():
            df = pd.read_csv(raw_file)
            if self.validate_data(df):
                return df
                
        # Collect fresh data
        df = self.collect_player_stats()
        return df if self.validate_data(df) else None

    def fetch_team_stats(self) -> pd.DataFrame:
        """Fetch and process team statistics."""
        logging.info("Fetching team statistics...")
        all_teams = teams.get_teams()
        data = []
        
        for team in all_teams:
            try:
                logs = teamgamelog.TeamGameLog(
                    team_id=team["id"],
                    season=self.season
                ).get_data_frames()[0]
                
                if not logs.empty:
                    stats = logs.mean(numeric_only=True)
                    stats["TEAM_ID"] = team["id"]
                    stats["TEAM_NAME"] = team["full_name"]
                    data.append(stats)
                
                time.sleep(self.delay)
                
            except Exception as e:
                logging.warning(f"Failed to fetch team stats for {team['full_name']}: {e}")
                continue
        
        df = pd.DataFrame(data)
        raw_file = get_file_path("raw", "team_stats_raw.csv")
        df.to_csv(raw_file, index=False)
        
        logging.info(f"Collected stats for {len(data)} teams")
        return df


def fetch_team_game_logs(team_id, season="2023-24"):
    """
    Fetch game logs for a team and store as a CSV.
    """
    cache_file = os.path.join(CACHE_DIR, f"team_{team_id}_{season}.csv")

    if os.path.exists(cache_file):
        return pd.read_csv(cache_file)

    try:
        logs = teamgamelog.TeamGameLog(team_id=team_id, season=season).get_data_frames()[0]
        logs.to_csv(cache_file, index=False)
        return logs
    except Exception as e:
        logging.warning(f"⚠️ Failed to fetch logs for team {team_id}: {e}")
        return pd.DataFrame()


def fetch_team_stats(season="2023-24"):
    """
    Fetches team stats and saves to CSV.
    """
    all_teams = teams.get_teams()
    data = []

    for team in all_teams:
        logs = fetch_team_game_logs(team["id"], season)
        if logs.empty:
            continue

        avg_stats = logs[["PTS", "AST", "REB"]].mean().to_dict()
        avg_stats["TEAM_NAME"] = team["full_name"]
        avg_stats["TEAM_ID"] = team["id"]
        data.append(avg_stats)

        time.sleep(1)  # Prevent API rate limiting

    df = pd.DataFrame(data)
    df.to_csv(os.path.join(RAW_DIR, "team_stats_raw.csv"), index=False)
    logging.info("✅ Team stats saved to team_stats_raw.csv")


def get_collector() -> DataCollector:
    """Factory function for DataCollector."""
    return DataCollector()


def clear_cache():
    """Clear all cached files."""
    cache_dir = get_file_path("cache", "")
    for file in cache_dir.glob("*.csv"):
        file.unlink()  # Delete file
    logging.info("Cache cleared")


if __name__ == "__main__":
    collector = get_collector()
    
    # Fetch player stats
    player_stats = collector.get_player_stats(force_refresh=True)
    if player_stats is not None:
        print(f"\nPlayer Statistics:")
        print(f"Successfully collected data for {len(player_stats)} players")
        print("\nSample player statistics:")
        print(player_stats.head())
    
    # Fetch team stats
    team_stats = collector.fetch_team_stats()
    print(f"\nTeam Statistics:")
    print(f"Successfully collected data for {len(team_stats)} teams")
    print("\nSample team statistics:")
    print(team_stats.head())

    # clear_cache()  # Add this line to clear cache when running the file
