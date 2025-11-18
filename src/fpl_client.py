"""
FPL API Client
Helper module for interacting with the Fantasy Premier League API
"""
import time
from typing import Any

import requests


class FPLClient:
    """Client for interacting with Fantasy Premier League API"""
    
    BASE_URL = "https://fantasy.premierleague.com/api"
    
    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Initialize FPL client
        
        Args:
            rate_limit_delay: Delay between requests in seconds
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
    
    def _get(self, endpoint: str) -> dict[str, Any]:
        """
        Make GET request with rate limiting
        
        Args:
            endpoint: API endpoint (without base URL)
        
        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url)
        response.raise_for_status()
        time.sleep(self.rate_limit_delay)
        return response.json()
    
    def get_bootstrap_static(self) -> dict[str, Any]:
        """
        Get bootstrap-static data containing players, teams, and gameweeks
        
        Returns:
            Dictionary with keys: elements (players), teams, events (gameweeks)
        """
        return self._get("bootstrap-static/")
    
    def get_player_summary(self, player_id: int) -> dict[str, Any]:
        """
        Get detailed player summary including gameweek history
        
        Args:
            player_id: FPL player ID
        
        Returns:
            Dictionary with player details and history
        """
        return self._get(f"element-summary/{player_id}/")
    
    def get_league_standings(self, league_id: int, page: int = 1) -> dict[str, Any]:
        """
        Get league standings
        
        Args:
            league_id: FPL league ID
            page: Page number for pagination
        
        Returns:
            Dictionary with league info and standings
        """
        endpoint = f"leagues-classic/{league_id}/standings/"
        if page > 1:
            endpoint += f"?page_standings={page}"
        return self._get(endpoint)
    
    def get_entry(self, entry_id: int) -> dict[str, Any]:
        """
        Get manager entry details
        
        Args:
            entry_id: FPL entry (team) ID
        
        Returns:
            Dictionary with entry details
        """
        return self._get(f"entry/{entry_id}/")
    
    def get_entry_history(self, entry_id: int) -> dict[str, Any]:
        """
        Get manager entry history
        
        Args:
            entry_id: FPL entry (team) ID
        
        Returns:
            Dictionary with historical data
        """
        return self._get(f"entry/{entry_id}/history/")
    
    def get_entry_picks(self, entry_id: int, gameweek: int) -> dict[str, Any]:
        """
        Get manager picks for a specific gameweek
        
        Args:
            entry_id: FPL entry (team) ID
            gameweek: Gameweek number
        
        Returns:
            Dictionary with picks and gameweek details
        """
        return self._get(f"entry/{entry_id}/event/{gameweek}/picks/")
    
    def get_fixtures(self, gameweek: int | None = None) -> list[dict[str, Any]]:
        """
        Get fixtures
        
        Args:
            gameweek: Optional gameweek number to filter by
        
        Returns:
            List of fixtures
        """
        endpoint = "fixtures/"
        if gameweek:
            endpoint += f"?event={gameweek}"
        return self._get(endpoint)
    
    def get_current_gameweek(self) -> int | None:
        """
        Get current gameweek number
        
        Returns:
            Current gameweek number or None if not started
        """
        data = self.get_bootstrap_static()
        for event in data.get("events", []):
            if event.get("is_current"):
                return event["id"]
        return None


# Example usage
if __name__ == "__main__":
    client = FPLClient()
    
    # Get bootstrap data
    print("Fetching bootstrap data...")
    bootstrap = client.get_bootstrap_static()
    print(f"Found {len(bootstrap['elements'])} players")
    print(f"Found {len(bootstrap['teams'])} teams")
    print(f"Found {len(bootstrap['events'])} gameweeks")
    
    # Get current gameweek
    current_gw = client.get_current_gameweek()
    print(f"\nCurrent gameweek: {current_gw}")
    
    # Get top 5 players by total points
    players = sorted(
        bootstrap['elements'],
        key=lambda x: x['total_points'],
        reverse=True
    )[:5]
    
    print("\nTop 5 players by total points:")
    for i, player in enumerate(players, 1):
        print(f"{i}. {player['web_name']} - {player['total_points']} points")

