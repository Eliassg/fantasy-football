"""
Configuration and Constants for Fantasy Football Dashboard
"""

# Premier League Team Colors (official colors)
PREMIER_LEAGUE_COLORS = {
    "Arsenal": {"primary": "#EF0107", "secondary": "#FFFFFF"},
    "Aston Villa": {"primary": "#670E36", "secondary": "#95BFE5"},
    "Bournemouth": {"primary": "#DA291C", "secondary": "#000000"},
    "Brentford": {"primary": "#E30613", "secondary": "#FBB800"},
    "Brighton": {"primary": "#0057B8", "secondary": "#FFCD00"},
    "Chelsea": {"primary": "#034694", "secondary": "#FFFFFF"},
    "Crystal Palace": {"primary": "#1B458F", "secondary": "#C4122E"},
    "Everton": {"primary": "#003399", "secondary": "#FFFFFF"},
    "Fulham": {"primary": "#FFFFFF", "secondary": "#CC0000"},
    "Liverpool": {"primary": "#C8102E", "secondary": "#00B2A9"},
    "Man City": {"primary": "#6CABDD", "secondary": "#1C2C5B"},
    "Man Utd": {"primary": "#DA291C", "secondary": "#FBE122"},
    "Newcastle": {"primary": "#241F20", "secondary": "#FFFFFF"},
    "Nott'm Forest": {"primary": "#DD0000", "secondary": "#FFFFFF"},
    "Spurs": {"primary": "#132257", "secondary": "#FFFFFF"},
    "West Ham": {"primary": "#7A263A", "secondary": "#1BB1E7"},
    "Wolves": {"primary": "#FDB913", "secondary": "#231F20"},
    "Leicester": {"primary": "#003090", "secondary": "#FDBE11"},
    "Leeds": {"primary": "#FFCD00", "secondary": "#1D428A"},
    "Southampton": {"primary": "#D71920", "secondary": "#130C0E"},
    "Ipswich": {"primary": "#0033A0", "secondary": "#FFFFFF"},
    "Luton": {"primary": "#F78F1E", "secondary": "#002D62"}
}

# Custom CSS - Dark Modern Theme
CUSTOM_CSS = """
<style>
    /* Import Google Fonts - Modern sans-serif */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* CSS Variables for consistent theming */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-tertiary: #1a1a24;
        --bg-card: #16161f;
        --bg-hover: #1f1f2a;
        --accent-primary: #00e676;
        --accent-secondary: #00bfa5;
        --accent-glow: rgba(0, 230, 118, 0.15);
        --text-primary: #f0f0f5;
        --text-secondary: #a0a0b0;
        --text-muted: #6a6a7a;
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-accent: rgba(0, 230, 118, 0.3);
    }
    
    /* Main App Background - Clean solid dark */
    .stApp {
        background-color: var(--bg-primary);
    }
    
    .main {
        background-color: transparent;
        font-family: 'Outfit', sans-serif;
    }
    
    .main * {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Hero Section - Sleek minimal design */
    .hero-banner {
        background: var(--bg-secondary);
        padding: 3rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid var(--border-subtle);
        position: relative;
        overflow: hidden;
    }
    
    .hero-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
        opacity: 0.5;
    }
    
    .hero-title {
        color: var(--text-primary);
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    /* Mobile responsiveness */
    @media screen and (max-width: 768px) {
        .hero-banner {
            padding: 2rem 1.5rem;
        }
        
        .hero-title {
            font-size: 1.8rem;
        }
        
        .hero-subtitle {
            font-size: 0.95rem;
        }
    }
    
    @media screen and (max-width: 480px) {
        .hero-banner {
            padding: 1.5rem 1rem;
        }
        
        .hero-title {
            font-size: 1.4rem;
        }
        
        .hero-subtitle {
            font-size: 0.85rem;
        }
    }
    
    /* Stats Cards */
    .metric-card {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid var(--border-subtle);
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        background: var(--bg-hover);
        border-color: var(--border-accent);
    }
    
    /* Tabs Styling - Clean dark pills */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--bg-secondary);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-subtle);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 2.75rem;
        font-size: 0.9rem;
        font-weight: 500;
        background-color: transparent;
        border-radius: 8px;
        padding: 0 1.25rem;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"] button,
    .stTabs [data-baseweb="tab"] p {
        color: var(--text-secondary) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--bg-hover);
    }
    
    .stTabs [data-baseweb="tab"]:hover button,
    .stTabs [data-baseweb="tab"]:hover p {
        color: var(--text-primary) !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--accent-primary);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] button,
    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: var(--bg-primary) !important;
        font-weight: 600;
    }
    
    /* Tab content area */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }
    
    /* Team Badge */
    .team-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        color: white;
        margin: 0.2rem;
        font-size: 0.85rem;
        transition: transform 0.2s ease;
    }
    
    .team-badge:hover {
        transform: translateY(-2px);
    }
    
    /* Metric Containers */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        padding: 1rem 1.25rem;
        border-radius: 12px;
        border: 1px solid var(--border-subtle);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--accent-primary) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 500;
        color: var(--text-secondary) !important;
        font-size: 0.9rem;
    }
    
    [data-testid="stMetricDelta"] {
        color: var(--text-muted) !important;
    }
    
    /* Headings */
    h1 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        font-size: 2.2rem !important;
    }
    
    h2 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px;
    }
    
    h3 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    h4, h5, h6 {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    
    /* Paragraphs and text */
    p, span, div, label {
        color: var(--text-secondary);
    }
    
    /* Links */
    a {
        color: var(--accent-primary) !important;
    }
    
    a:hover {
        color: var(--accent-secondary) !important;
    }
    
    /* Data Tables - Let Streamlit's native dark theme handle dataframes */
    /* Only style static HTML tables */
    .stTable table,
    table.dataframe {
        background: #16161f !important;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stTable th,
    table.dataframe th {
        background: #1a1a24 !important;
        color: #f0f0f5 !important;
        font-weight: 600;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stTable td,
    table.dataframe td {
        background: #16161f !important;
        color: #e0e0e5 !important;
        padding: 0.6rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    .stTable tr:hover td,
    table.dataframe tr:hover td {
        background: #1f1f2a !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--accent-primary);
        color: var(--bg-primary) !important;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: var(--accent-secondary);
        transform: translateY(-1px);
        box-shadow: 0 4px 20px var(--accent-glow);
    }
    
    /* Selectbox and Inputs */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        color: var(--text-primary);
    }
    
    .stSelectbox > div > div:hover,
    .stMultiSelect > div > div:hover {
        border-color: var(--border-accent);
    }
    
    .stSelectbox label,
    .stMultiSelect label {
        color: var(--text-secondary) !important;
        font-weight: 500;
    }
    
    /* Selected items in multiselect - dark text on green background */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: var(--accent-primary) !important;
        color: #0a0a0f !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] span {
        color: #0a0a0f !important;
    }
    
    /* Tag close button */
    .stMultiSelect [data-baseweb="tag"] svg {
        fill: #0a0a0f !important;
    }
    
    /* Selectbox selected value text */
    .stSelectbox [data-baseweb="select"] span {
        color: var(--text-primary) !important;
    }
    
    /* Text inputs */
    .stTextInput input {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 1px var(--accent-primary) !important;
    }
    
    /* Slider */
    .stSlider [data-baseweb="slider"] {
        background: var(--bg-tertiary);
    }
    
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: var(--text-muted) !important;
    }
    
    /* Footer */
    .footer-style {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 2rem;
        border: 1px solid var(--border-subtle);
    }
    
    .footer-style div {
        color: var(--text-secondary) !important;
    }
    
    .footer-style strong {
        color: var(--accent-primary) !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: var(--bg-card);
        border-radius: 8px;
        border: 1px solid var(--border-subtle);
        font-weight: 500;
        color: var(--text-primary);
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-hover);
        border-color: var(--border-accent);
    }
    
    [data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        border-radius: 10px;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-subtle);
    }
    
    /* Horizontal rule */
    hr {
        border-color: var(--border-subtle);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--accent-primary) !important;
    }
    
    /* Checkbox and radio */
    .stCheckbox label,
    .stRadio label {
        color: var(--text-secondary) !important;
    }
    
    /* Code blocks */
    code {
        background: var(--bg-tertiary) !important;
        color: var(--accent-primary) !important;
        font-family: 'JetBrains Mono', monospace;
    }
    
    pre {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly .bg {
        fill: var(--bg-card) !important;
    }
</style>
"""

# CDF Configuration
SPACE = "fantasy_football"
VERSION = "1"

# Data model external IDs
MANAGER_VIEW = "Manager"
GAMEWEEK_PERF_VIEW = "ManagerGameweekPerformance"
TEAM_BETTING_VIEW = "ManagerTeamBetting"
TEAM_VIEW = "PLTeam"
TRANSFER_VIEW = "Transfer"
PLAYER_VIEW = "Player"
MANAGER_TEAM_VIEW = "ManagerTeam"
GAMEWEEK_VIEW = "Gameweek"
FIXTURE_VIEW = "Fixture"

# Cache TTL (in seconds)
CACHE_TTL = 3600  # 1 hour

# Plotly Chart Theme Configuration - Dark Modern
PLOTLY_THEME = {
    "layout": {
        "paper_bgcolor": "#16161f",
        "plot_bgcolor": "#16161f",
        "font": {
            "family": "Outfit, sans-serif",
            "size": 13,
            "color": "#a0a0b0"
        },
        "title": {
            "font": {
                "family": "Outfit, sans-serif",
                "size": 18,
                "color": "#f0f0f5"
            }
        },
        "xaxis": {
            "gridcolor": "rgba(255, 255, 255, 0.06)",
            "linecolor": "rgba(255, 255, 255, 0.1)",
            "tickfont": {"color": "#a0a0b0", "size": 12},
            "zerolinecolor": "rgba(255, 255, 255, 0.1)"
        },
        "yaxis": {
            "gridcolor": "rgba(255, 255, 255, 0.06)",
            "linecolor": "rgba(255, 255, 255, 0.1)",
            "tickfont": {"color": "#a0a0b0", "size": 12},
            "zerolinecolor": "rgba(255, 255, 255, 0.1)"
        },
        "colorway": ["#00e676", "#00bfa5", "#64b5f6", "#ba68c8", "#ff8a65", "#ffd54f", "#4db6ac", "#7986cb"],
        "hovermode": "closest",
        "hoverlabel": {
            "bgcolor": "#1a1a24",
            "bordercolor": "rgba(0, 230, 118, 0.3)",
            "font": {"color": "#f0f0f5", "family": "Outfit, sans-serif"}
        },
        "legend": {
            "bgcolor": "rgba(22, 22, 31, 0.8)",
            "bordercolor": "rgba(255, 255, 255, 0.06)",
            "font": {"color": "#a0a0b0"}
        }
    }
}

