"""
Weekly FPL Data Update Function
Fetches latest data from FPL API and updates the data model in CDF
"""
import os
import requests
import numpy as np
from datetime import datetime
from typing import Any
from collections import defaultdict
from cognite.client import CogniteClient
from cognite.client.data_classes.data_modeling import NodeApply, ViewId


def handle(data: dict[str, Any], client: CogniteClient) -> dict[str, Any]:
    """
    Fetch latest FPL data and update CDF data model with enhanced analytics
    """
    SPACE = "fantasy_football"
    FPL_LEAGUE_ID = data.get("league_id") or os.getenv("FPL_LEAGUE_ID", "sl9tyc")
    
    stats = {"teams": 0, "gameweeks": 0, "managers": 0, "performance": 0, "players": 0, "team_betting": 0}
    
    try:
        # 1. Fetch bootstrap data (teams, gameweeks)
        print("Fetching FPL bootstrap data...")
        response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
        response.raise_for_status()
        bootstrap = response.json()
        
        # 2. Create Team nodes
        team_nodes = []
        for team in bootstrap.get("teams", []):
            team_nodes.append(NodeApply(
                space=SPACE,
                external_id=f"team_{team['id']}",
                sources=[{
                    "source": ViewId(space=SPACE, external_id="Team", version="1"),
                    "properties": {
                        "teamId": team["id"],
                        "name": team["name"],
                        "shortName": team["short_name"],
                        "strength": team.get("strength", 0)
                    }
                }]
            ))
        
        if team_nodes:
            client.data_modeling.instances.apply(team_nodes)
            stats["teams"] = len(team_nodes)
            print(f"✓ Loaded {len(team_nodes)} teams")
        
        # 3. Create Gameweek nodes
        gameweek_nodes = []
        for event in bootstrap.get("events", []):
            gameweek_nodes.append(NodeApply(
                space=SPACE,
                external_id=f"gameweek_{event['id']}",
                sources=[{
                    "source": ViewId(space=SPACE, external_id="Gameweek", version="1"),
                    "properties": {
                        "gameweekNumber": event["id"],
                        "name": event["name"],
                        "deadline": event["deadline_time"],
                        "isFinished": event["finished"],
                        "isCurrent": event["is_current"],
                        "averageScore": event.get("average_entry_score", 0),
                        "highestScore": event.get("highest_score", 0)
                    }
                }]
            ))
        
        if gameweek_nodes:
            client.data_modeling.instances.apply(gameweek_nodes)
            stats["gameweeks"] = len(gameweek_nodes)
            print(f"✓ Loaded {len(gameweek_nodes)} gameweeks")
        
        # 4. Load Players
        print("Loading FPL players...")
        player_nodes = []
        players = bootstrap.get("elements", [])
        position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        player_team_map = {player['id']: player['team'] for player in players}
        
        for player in players:
            player_nodes.append(NodeApply(
                space=SPACE,
                external_id=f"player_{player['id']}",
                sources=[{
                    "source": ViewId(space=SPACE, external_id="Player", version="1"),
                    "properties": {
                        "playerId": player['id'],
                        "webName": player['web_name'],
                        "firstName": player['first_name'],
                        "lastName": player['second_name'],
                        "team": {"space": SPACE, "externalId": f"team_{player['team']}"},
                        "position": position_map.get(player['element_type'], "Unknown"),
                        "currentPrice": player['now_cost'] / 10.0,
                        "totalPoints": player['total_points'],
                        "form": float(player.get('form', 0)) if player.get('form') else 0.0,
                        "selectedByPercent": float(player.get('selected_by_percent', 0)) if player.get('selected_by_percent') else 0.0,
                        "pointsPerGame": float(player.get('points_per_game', 0)) if player.get('points_per_game') else 0.0
                    }
                }]
            ))
        
        if player_nodes:
            client.data_modeling.instances.apply(player_nodes)
            stats["players"] = len(player_nodes)
            print(f"✓ Loaded {len(player_nodes)} players")
        
        # 5. Fetch league standings
        print(f"Fetching league {FPL_LEAGUE_ID} standings...")
        league_response = requests.get(
            f"https://fantasy.premierleague.com/api/leagues-classic/{FPL_LEAGUE_ID}/standings/"
        )
        league_response.raise_for_status()
        league_data = league_response.json()
        
        # 6. Create Manager nodes with analytics and performance records
        manager_nodes = []
        performance_nodes = []
        
        for standing in league_data["standings"]["results"]:
            entry_id = standing["entry"]
            
            # Fetch manager history
            history_response = requests.get(
                f"https://fantasy.premierleague.com/api/entry/{entry_id}/history/"
            )
            history_response.raise_for_status()
            history_data = history_response.json()
            current_gw_data = history_data.get("current", [])
            
            # Compute analytics
            if current_gw_data:
                weekly_points = [gw['points'] for gw in current_gw_data]
                
                if len(weekly_points) > 1 and np.mean(weekly_points) > 0:
                    points_mean = float(np.mean(weekly_points))
                    points_std = float(np.std(weekly_points))
                    coeff_variation = points_std / points_mean
                    consistency_score = max(0, min(100, 100 * (1 - min(coeff_variation, 1))))
                else:
                    points_mean = float(np.mean(weekly_points)) if weekly_points else 0.0
                    points_std = 0.0
                    consistency_score = 0.0
                
                starting_value = current_gw_data[0]['value'] / 10.0
                current_value = current_gw_data[-1]['value'] / 10.0
                team_value_growth = current_value - starting_value
                total_transfers = sum(gw.get('event_transfers', 0) for gw in current_gw_data)
            else:
                points_mean = points_std = consistency_score = team_value_growth = 0.0
                total_transfers = 0
            
            # Create manager node
            manager_nodes.append(NodeApply(
                space=SPACE,
                external_id=f"manager_{entry_id}",
                sources=[{
                    "source": ViewId(space=SPACE, external_id="Manager", version="1"),
                    "properties": {
                        "entryId": entry_id,
                        "managerName": standing["player_name"],
                        "teamName": standing["entry_name"],
                        "overallPoints": history_data["current"][0]["total_points"] if history_data.get("current") else 0,
                        "overallRank": history_data["current"][0]["rank"] if history_data.get("current") else 0,
                        "leagueRank": standing["rank"],
                        "teamValue": history_data["current"][0]["value"] / 10.0 if history_data.get("current") else 0.0,
                        "consistencyScore": round(consistency_score, 2),
                        "averagePointsPerWeek": round(points_mean, 2),
                        "pointsStdDev": round(points_std, 2),
                        "teamValueGrowth": round(team_value_growth, 2),
                        "totalTransfers": total_transfers,
                        "transferSuccessRate": 0.0,  # Would require transfer analysis
                        "successfulTransfers": 0
                    }
                }]
            ))
            
            # Create performance records for each gameweek
            for gw_data in history_data.get("current", []):
                performance_nodes.append(NodeApply(
                    space=SPACE,
                    external_id=f"perf_{entry_id}_gw_{gw_data['event']}",
                    sources=[{
                        "source": ViewId(space=SPACE, external_id="ManagerGameweekPerformance", version="1"),
                        "properties": {
                            "manager": {"space": SPACE, "externalId": f"manager_{entry_id}"},
                            "gameweek": {"space": SPACE, "externalId": f"gameweek_{gw_data['event']}"},
                            "points": gw_data["points"],
                            "totalPoints": gw_data["total_points"],
                            "gameweekRank": gw_data["rank"],
                            "overallRank": gw_data.get("overall_rank", 0),
                            "transfers": gw_data.get("event_transfers", 0),
                            "transferCost": gw_data.get("event_transfers_cost", 0),
                            "teamValue": gw_data["value"] / 10.0,
                            "bank": gw_data["bank"] / 10.0
                        }
                    }]
                ))
        
        if manager_nodes:
            client.data_modeling.instances.apply(manager_nodes)
            stats["managers"] = len(manager_nodes)
            print(f"✓ Loaded {len(manager_nodes)} managers")
        
        if performance_nodes:
            client.data_modeling.instances.apply(performance_nodes)
            stats["performance"] = len(performance_nodes)
            print(f"✓ Loaded {len(performance_nodes)} performance records")
        
        return {
            "status": "success",
            "message": "FPL data updated successfully",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }

