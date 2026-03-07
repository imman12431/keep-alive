# GitHub Actions Quick Start Guide

## 🚀 Setting Up Automated Keep-Alive for Both Apps

This guide will help you set up a **free, automated** keep-alive system using GitHub Actions that will interact with both your Streamlit apps every 5 hours.

---

## ✅ Prerequisites

- A GitHub account (free)
- 5 minutes of your time

---

## 📋 Step-by-Step Setup

### Step 1: Create a New GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Name it something like: `streamlit-keep-alive`
4. Set visibility to **Public** or **Private** (both work)
5. Click **"Create repository"**

### Step 2: Upload the Files

You have two options:

#### Option A: Upload via Web Interface (Easiest)

1. In your new repository, click **"uploading an existing file"**
2. Drag and drop these files:
   - `keep_alive_dual.py`
   - `requirements.txt`
   - `.github/workflows/keep-alive.yml`
3. Click **"Commit changes"**

#### Option B: Upload via Git Command Line

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/streamlit-keep-alive.git
cd streamlit-keep-alive

# Copy the files into the repository
cp keep_alive_dual.py requirements.txt ./
mkdir -p .github/workflows
cp .github/workflows/keep-alive.yml .github/workflows/

# Commit and push
git add .
git commit -m "Add keep-alive automation"
git push origin main
```

### Step 3: Verify the Setup

1. In your GitHub repository, click on the **"Actions"** tab
2. You should see a workflow named **"Keep Streamlit Apps Alive"**
3. If prompted, click **"I understand my workflows, go ahead and enable them"**

### Step 4: Test It Manually (Optional)

1. In the **Actions** tab, click on **"Keep Streamlit Apps Alive"**
2. Click the **"Run workflow"** button on the right
3. Select **"Run workflow"**
4. Wait for it to complete (takes about 1-2 minutes)
5. Click on the completed run to see the logs

---

## 🎯 What Happens Now?

### Automatic Execution

The workflow will now run automatically:

- **Every 5 hours** (at :00 of every 5th hour)
- Starting from the next scheduled time
- First run: within the next 5 hours

### What It Does

Each run will:

1. **Tennis App** → Selects Djokovic video → Clicks "Run Backhand Detection"
2. **QA App** → Clicks first sample question about Qatar's GDP
3. Both apps stay awake and active! 🎉

### Schedule Times (UTC)

The workflow runs at:
- 00:00 UTC
- 05:00 UTC
- 10:00 UTC
- 15:00 UTC
- 20:00 UTC

---

## 🔍 Monitoring

### View Execution History

1. Go to your repository
2. Click **"Actions"** tab
3. See all past runs with ✅ success or ❌ failure indicators

### View Detailed Logs

1. Click on any workflow run
2. Click **"Keep Tennis App Alive"**
3. Expand the steps to see detailed logs:
   - When it connected to each app
   - What buttons it clicked
   - Success/failure status

### Download Logs

1. In a workflow run, scroll to **"Artifacts"** section
2. Download `execution-logs` if available
3. Download `debug-screenshots` if the workflow failed

---

## 🛠️ Customization

### Change the Interval

Edit `.github/workflows/keep-alive.yml`:

```yaml
schedule:
  # Every 3 hours
  - cron: '0 */3 * * *'
  
  # Every 6 hours
  - cron: '0 */6 * * *'
  
  # Every 12 hours
  - cron: '0 */12 * * *'
  
  # Specific times (e.g., 9 AM and 9 PM UTC)
  - cron: '0 9,21 * * *'
```

After editing, commit and push the changes.

### Disable One App

Edit `keep_alive_dual.py` and comment out the app you don't want:

```python
# Tennis app
tennis_success = interact_with_tennis_app(driver)

# QA app (commented out)
# qa_success = interact_with_qa_app(driver)
```

---

## ❓ Troubleshooting

### Workflow Not Running

**Problem:** No automatic runs showing up

**Solutions:**
1. Ensure the repository is not archived
2. Check that GitHub Actions are enabled (Settings → Actions → Allow all actions)
3. Make sure the workflow file is in `.github/workflows/keep-alive.yml`
4. Try running it manually first

### Workflow Failing

**Problem:** Red X next to workflow runs

**Solutions:**
1. Click on the failed run to see error details
2. Download the `debug-screenshots` artifact to see what went wrong
3. Common issues:
   - App URL changed → Update URLs in `keep_alive_dual.py`
   - App UI changed → Update button selectors in the script
   - Timeout issues → Increase wait times in the script

### Apps Still Going to Sleep

**Problem:** Apps becoming inactive despite the workflow

**Possible causes:**
1. Streamlit Community Cloud has strict limits - consider upgrading
2. The interaction isn't triggering enough activity
3. You may need more frequent runs (every 3 hours instead of 5)

---

## 💡 Benefits of GitHub Actions

✅ **Completely free** (2,000 minutes/month for free accounts)
✅ **No server needed** - runs in the cloud
✅ **No maintenance** - GitHub handles everything
✅ **Logs and monitoring** built-in
✅ **Easy to disable/enable** - just toggle the workflow
✅ **Works from anywhere** - no need to keep your computer on

---

## 📊 Usage Limits

**Free GitHub Account:**
- 2,000 minutes/month of Actions
- Each run takes ~2 minutes
- 5-hour interval = ~144 runs/month = ~288 minutes
- **You're well within the free tier!** 🎉

---

## 🔐 Security Notes

- The scripts run in GitHub's secure environment
- No credentials or API keys needed
- Public repos: Anyone can see the code (but that's fine - it's just automation)
- Private repos: Only you can see everything

---

## 🆘 Need Help?

If something isn't working:

1. Check the Actions logs (most detailed information)
2. Download the artifacts (screenshots show what failed)
3. Try running manually first
4. Compare your files to the originals

---

## ✨ You're Done!

Your apps will now automatically stay active every 5 hours, completely hands-free! 🎉

Just sit back and let GitHub Actions do the work. Check the Actions tab occasionally to confirm everything is running smoothly.
