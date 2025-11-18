# Fantasy Football Project Setup Guide

## Overview

This project fetches and analyzes Fantasy Premier League data using Cognite Data Fusion (CDF) Toolkit. The complete data pipeline includes:

1. **FPL API Ingestion** → Fetches data from Fantasy Premier League API
2. **RAW Storage** → Stores raw JSON data in CDF RAW tables
3. **Transformations** → Processes and structures the data
4. **Data Model** → Final structured data accessible via GraphQL

## Project Structure

```
fantasy-football/
├── modules/fantasy-football/          # CDF Toolkit module
│   ├── data_models/                   # Data model definitions (GraphQL schema)
│   ├── raw/                           # RAW table definitions
│   ├── transformations/               # SQL transformations (RAW → Data Model)
│   ├── functions/                     # CDF Functions for data ingestion
│   ├── workflows/                     # Workflow orchestration
│   ├── data_sets/                     # Dataset definitions
│   └── README.md                      # Module documentation
│
├── src/                               # Python source code
│   ├── fpl_client.py                  # FPL API client
│   └── __init__.py
│
├── notebooks/                         # Jupyter notebooks for exploration
│   └── explore_fpl_data.ipynb        # Data analysis notebook
│
├── config.dev.yaml                    # CDF Toolkit configuration
├── cdf.toml                           # Toolkit settings
├── pyproject.toml                     # Python dependencies
├── poetry.lock                        # Locked dependencies
└── env.template                       # Environment variables template

```

## Quick Start

### 1. Install Dependencies

```bash
# Install Python dependencies using Poetry
poetry install
```

### 2. Configure Environment

Create a `.env` file from the template:

```bash
cp env.template .env
```

Edit `.env` with your credentials:

```bash
# CDF Configuration
CDF_PROJECT=your-project-name
CDF_CLUSTER=your-cluster
CDF_CLIENT_ID=your-client-id
CDF_CLIENT_SECRET=your-client-secret
CDF_TOKEN_URL=https://login.microsoftonline.com/YOUR-TENANT-ID/oauth2/v2.0/token

# FPL Configuration
FPL_LEAGUE_ID=123456  # Your FPL league ID
```

**Finding your FPL League ID:**
1. Go to your league on https://fantasy.premierleague.com
2. Look at the URL: `https://fantasy.premierleague.com/leagues/123456/standings/c`
3. The number `123456` is your league ID

### 3. Build and Deploy

```bash
# Build the CDF configuration
poetry run cdf build

# Deploy to CDF
poetry run cdf deploy
```

This will create:
- **Space**: `fantasy_football`
- **Data Model**: `FantasyFootballDataModel`
- **RAW Database**: `fantasy_football` with 4 tables
- **Transformations**: 4 SQL transformations
- **Function**: `fpl_data_ingestion`
- **Workflow**: `daily_fpl_sync`

### 4. Run Data Ingestion

Manually trigger the first data load:

```bash
# Option 1: Run the workflow (recommended)
poetry run cdf workflow run daily_fpl_sync

# Option 2: Call the function directly
poetry run cdf function call fpl_data_ingestion --data '{"league_id": "YOUR_LEAGUE_ID"}'
```

The ingestion will:
1. Fetch all players, teams, and gameweeks from FPL API
2. Fetch detailed player stats for each gameweek
3. Fetch your league standings and manager data
4. Fetch manager picks for each gameweek
5. Store everything in RAW tables
6. Run transformations to populate the data model

**Note:** Full ingestion can take 10-30 minutes depending on data volume.

### 5. Explore the Data

#### Using Jupyter Notebook

```bash
# Start Jupyter
poetry run jupyter notebook notebooks/explore_fpl_data.ipynb
```

The notebook includes analyses for:
- Top players by total points
- Best value players (points per million)
- Team performance comparison
- Player form analysis
- Price vs performance scatter plots

#### Using GraphQL

Query the data model directly in CDF:

```graphql
query TopPlayers {
  listPlayer(
    sort: { totalPoints: DESC }
    limit: 10
  ) {
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

#### Using Python SDK

```python
from cognite.client import CogniteClient
from cognite.client.data_classes.data_modeling import NodeId

client = CogniteClient()

# Query players
result = client.data_modeling.instances.list(
    "node",
    sources=[{
        "space": "fantasy_football",
        "externalId": "FantasyFootballDataModel",
        "version": "1",
        "type": "Player"
    }],
    limit=10
)

for player in result:
    print(f"{player.properties['name']}: {player.properties['totalPoints']} points")
```

## Data Model

### Core Entities

| Entity | Description | Key Fields |
|--------|-------------|------------|
| **Player** | Individual player info | name, position, team, price, totalPoints, form |
| **Team** | Premier League teams | name, shortName, strength |
| **Gameweek** | Each week of the season | gameweekNumber, deadlineTime, isFinished, averageScore |
| **PlayerGameweekStats** | Player performance per week | player, gameweek, totalPoints, goals, assists, bonus |
| **League** | Your friend leagues | leagueId, name, leagueType |
| **ManagerTeam** | Fantasy teams | entryId, managerName, teamName, overallPoints |
| **ManagerGameweekPicks** | Manager selections per week | managerTeam, gameweek, points, transfers, picks |

### Relationships

```
Team ←─── Player ←─── PlayerGameweekStats ───→ Gameweek
                                                    ↑
League ←─── ManagerTeam ←─── ManagerGameweekPicks ─┘
```

## Automated Data Refresh

The `daily_fpl_sync` workflow runs daily at 3 AM UTC to:
1. Fetch latest data from FPL API
2. Update RAW tables
3. Run transformations to update the data model

You can modify the schedule in `modules/fantasy-football/workflows/daily_fpl_sync.yaml`.

## Testing Locally

Before deploying, you can test the FPL API integration locally:

```bash
# Test FPL client
poetry run python src/fpl_client.py

# Run in interactive Python
poetry run python
>>> from src.fpl_client import FPLClient
>>> client = FPLClient()
>>> data = client.get_bootstrap_static()
>>> print(f"Players: {len(data['elements'])}")
```

## Troubleshooting

### Build Errors

**Error: Module not found**
- Ensure `config.dev.yaml` has correct syntax: `- modules/fantasy-football` (space after hyphen)

**Error: Directory not found**
- Check `cdf.toml` has `default_organization_dir = "."`

### Deployment Errors

**Authentication failed**
- Verify `.env` credentials are correct
- Ensure service principal has necessary permissions in CDF

**Transformation errors**
- Check that RAW tables have data before running transformations
- View transformation logs in CDF

### Data Ingestion Errors

**Function timeout**
- Increase timeout in `function_config.yaml`
- Consider splitting ingestion into smaller batches

**Rate limit errors**
- Increase `time.sleep()` delay in `handler.py`
- FPL API has rate limits; respect them

**Missing gameweek data**
- Data is only available after matches finish
- Check `isFinished` field on Gameweek

## Next Steps

1. **Visualize Data**: Create Streamlit dashboard for team analysis
2. **ML Predictions**: Build models to predict player performance
3. **Transfer Advisor**: Recommend optimal transfers based on form
4. **Fixture Analysis**: Add fixture difficulty ratings
5. **Historical Analysis**: Compare current season to previous seasons

## Resources

- [CDF Toolkit Documentation](https://docs.cognite.com/cdf/deploy/cdf_toolkit/)
- [Fantasy Premier League API](https://fantasy.premierleague.com/api/bootstrap-static/)
- [Module README](modules/fantasy-football/README.md)

## Support

For issues or questions:
1. Check the module README
2. Review CDF Toolkit documentation
3. Check FPL API documentation

Happy analyzing! 🎯⚽

