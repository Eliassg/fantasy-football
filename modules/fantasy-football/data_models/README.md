# Fantasy Football Data Models

This module uses RAW tables and Transformations to load FPL data into CDF.

Due to limitations with the current CDF Toolkit version and GraphQL schema support,
the data model views will need to be created manually in the CDF UI or using the SDK
after the initial deployment.

## Manual Setup After Deployment

After running `cdf deploy`, you can:

1. Create containers and views in CDF UI for:
   - Player
   - Team
   - Gameweek
   - PlayerGameweekStats
   - League
   - ManagerTeam
   - ManagerGameweekPicks

2. The transformations are already configured to write to these views once they exist.

## Alternative: Using RAW Data Directly

For now, you can query the RAW tables directly:
- `fantasy_football.fpl_bootstrap_static` - Players, teams, gameweeks
- `fantasy_football.fpl_player_gameweek` - Player stats per gameweek
- `fantasy_football.fpl_leagues` - League information
- `fantasy_football.fpl_manager_picks` - Manager picks per gameweek

The transformations SQL files in the `transformations/` directory show the expected schema.


