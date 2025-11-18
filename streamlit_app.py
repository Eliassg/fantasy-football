"""
Fantasy Football Analytics Dashboard
Streamlit app for visualizing FPL data from CDF
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from cognite.client import CogniteClient
from cognite.client.config import ClientConfig
from cognite.client.credentials import OAuthClientCredentials
from cognite.client.data_classes.data_modeling.ids import ViewId

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Fantasy Football Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #37003c;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize CDF client
@st.cache_resource
def get_cdf_client():
    """Initialize and return CDF client"""
    cluster = os.getenv("CDF_CLUSTER", "bluefield")
    project = os.getenv("CDF_PROJECT", "sofie-prod")
    base_url = os.getenv("CDF_BASE_URL", f"https://{cluster}.cognitedata.com")
    token_url = os.getenv("CDF_TOKEN_URL")
    client_id = os.getenv("CDF_CLIENT_ID")
    client_secret = os.getenv("CDF_CLIENT_SECRET")
    
    creds = OAuthClientCredentials(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        scopes=[f"{base_url}/.default"],
    )
    
    cnf = ClientConfig(
        client_name="fpl-streamlit-app",
        project=project,
        credentials=creds,
        base_url=base_url,
    )
    
    return CogniteClient(cnf)

# Fetch data functions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_managers(_client):
    """Fetch all managers from CDF"""
    try:
        # Query with ViewId to get properties populated
        manager_view = ViewId(space="fantasy_football", external_id="Manager", version="1")
        nodes = _client.data_modeling.instances.list(
            instance_type="node",
            sources=[manager_view],
            limit=100
        )
        
        managers = []
        for node in nodes:
            if hasattr(node, 'properties'):
                props_dict = node.properties.dump() if hasattr(node.properties, 'dump') else node.properties
                props = props_dict.get("fantasy_football", {}).get("Manager/1", {})
                if props:
                    managers.append({
                        "external_id": node.external_id,
                        "entry_id": props.get("entryId"),
                        "manager_name": props.get("managerName", "Unknown"),
                        "team_name": props.get("teamName", ""),
                        "overall_points": props.get("overallPoints", 0),
                        "overall_rank": props.get("overallRank", 0),
                        "league_rank": props.get("leagueRank", 0),
                        "team_value": props.get("teamValue", 0),
                        "consistency_score": props.get("consistencyScore", 0),
                        "avg_points_per_week": props.get("averagePointsPerWeek", 0),
                        "points_std_dev": props.get("pointsStdDev", 0),
                        "team_value_growth": props.get("teamValueGrowth", 0),
                        "total_transfers": props.get("totalTransfers", 0)
                    })
        
        return pd.DataFrame(managers)
    except Exception as e:
        st.error(f"Error fetching managers: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_performance_data(_client, manager_external_id):
    """Fetch gameweek performance for a manager"""
    try:
        perf_view = ViewId(space="fantasy_football", external_id="ManagerGameweekPerformance", version="1")
        nodes = _client.data_modeling.instances.list(
            instance_type="node",
            sources=[perf_view],
            limit=1000
        )
        
        performance = []
        for node in nodes:
            if node.external_id.startswith(f"perf_{manager_external_id.split('_')[1]}_") and hasattr(node, 'properties'):
                props_dict = node.properties.dump() if hasattr(node.properties, 'dump') else node.properties
                props = props_dict.get("fantasy_football", {}).get("ManagerGameweekPerformance/1", {})
                if props:
                    gw_num = node.external_id.split("_gw")[-1]
                    performance.append({
                        "gameweek": int(gw_num) if gw_num.isdigit() else 0,
                        "points": props.get("points", 0),
                        "total_points": props.get("totalPoints", 0),
                        "rank": props.get("overallRank", 0),
                        "transfers": props.get("transfers", 0),
                        "transfer_cost": props.get("transferCost", 0)
                    })
        
        df = pd.DataFrame(performance)
        if not df.empty:
            df = df.sort_values("gameweek")
        return df
    except Exception as e:
        st.error(f"Error fetching performance data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_team_betting_data(_client):
    """Fetch team betting patterns"""
    try:
        betting_view = ViewId(space="fantasy_football", external_id="ManagerTeamBetting", version="1")
        nodes = _client.data_modeling.instances.list(
            instance_type="node",
            sources=[betting_view],
            limit=1000
        )
        
        betting_data = []
        for node in nodes:
            if hasattr(node, 'properties'):
                props_dict = node.properties.dump() if hasattr(node.properties, 'dump') else node.properties
                props = props_dict.get("fantasy_football", {}).get("ManagerTeamBetting/1", {})
                if props:
                    # Extract IDs from relations
                    manager_id = props.get("manager", {}).get("externalId", "")
                    team_id = props.get("team", {}).get("externalId", "")
                    
                    betting_data.append({
                        "manager_id": manager_id,
                        "team_id": team_id,
                        "total_players_used": props.get("totalPlayersUsed", 0),
                        "total_points": props.get("totalPoints", 0),
                        "avg_points_per_player": props.get("averagePointsPerPlayer", 0),
                        "success_rate": props.get("successRate", 0)
                    })
        
        return pd.DataFrame(betting_data)
    except Exception as e:
        st.error(f"Error fetching team betting data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_teams(_client):
    """Fetch Premier League teams"""
    try:
        team_view = ViewId(space="fantasy_football", external_id="Team", version="1")
        nodes = _client.data_modeling.instances.list(
            instance_type="node",
            sources=[team_view],
            limit=100
        )
        
        teams = {}
        for node in nodes:
            if hasattr(node, 'properties'):
                props_dict = node.properties.dump() if hasattr(node.properties, 'dump') else node.properties
                props = props_dict.get("fantasy_football", {}).get("Team/1", {})
                if props:
                    teams[node.external_id] = props.get("name", "Unknown Team")
        
        return teams
    except Exception as e:
        st.error(f"Error fetching teams: {e}")
        return {}

@st.cache_data(ttl=3600)
def fetch_transfer_data(_client):
    """Fetch transfer data with success metrics"""
    try:
        transfer_view = ViewId(space="fantasy_football", external_id="Transfer", version="1")
        nodes = _client.data_modeling.instances.list(
            instance_type="node",
            sources=[transfer_view],
            limit=2000
        )
        
        transfers = []
        for node in nodes:
            if hasattr(node, 'properties'):
                props_dict = node.properties.dump() if hasattr(node.properties, 'dump') else node.properties
                props = props_dict.get("fantasy_football", {}).get("Transfer/1", {})
                if props:
                    # Extract IDs from relations
                    manager_id = props.get("manager", {}).get("externalId", "")
                    gameweek_id = props.get("gameweek", {}).get("externalId", "")
                    player_in_id = props.get("playerIn", {}).get("externalId", "")
                    player_out_id = props.get("playerOut", {}).get("externalId", "")
                    
                    # Extract gameweek number from gameweek_id
                    gw_num = gameweek_id.split("_")[-1] if gameweek_id else "0"
                    
                    transfers.append({
                        "external_id": node.external_id,
                        "manager_id": manager_id,
                        "gameweek": int(gw_num) if gw_num.isdigit() else 0,
                        "player_in_id": player_in_id,
                        "player_out_id": player_out_id,
                        "transfer_cost": props.get("transferCost", 0),
                        "player_in_price": props.get("playerInPrice", 0),
                        "player_out_price": props.get("playerOutPrice", 0),
                        "points_gained_next_3gw": props.get("pointsGainedNext3GW", 0),
                        "was_successful": props.get("wasSuccessful", False),
                        "net_benefit": props.get("netBenefit", 0)
                    })
        
        return pd.DataFrame(transfers)
    except Exception as e:
        st.error(f"Error fetching transfer data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_players(_client):
    """Fetch player data"""
    try:
        player_view = ViewId(space="fantasy_football", external_id="Player", version="1")
        nodes = _client.data_modeling.instances.list(
            instance_type="node",
            sources=[player_view],
            limit=1000
        )
        
        players = {}
        for node in nodes:
            if hasattr(node, 'properties'):
                props_dict = node.properties.dump() if hasattr(node.properties, 'dump') else node.properties
                props = props_dict.get("fantasy_football", {}).get("Player/1", {})
                if props:
                    players[node.external_id] = {
                        "name": props.get("webName", "Unknown"),
                        "full_name": props.get("fullName", ""),
                        "team_id": props.get("team", {}).get("externalId", ""),
                        "position": props.get("elementType", "")
                    }
        
        return players
    except Exception as e:
        st.error(f"Error fetching players: {e}")
        return {}

# Main app
def main():
    st.markdown('<h1 class="main-header">⚽ Fantasy Football Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize client
    try:
        client = get_cdf_client()
        st.sidebar.success(f"✓ Connected to CDF: {client.config.project}")
    except Exception as e:
        st.error(f"Failed to connect to CDF: {e}")
        st.info("Please check your .env file and credentials")
        return
    
    # Fetch data
    with st.spinner("Loading data from CDF..."):
        managers_df = fetch_managers(client)
        teams_dict = fetch_teams(client)
    
    if managers_df.empty:
        st.warning("No manager data found. Please run the notebook to load data first.")
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_managers = st.sidebar.multiselect(
        "Select Managers",
        options=managers_df["manager_name"].tolist(),
        default=managers_df["manager_name"].tolist()[:5]
    )
    
    # Filter data
    filtered_df = managers_df[managers_df["manager_name"].isin(selected_managers)]
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Leaderboard", 
        "📈 Performance Trends", 
        "🔄 Transfer Analysis",
        "🎯 Team Betting", 
        "💎 Consistency Analysis"
    ])
    
    # TAB 1: Leaderboard
    with tab1:
        st.header("League Leaderboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Managers",
                len(managers_df),
                help="Number of managers in your league"
            )
        
        with col2:
            st.metric(
                "Highest Points",
                f"{managers_df['overall_points'].max():,.0f}",
                help="Highest total points"
            )
        
        with col3:
            st.metric(
                "Most Consistent",
                managers_df.loc[managers_df['consistency_score'].idxmax(), 'manager_name'],
                f"{managers_df['consistency_score'].max():.1f} score"
            )
        
        with col4:
            st.metric(
                "Best Value Growth",
                managers_df.loc[managers_df['team_value_growth'].idxmax(), 'manager_name'],
                f"£{managers_df['team_value_growth'].max():.1f}m"
            )
        
        # Main leaderboard table
        st.subheader("Rankings")
        display_df = managers_df.sort_values("overall_points", ascending=False)[
            ["league_rank", "manager_name", "team_name", "overall_points", 
             "team_value", "consistency_score", "avg_points_per_week", "total_transfers"]
        ].copy()
        
        display_df.columns = ["Rank", "Manager", "Team", "Points", "Value (£m)", 
                              "Consistency", "Avg PPW", "Transfers"]
        
        st.dataframe(
            display_df.style.format({
                "Points": "{:,.0f}",
                "Value (£m)": "£{:.1f}m",
                "Consistency": "{:.1f}",
                "Avg PPW": "{:.1f}",
                "Transfers": "{:.0f}"
            }).background_gradient(subset=["Points"], cmap="Greens"),
            use_container_width=True,
            height=400
        )
        
        # Points distribution
        st.subheader("Points Distribution")
        fig = px.bar(
            managers_df.sort_values("overall_points", ascending=False),
            x="manager_name",
            y="overall_points",
            color="consistency_score",
            color_continuous_scale="RdYlGn",
            labels={"overall_points": "Total Points", "manager_name": "Manager", 
                   "consistency_score": "Consistency Score"},
            title="Total Points by Manager (colored by consistency)"
        )
        fig.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 2: Performance Trends
    with tab2:
        st.header("Weekly Performance Trends")
        
        if not selected_managers:
            st.info("Select managers from the sidebar to view their performance")
        else:
            # Fetch performance data for selected managers
            all_performance = []
            for manager_name in selected_managers:
                manager_row = managers_df[managers_df["manager_name"] == manager_name].iloc[0]
                perf_df = fetch_performance_data(client, manager_row["external_id"])
                if not perf_df.empty:
                    perf_df["manager"] = manager_name
                    all_performance.append(perf_df)
            
            if all_performance:
                combined_df = pd.concat(all_performance, ignore_index=True)
                
                # Weekly points trend
                fig = px.line(
                    combined_df,
                    x="gameweek",
                    y="points",
                    color="manager",
                    markers=True,
                    title="Points Per Gameweek",
                    labels={"points": "Points", "gameweek": "Gameweek", "manager": "Manager"}
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Cumulative points
                    fig = px.line(
                        combined_df,
                        x="gameweek",
                        y="total_points",
                        color="manager",
                        markers=True,
                        title="Cumulative Points",
                        labels={"total_points": "Total Points", "gameweek": "Gameweek"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Transfer activity
                    fig = px.bar(
                        combined_df,
                        x="gameweek",
                        y="transfers",
                        color="manager",
                        barmode="group",
                        title="Transfer Activity",
                        labels={"transfers": "Transfers Made", "gameweek": "Gameweek"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No performance data available for selected managers")
    
    # TAB 3: Transfer Analysis
    with tab3:
        st.header("Transfer Success Analysis")
        st.write("Comparing points from transferred-in players vs transferred-out players")
        
        transfer_df = fetch_transfer_data(client)
        players_dict = fetch_players(client)
        
        if not transfer_df.empty and not filtered_df.empty:
            # Map manager IDs to names
            manager_id_to_name = dict(zip(managers_df["external_id"], managers_df["manager_name"]))
            transfer_df["manager_name"] = transfer_df["manager_id"].map(manager_id_to_name)
            
            # Map player IDs to names
            transfer_df["player_in_name"] = transfer_df["player_in_id"].map(lambda x: players_dict.get(x, {}).get("name", "Unknown"))
            transfer_df["player_out_name"] = transfer_df["player_out_id"].map(lambda x: players_dict.get(x, {}).get("name", "Unknown"))
            
            # Filter for selected managers
            transfer_filtered = transfer_df[transfer_df["manager_name"].isin(selected_managers)]
            
            if not transfer_filtered.empty:
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_transfers = len(transfer_filtered)
                    st.metric(
                        "Total Transfers",
                        total_transfers,
                        help="Total transfers made by selected managers"
                    )
                
                with col2:
                    successful_transfers = transfer_filtered["was_successful"].sum()
                    success_rate = (successful_transfers / total_transfers * 100) if total_transfers > 0 else 0
                    st.metric(
                        "Successful Transfers",
                        f"{successful_transfers}",
                        f"{success_rate:.1f}% success rate"
                    )
                
                with col3:
                    avg_net_benefit = transfer_filtered["net_benefit"].mean()
                    st.metric(
                        "Avg Net Benefit",
                        f"{avg_net_benefit:.1f} pts",
                        help="Average point difference (player in - player out)"
                    )
                
                with col4:
                    total_cost = transfer_filtered["transfer_cost"].sum()
                    st.metric(
                        "Total Cost",
                        f"{total_cost} pts",
                        help="Total points lost to transfer costs"
                    )
                
                # Transfer success by manager
                st.subheader("Transfer Success by Manager")
                manager_transfer_stats = transfer_filtered.groupby("manager_name").agg({
                    "was_successful": ["sum", "count"],
                    "net_benefit": "sum",
                    "transfer_cost": "sum"
                }).round(2)
                
                manager_transfer_stats.columns = ["Successful", "Total", "Total Benefit", "Total Cost"]
                manager_transfer_stats["Success Rate %"] = (
                    manager_transfer_stats["Successful"] / manager_transfer_stats["Total"] * 100
                ).round(1)
                manager_transfer_stats["Net Gain"] = (
                    manager_transfer_stats["Total Benefit"] - manager_transfer_stats["Total Cost"]
                ).round(1)
                
                manager_transfer_stats = manager_transfer_stats.sort_values("Success Rate %", ascending=False)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        name='Successful',
                        x=manager_transfer_stats.index,
                        y=manager_transfer_stats["Successful"],
                        marker_color='green'
                    ))
                    fig.add_trace(go.Bar(
                        name='Unsuccessful',
                        x=manager_transfer_stats.index,
                        y=manager_transfer_stats["Total"] - manager_transfer_stats["Successful"],
                        marker_color='red'
                    ))
                    fig.update_layout(
                        barmode='stack',
                        title="Transfer Success by Manager",
                        xaxis_title="Manager",
                        yaxis_title="Number of Transfers",
                        xaxis_tickangle=-45,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.dataframe(
                        manager_transfer_stats[["Total", "Success Rate %", "Net Gain"]].style.format({
                            "Success Rate %": "{:.1f}%",
                            "Net Gain": "{:.0f}"
                        }).background_gradient(subset=["Success Rate %"], cmap="RdYlGn"),
                        height=400
                    )
                
                # Recent transfers
                st.subheader("Recent Transfers")
                recent_transfers = transfer_filtered.sort_values("gameweek", ascending=False).head(20)
                
                display_transfers = recent_transfers[[
                    "manager_name", "gameweek", "player_out_name", "player_in_name",
                    "net_benefit", "was_successful"
                ]].copy()
                
                display_transfers.columns = [
                    "Manager", "GW", "Player Out", "Player In", "Net Benefit", "Success"
                ]
                
                # Add visual indicators
                display_transfers["Success"] = display_transfers["Success"].apply(
                    lambda x: "✅" if x else "❌"
                )
                
                st.dataframe(
                    display_transfers.style.format({"Net Benefit": "{:.0f}"}).apply(
                        lambda x: ['background-color: #d4edda' if v == "✅" else 'background-color: #f8d7da' 
                                   for v in x], subset=["Success"]
                    ),
                    use_container_width=True,
                    height=400
                )
                
                # Net benefit distribution
                st.subheader("Transfer Net Benefit Distribution")
                fig = px.histogram(
                    transfer_filtered,
                    x="net_benefit",
                    nbins=30,
                    title="Distribution of Transfer Net Benefits",
                    labels={"net_benefit": "Net Benefit (points)", "count": "Number of Transfers"},
                    color_discrete_sequence=["#38003c"]
                )
                fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Break-even")
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("No transfer data available for selected managers")
        else:
            st.warning("⚠️ No transfer data found in CDF. Please run the transfer analysis in the notebook first.")
            st.info("""
            **To enable transfer analysis:**
            1. Open `notebooks/load_fpl_to_cdf.ipynb`
            2. Run the transfer analysis cells to fetch and calculate transfer success metrics
            3. Refresh this dashboard
            """)
    
    # TAB 4: Team Betting
    with tab4:
        st.header("Team Selection Patterns")
        st.write("Which Premier League teams do managers pick players from?")
        
        betting_df = fetch_team_betting_data(client)
        
        if not betting_df.empty and not filtered_df.empty:
            # Map team IDs to names
            betting_df["team_name"] = betting_df["team_id"].map(teams_dict)
            
            # Map manager IDs to names
            manager_id_to_name = dict(zip(managers_df["external_id"], managers_df["manager_name"]))
            betting_df["manager_name"] = betting_df["manager_id"].map(manager_id_to_name)
            
            # Filter for selected managers
            betting_filtered = betting_df[betting_df["manager_name"].isin(selected_managers)]
            
            if not betting_filtered.empty:
                # Team usage heatmap
                pivot = betting_filtered.pivot_table(
                    index="manager_name",
                    columns="team_name",
                    values="total_points",
                    aggfunc="sum",
                    fill_value=0
                )
                
                fig = px.imshow(
                    pivot,
                    labels=dict(x="Team", y="Manager", color="Total Points"),
                    title="Points from Each Team by Manager",
                    color_continuous_scale="YlOrRd",
                    aspect="auto"
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top teams by success rate
                    team_success = betting_filtered.groupby("team_name").agg({
                        "success_rate": "mean",
                        "total_points": "sum",
                        "total_players_used": "sum"
                    }).sort_values("success_rate", ascending=False).head(10)
                    
                    fig = px.bar(
                        team_success.reset_index(),
                        x="team_name",
                        y="success_rate",
                        title="Top 10 Teams by Success Rate",
                        labels={"success_rate": "Success Rate (%)", "team_name": "Team"}
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Points per team
                    team_points = betting_filtered.groupby("team_name")["total_points"].sum().sort_values(ascending=False).head(10)
                    
                    fig = px.bar(
                        team_points.reset_index(),
                        x="team_name",
                        y="total_points",
                        title="Top 10 Teams by Total Points",
                        labels={"total_points": "Total Points", "team_name": "Team"}
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No team betting data available for selected managers")
        else:
            st.info("No team betting data available. Run the team betting analysis in the notebook first.")
    
    # TAB 5: Consistency Analysis
    with tab5:
        st.header("Consistency Analysis")
        st.write("Who's the most reliable week-to-week performer?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Consistency score distribution
            fig = px.scatter(
                managers_df,
                x="avg_points_per_week",
                y="points_std_dev",
                size="overall_points",
                color="consistency_score",
                hover_data=["manager_name", "team_name"],
                color_continuous_scale="RdYlGn",
                title="Consistency: Average vs Volatility",
                labels={
                    "avg_points_per_week": "Average Points Per Week",
                    "points_std_dev": "Points Standard Deviation",
                    "consistency_score": "Consistency Score"
                }
            )
            fig.add_annotation(
                text="Lower std dev = More consistent",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="gray")
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Team value growth
            fig = px.scatter(
                managers_df,
                x="total_transfers",
                y="team_value_growth",
                size="overall_points",
                color="consistency_score",
                hover_data=["manager_name", "team_name"],
                color_continuous_scale="RdYlGn",
                title="Transfers vs Team Value Growth",
                labels={
                    "total_transfers": "Total Transfers Made",
                    "team_value_growth": "Team Value Growth (£m)",
                    "consistency_score": "Consistency Score"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top performers in different categories
        st.subheader("Category Leaders")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🎯 Most Consistent**")
            top_consistent = managers_df.nlargest(5, "consistency_score")[["manager_name", "consistency_score"]]
            for idx, row in top_consistent.iterrows():
                st.write(f"{row['manager_name']}: {row['consistency_score']:.1f}")
        
        with col2:
            st.markdown("**📈 Best Value Growth**")
            top_growth = managers_df.nlargest(5, "team_value_growth")[["manager_name", "team_value_growth"]]
            for idx, row in top_growth.iterrows():
                st.write(f"{row['manager_name']}: £{row['team_value_growth']:.1f}m")
        
        with col3:
            st.markdown("**⚡ Highest Average PPW**")
            top_avg = managers_df.nlargest(5, "avg_points_per_week")[["manager_name", "avg_points_per_week"]]
            for idx, row in top_avg.iterrows():
                st.write(f"{row['manager_name']}: {row['avg_points_per_week']:.1f}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"**Data from CDF Project:** {client.config.project} | "
        f"**Space:** fantasy_football | "
        f"**Last refreshed:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"
    )

if __name__ == "__main__":
    main()

