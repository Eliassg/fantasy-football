"""
Fantasy Premier League API Data Ingestion Function
Fetches data from FPL API and loads into CDF RAW tables
"""
import os
import time
from datetime import datetime
from typing import Any

import requests
from cognite.client import CogniteClient
from cognite.client.data_classes import Row


def handle(data: dict[str, Any], client: CogniteClient) -> dict[str, Any]:
    """
    Main handler function for FPL data ingestion
    
    Args:
        data: Input data containing configuration
        client: CogniteClient instance
    
    Returns:
        Dictionary with status and statistics
    """
    
    # FPL API endpoints
    BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
    LEAGUE_URL_TEMPLATE = "https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    ENTRY_URL_TEMPLATE = "https://fantasy.premierleague.com/api/entry/{entry_id}/"
    ENTRY_HISTORY_TEMPLATE = "https://fantasy.premierleague.com/api/entry/{entry_id}/history/"
    PICKS_URL_TEMPLATE = "https://fantasy.premierleague.com/api/entry/{entry_id}/event/{event_id}/picks/"
    
    db_name = "fantasy_football"
    stats = {
        "teams": 0,
        "players": 0,
        "gameweeks": 0,
        "player_stats": 0,
        "leagues": 0,
        "managers": 0,
        "picks": 0
    }
    
    try:
        # 1. Fetch bootstrap-static data (players, teams, events/gameweeks)
        print("Fetching bootstrap-static data...")
        response = requests.get(BOOTSTRAP_URL)
        response.raise_for_status()
        bootstrap_data = response.json()
        
        # Process teams
        team_rows = []
        for team in bootstrap_data.get("teams", []):
            team_rows.append(Row(
                key=f"team_{team['id']}",
                columns={
                    "_type": "team",
                    "id": team["id"],
                    "name": team["name"],
                    "short_name": team["short_name"],
                    "strength": team.get("strength"),
                    "updated_at": datetime.now().isoformat()
                }
            ))
        
        if team_rows:
            client.raw.rows.insert(db_name, "fpl_bootstrap_static", team_rows)
            stats["teams"] = len(team_rows)
            print(f"Loaded {len(team_rows)} teams")
        
        # Process players
        player_rows = []
        for player in bootstrap_data.get("elements", []):
            player_rows.append(Row(
                key=f"player_{player['id']}",
                columns={
                    "_type": "player",
                    "id": player["id"],
                    "first_name": player["first_name"],
                    "second_name": player["second_name"],
                    "web_name": player["web_name"],
                    "element_type": player["element_type"],
                    "team": player["team"],
                    "now_cost": player["now_cost"],
                    "total_points": player["total_points"],
                    "points_per_game": player.get("points_per_game"),
                    "form": player.get("form"),
                    "selected_by_percent": player.get("selected_by_percent"),
                    "updated_at": datetime.now().isoformat()
                }
            ))
        
        if player_rows:
            # Insert in batches of 1000
            batch_size = 1000
            for i in range(0, len(player_rows), batch_size):
                batch = player_rows[i:i + batch_size]
                client.raw.rows.insert(db_name, "fpl_bootstrap_static", batch)
            stats["players"] = len(player_rows)
            print(f"Loaded {len(player_rows)} players")
        
        # Process events (gameweeks)
        event_rows = []
        for event in bootstrap_data.get("events", []):
            event_rows.append(Row(
                key=f"gameweek_{event['id']}",
                columns={
                    "_type": "event",
                    "id": event["id"],
                    "name": event["name"],
                    "deadline_time": event["deadline_time"],
                    "finished": event["finished"],
                    "is_current": event["is_current"],
                    "average_entry_score": event.get("average_entry_score"),
                    "highest_score": event.get("highest_score"),
                    "updated_at": datetime.now().isoformat()
                }
            ))
        
        if event_rows:
            client.raw.rows.insert(db_name, "fpl_bootstrap_static", event_rows)
            stats["gameweeks"] = len(event_rows)
            print(f"Loaded {len(event_rows)} gameweeks")
        
        # 2. Fetch detailed player gameweek stats
        print("Fetching player gameweek stats...")
        current_event = next((e for e in bootstrap_data.get("events", []) if e.get("is_current")), None)
        if current_event:
            current_gw = current_event["id"]
            player_stats_rows = []
            
            for player in bootstrap_data.get("elements", []):
                player_id = player["id"]
                # Fetch player's detailed history
                try:
                    player_url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
                    player_response = requests.get(player_url)
                    player_response.raise_for_status()
                    player_data = player_response.json()
                    
                    for history in player_data.get("history", []):
                        player_stats_rows.append(Row(
                            key=f"player_{player_id}_gw_{history['round']}",
                            columns={
                                "player_id": player_id,
                                "gameweek": history["round"],
                                "total_points": history["total_points"],
                                "minutes": history["minutes"],
                                "goals_scored": history["goals_scored"],
                                "assists": history["assists"],
                                "clean_sheets": history["clean_sheets"],
                                "goals_conceded": history["goals_conceded"],
                                "own_goals": history["own_goals"],
                                "penalties_saved": history["penalties_saved"],
                                "penalties_missed": history["penalties_missed"],
                                "yellow_cards": history["yellow_cards"],
                                "red_cards": history["red_cards"],
                                "saves": history["saves"],
                                "bonus": history["bonus"],
                                "bps": history["bps"],
                                "influence": history["influence"],
                                "creativity": history["creativity"],
                                "threat": history["threat"],
                                "ict_index": history["ict_index"],
                                "value": history["value"],
                                "transfers_in": history["transfers_in"],
                                "transfers_out": history["transfers_out"],
                                "selected": history["selected"],
                                "updated_at": datetime.now().isoformat()
                            }
                        ))
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error fetching stats for player {player_id}: {e}")
                    continue
            
            if player_stats_rows:
                # Insert in batches
                batch_size = 1000
                for i in range(0, len(player_stats_rows), batch_size):
                    batch = player_stats_rows[i:i + batch_size]
                    client.raw.rows.insert(db_name, "fpl_player_gameweek", batch)
                stats["player_stats"] = len(player_stats_rows)
                print(f"Loaded {len(player_stats_rows)} player gameweek stats")
        
        # 3. Fetch league data if league_id is provided
        league_id = data.get("league_id") or os.getenv("FPL_LEAGUE_ID")
        if league_id:
            print(f"Fetching league data for league {league_id}...")
            league_url = LEAGUE_URL_TEMPLATE.format(league_id=league_id)
            league_response = requests.get(league_url)
            league_response.raise_for_status()
            league_data = league_response.json()
            
            # Process league info
            league_info = league_data.get("league", {})
            league_row = Row(
                key=f"league_{league_id}",
                columns={
                    "league_id": league_id,
                    "name": league_info.get("name"),
                    "league_type": "classic",
                    "updated_at": datetime.now().isoformat()
                }
            )
            client.raw.rows.insert(db_name, "fpl_leagues", [league_row])
            stats["leagues"] = 1
            
            # Process manager teams and their picks
            for standing in league_data.get("standings", {}).get("results", []):
                entry_id = standing["entry"]
                
                # Fetch manager entry details
                entry_url = ENTRY_URL_TEMPLATE.format(entry_id=entry_id)
                entry_response = requests.get(entry_url)
                entry_response.raise_for_status()
                entry_data = entry_response.json()
                
                # Store manager info
                manager_row = Row(
                    key=f"manager_{entry_id}",
                    columns={
                        "entry_id": entry_id,
                        "manager_name": f"{entry_data['player_first_name']} {entry_data['player_last_name']}",
                        "team_name": entry_data["name"],
                        "league_id": league_id,
                        "overall_points": entry_data.get("summary_overall_points"),
                        "overall_rank": entry_data.get("summary_overall_rank"),
                        "updated_at": datetime.now().isoformat()
                    }
                )
                client.raw.rows.insert(db_name, "fpl_manager_picks", [manager_row])
                stats["managers"] += 1
                
                # Fetch picks for each completed gameweek
                if current_event:
                    for gw in range(1, current_gw + 1):
                        try:
                            picks_url = PICKS_URL_TEMPLATE.format(entry_id=entry_id, event_id=gw)
                            picks_response = requests.get(picks_url)
                            picks_response.raise_for_status()
                            picks_data = picks_response.json()
                            
                            entry_history = picks_data.get("entry_history", {})
                            picks_row = Row(
                                key=f"manager_{entry_id}_gw_{gw}",
                                columns={
                                    "entry_id": entry_id,
                                    "gameweek": gw,
                                    "points": entry_history.get("points"),
                                    "total_points": entry_history.get("total_points"),
                                    "rank": entry_history.get("rank"),
                                    "transfers": entry_history.get("event_transfers"),
                                    "transfer_cost": entry_history.get("event_transfers_cost"),
                                    "bank": entry_history.get("bank"),
                                    "team_value": entry_history.get("value"),
                                    "active_chip": picks_data.get("active_chip"),
                                    "picks_json": str(picks_data.get("picks", [])),
                                    "updated_at": datetime.now().isoformat()
                                }
                            )
                            client.raw.rows.insert(db_name, "fpl_manager_picks", [picks_row])
                            stats["picks"] += 1
                            
                            time.sleep(0.5)  # Rate limiting
                            
                        except Exception as e:
                            print(f"Error fetching picks for manager {entry_id} GW {gw}: {e}")
                            continue
                
                time.sleep(0.5)  # Rate limiting
        
        return {
            "status": "success",
            "message": "FPL data ingestion completed",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }

