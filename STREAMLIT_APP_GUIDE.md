# 🎯 Fantasy Football Analytics - Streamlit Dashboard

A beautiful, interactive dashboard to visualize your Fantasy Premier League analytics from CDF!

## ✨ Features

### 📊 **Leaderboard Tab**
- Real-time league rankings
- Key metrics: Total managers, highest points, most consistent, best value growth
- Interactive points distribution chart
- Sortable manager table with all stats

### 📈 **Performance Trends Tab**
- Week-by-week points comparison
- Cumulative points tracking
- Transfer activity visualization
- Multi-manager comparison

### 🎯 **Team Betting Tab**
- Heatmap showing which PL teams each manager picks from
- Success rate analysis by team
- Total points per team breakdown
- Discover your "lucky" teams!

### 💎 **Consistency Analysis Tab**
- Scatter plots: Average vs volatility, Transfers vs value growth
- Category leaders: Most consistent, best value growth, highest average PPW
- Visual identification of different playing styles

## 🚀 How to Run

### 1. Install Dependencies (if needed)
```bash
poetry install
```

### 2. Make Sure Your .env File is Set Up
The app uses the same `.env` file as your notebook:
```bash
CDF_CLUSTER=bluefield
CDF_PROJECT=sofie-prod
CDF_BASE_URL=https://bluefield.cognitedata.com
CDF_TOKEN_URL=<your-token-url>
CDF_CLIENT_ID=<your-client-id>
CDF_CLIENT_SECRET=<your-client-secret>
```

### 3. Run the Streamlit App
```bash
poetry run streamlit run streamlit_app.py
```

Or if you're in the poetry shell:
```bash
poetry shell
streamlit run streamlit_app.py
```

### 4. Open in Browser
The app will automatically open in your default browser at:
```
http://localhost:8501
```

## 📱 Using the Dashboard

### Sidebar Controls
- **Select Managers**: Choose which managers to display in the charts
- **Connection Status**: Shows if you're connected to CDF

### Navigation Tabs
Click on any tab to explore different analytics:
- **Leaderboard**: Overall standings and rankings
- **Performance Trends**: Week-by-week analysis
- **Team Betting**: PL team selection patterns
- **Consistency Analysis**: Playing style comparisons

### Interactive Features
- 📊 **Hover** over charts for detailed tooltips
- 🔍 **Zoom** in/out on any chart
- 💾 **Download** chart data or images
- 🔄 **Auto-refresh**: Data is cached for 1 hour
- 📱 **Responsive**: Works on desktop, tablet, and mobile

## 🎨 Customization

### Change Theme
Add a `.streamlit/config.toml` file:
```toml
[theme]
primaryColor = "#37003c"  # Premier League purple
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Modify Visualizations
Edit `streamlit_app.py`:
- Change chart colors in `px.bar()`, `px.line()`, etc.
- Add new metrics or charts
- Customize layout with `st.columns()`, `st.container()`, etc.

## 🔄 Refreshing Data

The app caches data for 1 hour. To force refresh:
1. **Restart the app**: Stop (Ctrl+C) and run again
2. **Clear cache**: Press `C` in the terminal while app is running
3. **In-app**: Click "Clear cache" in the hamburger menu (☰)

Or set a shorter TTL in the code:
```python
@st.cache_data(ttl=600)  # 10 minutes instead of 3600
```

## 🐛 Troubleshooting

### "No manager data found"
**Solution**: Run the `load_fpl_to_cdf.ipynb` notebook first to load data

### "Failed to connect to CDF"
**Solution**: Check your `.env` file has correct credentials

### "Module not found" error
**Solution**: 
```bash
poetry install
poetry run streamlit run streamlit_app.py
```

### Charts not loading
**Solution**: Clear browser cache or try incognito mode

### Data seems outdated
**Solution**: 
1. Run the notebook to update CDF data
2. Restart the Streamlit app
3. Clear cache with `C` key

## 🚀 Deployment Options

### Deploy to Streamlit Cloud (Free!)
1. Push your code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Add environment variables in Settings
5. Click Deploy!

### Deploy to Your Own Server
```bash
# Using screen or tmux
screen -S fpl-dashboard
poetry run streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
# Detach with Ctrl+A, D
```

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install
EXPOSE 8501
CMD ["poetry", "run", "streamlit", "run", "streamlit_app.py"]
```

## 📊 Performance Tips

1. **Use filters**: Select fewer managers for faster loading
2. **Cache duration**: Increase TTL if data updates infrequently
3. **Limit data**: Modify fetch functions to limit rows
4. **Optimize queries**: Use CDF filters instead of Python filtering

## 🎯 Next Steps

### Enhance Your Dashboard
- Add player-level analysis tab
- Create custom metrics and KPIs
- Add prediction features
- Integrate with more FPL APIs
- Add export to PDF/Excel
- Create manager comparison tool

### Share with Your League
- Deploy to Streamlit Cloud
- Share the URL with friends
- Enable authentication if needed
- Add league chat/comments

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Python](https://plotly.com/python/)
- [CDF Python SDK](https://cognite-sdk-python.readthedocs-hosted.com)
- [Fantasy Premier League API](https://fantasy.premierleague.com/api/bootstrap-static/)

---

**Built with ❤️ for Fantasy Football fans**

Enjoy your dashboard! 🎉⚽

