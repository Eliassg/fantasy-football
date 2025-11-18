# 📅 Setting Up Weekly FPL Data Updates

You have two options for automatic weekly updates:

## Option 1: Upload & Schedule Function in CDF Fusion (Recommended) ⭐

### Step 1: Upload the Function
1. Open https://bluefield.cognitedata.com
2. Click **"Integrate"** → **"Functions"** in the left menu
3. Click **"Create Function"** or **"Upload Function"**
4. Configure:
   - **Name**: `FPL Weekly Update`
   - **External ID**: `fpl_weekly_update`
   - **Runtime**: Python 3.11
   - **CPU**: 0.5
   - **Memory**: 1.5 GB
5. Upload these files from your project:
   ```
   modules/fantasy-football/functions/fpl_weekly_update/
   ├── handler.py
   ├── requirements.txt
   └── function_config.yaml
   ```
6. Set **Environment Variables**:
   - `FPL_LEAGUE_ID` = `sl9tyc`
7. Click **"Create"** or **"Deploy"**

### Step 2: Test the Function First
1. Click on the function
2. Click **"Run"** or **"Test"**
3. Leave the input data empty (or use `{}`)
4. Click **"Execute"**
5. Check that it runs successfully and shows stats like:
   ```json
   {
     "status": "success",
     "stats": {
       "teams": 20,
       "gameweeks": 38,
       "managers": 27,
       "performance": 115
     }
   }
   ```

### Step 3: Create a Schedule
1. In the function details, look for **"Schedules"** or **"Trigger"**
2. Click **"Add Schedule"** or **"Create Schedule"**
3. Set the schedule:
   - **Name**: `Weekly FPL Update`
   - **Cron expression**: `0 2 * * 1` (Mondays at 2 AM UTC)
   - **Data/Input**: Leave empty `{}`
4. Click **"Create"** or **"Save"**

### Common Cron Schedules:
- `0 2 * * 1` - Every Monday at 2 AM
- `0 0 * * 1` - Every Monday at midnight
- `0 6 * * 2` - Every Tuesday at 6 AM (after gameweek ends)
- `0 */12 * * *` - Every 12 hours

## Option 2: Simple Manual Updates via Notebook 📓 (Easiest!)

If you prefer manual control, just run your notebook when you want to update:
1. Open `notebooks/load_fpl_to_cdf.ipynb`
2. Run the cells (or "Run All")
3. Data gets updated in CDF

## Testing Your Schedule

After setting up the schedule:
1. Wait for the first scheduled run, OR
2. Trigger it manually to test
3. Check your data model in Fusion to see updated stats
4. Go to **"Data Modeling"** → **"Instances"** → Filter by `fantasy_football` space

## Monitoring

To check if your scheduled function is running:
1. Go to **Functions** → **"FPL Weekly Update"**
2. Check **"Logs"** or **"Execution History"**
3. You'll see timestamps and results of each run

## Troubleshooting

**If the function fails:**
- Check the function logs in Fusion
- Verify the FPL API is accessible
- Make sure your league ID is correct in the config

**To update the league ID:**
Edit `config.dev.yaml` and redeploy:
```bash
poetry run cdf build && poetry run cdf deploy
```

---

## 🎉 You're All Set!

Your FPL data will now update automatically every week. Check CDF Fusion to see your league's progress over the season!

