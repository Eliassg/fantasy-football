# Fantasy Premier League Module

This module provides a complete data pipeline for fetching, storing, and analyzing Fantasy Premier League (FPL) data in Cognite Data Fusion.

## Overview

The module tracks:
- **Players**: Individual player information including stats, position, price, and form
- **Teams**: Premier League teams
- **Gameweeks**: Each week of the season with deadlines and scores
- **Player Gameweek Stats**: Detailed performance metrics for each player each week
- **Leagues**: Your friend leagues
- **Manager Teams**: Fantasy teams owned by managers in your leagues
- **Manager Gameweek Picks**: Team selections and performance week by week

## Architecture

```
Fantasy Premier League API
         ↓
    [Functions]         ← Fetches data from FPL API
         ↓
      [RAW]             ← Stores raw JSON data
         ↓
  [Transformations]     ← Processes and structures data
         ↓
   [Data Model]         ← Final structured data (Containers & Views)
```

## Directory Structure

```
modules/fantasy-football/
├── data_models/              # Data model definitions
│   ├── fantasy_football_space.yaml
│   ├── fantasy_football_datamodel.yaml
│   └── fantasy_football_datamodel.graphql
├── raw/                      # RAW table definitions
│   ├── raw_fpl_bootstrap.yaml
│   ├── raw_fpl_player_gameweek.yaml
│   ├── raw_fpl_leagues.yaml
│   └── raw_fpl_manager_picks.yaml
├── transformations/          # SQL transformations
│   ├── 01_load_teams/
│   ├── 02_load_players/
│   ├── 03_load_gameweeks/
│   └── 04_load_player_gameweek_stats/
├── functions/                # CDF Functions
│   └── fpl_data_ingestion/
└── workflows/                # Workflow definitions
    └── daily_fpl_sync.yaml
```

## Data Model

### Core Entities

#### Player
- Basic info: name, position, team
- Current stats: price, total points, form
- Performance tracking through gameweek stats

#### Team
- Premier League team information
- Links to all players in the team

#### Gameweek
- Week number and name
- Deadline times
- Average and highest scores
- Status (current, finished)

#### PlayerGameweekStats
- Detailed performance metrics per player per week
- Goals, assists, clean sheets
- Bonus points, BPS, ICT index
- Transfer statistics

#### League
- Your friend leagues from FPL
- Links to all manager teams

#### ManagerTeam
- Fantasy teams owned by managers
- Overall points and rank
- Weekly performance tracking

#### ManagerGameweekPicks
- Team selections each week
- Points scored
- Transfers made
- Active chips used

## Setup

### 1. Configure Your League

Set your FPL league ID in `config.dev.yaml`:

```yaml
environment:
  name: dev
  project: your-project
  selected:
    - modules/fantasy-football
  variables:
    fpl_league_id: "YOUR_LEAGUE_ID"  # Add this
```

To find your league ID:
1. Go to your league on Fantasy Premier League website
2. Look at the URL: `https://fantasy.premierleague.com/leagues/123456/standings/c`
3. The number (123456) is your league ID

### 2. Deploy the Module

```bash
# Build the configuration
poetry run cdf build

# Deploy to CDF
poetry run cdf deploy
```

### 3. Run Data Ingestion

The workflow `daily_fpl_sync` is configured to run daily at 3 AM UTC. You can also trigger it manually:

```bash
poetry run cdf workflow run daily_fpl_sync
```

Or call the function directly:

```bash
poetry run cdf function call fpl_data_ingestion --data '{"league_id": "YOUR_LEAGUE_ID"}'
```

## Usage Examples

### Query Player Stats

```graphql
query {
  listPlayer {
    items {
      name
      position
      currentPrice
      totalPoints
      form
      team {
        name
      }
    }
  }
}
```

### Get Top Performers This Gameweek

```graphql
query {
  listPlayerGameweekStats(
    filter: { gameweek: { gameweekNumber: { eq: 10 } } }
    sort: { totalPoints: DESC }
    limit: 10
  ) {
    items {
      player {
        name
        team {
          name
        }
      }
      totalPoints
      goalsScored
      assists
      bonus
    }
  }
}
```

### Track Your League Performance

```graphql
query {
  listManagerTeam(filter: { league: { leagueId: { eq: YOUR_LEAGUE_ID } } }) {
    items {
      teamName
      managerName
      overallPoints
      overallRank
      gameweekPicks {
        gameweek {
          gameweekNumber
        }
        points
        rank
      }
    }
  }
}
```

## FPL API Endpoints Used

- `bootstrap-static`: Player, team, and gameweek data
- `element-summary/{player_id}`: Detailed player history
- `leagues-classic/{league_id}/standings`: League standings
- `entry/{entry_id}`: Manager team details
- `entry/{entry_id}/event/{event_id}/picks`: Manager picks per gameweek

## Rate Limiting

The ingestion function includes rate limiting (0.5s between requests) to respect FPL API limits. Full ingestion may take several minutes depending on:
- Number of players (~600+)
- Number of gameweeks completed
- Number of managers in your league

## Data Refresh

- **Daily sync** (3 AM UTC): Updates all current data
- **Manual trigger**: For immediate updates after gameweeks
- **Incremental**: Only fetches new data where possible

## Troubleshooting

### Function timeout
If the function times out during player stats fetching, you can:
1. Increase the function timeout in `function_config.yaml`
2. Split the ingestion into multiple functions

### API rate limits
If you hit rate limits, increase the `time.sleep()` duration in `handler.py`

### Missing gameweek data
Gameweek stats are only available after matches are completed. Check the `isFinished` field on Gameweek entities.

## Future Enhancements

Potential additions:
- [ ] Fixture difficulty ratings
- [ ] Player injury status tracking
- [ ] Transfer recommendations based on form
- [ ] Head-to-head league support
- [ ] Historical season comparisons
- [ ] Predicted points using ML
- [ ] Streamlit dashboard for visualization

## Contributing

Feel free to extend this module with additional features or analytics!

