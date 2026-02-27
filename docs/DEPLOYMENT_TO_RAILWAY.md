# Deployment to Railway - Step by Step Guide

## Prerequisites
- Railway account (sign up at https://railway.app)
- Git repository with changes
- Railway CLI installed

## Step 1: Verify All Changes Are Committed

```bash
git status
# Should show: "On branch main, nothing to commit, working tree clean"

git log --oneline -5
# Show recent commits with wave animation feature
```

## Step 2: Ensure Railway Configuration

Your `railway.json` is already configured:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "bash start.sh",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Step 3: Push to GitHub

```bash
git push origin main
# Pushes all commits including wave animation feature
```

## Step 4: Option A - Deploy via Railway CLI

### Install Railway CLI (if not already installed)
```bash
npm install -g @railway/cli
```

### Login to Railway
```bash
railway login
# Opens browser for authentication
```

### Link to Project
```bash
cd /workspaces/India-specific-tsunami-early-warning-system
railway init
# Select existing project or create new one
```

### Deploy
```bash
railway up
# Deploys current code to Railway
```

### Monitor Deployment
```bash
railway logs
# Shows deployment and application logs
```

### Get URL
```bash
railway open
# Opens your deployed application
```

## Step 5: Option B - Deploy via GitHub Integration

1. **Visit Railway Dashboard**
   - Go to https://railway.app/dashboard
   - Click "New Project"

2. **Select Deployment Method**
   - Choose "Deploy from GitHub"

3. **Select Repository**
   - Choose: vsiva763-git/India-specific-tsunami-early-warning-system
   - Authorize Railway to access your repository

4. **Configure Environment**
   - Railway will auto-detect `railway.json`
   - No additional configuration needed

5. **Deploy**
   - Click "Deploy" button
   - Railway automatically builds and deploys

## Step 6: Verify Deployment

### Check Wave Animation Feature

1. **Access Your Deployment**
   - URL: `https://your-service-name.railway.app`
   - Or check email for deployment URL

2. **Navigate to Wave Visualization**
   - Option A: Click "🌊 Wave Visualization" button on main dashboard
   - Option B: Direct URL: `https://your-service-name.railway.app/waves`

3. **Test Features**
   - ✓ Animation modes work
   - ✓ Controls are responsive
   - ✓ Data displays correctly
   - ✓ Risk levels update
   - ✓ Mobile layout works

### Test Main Endpoints

```bash
curl https://your-service-name.railway.app/health
# Should return: {"status": "healthy", ...}

curl https://your-service-name.railway.app/waves
# Should return: HTML dashboard

curl https://your-service-name.railway.app/
# Should return: Main live dashboard
```

## Step 7: Monitor and Troubleshoot

### View Logs
```bash
railway logs
# Shows all application logs
```

### Check Health Status
```bash
curl https://your-service-name.railway.app/health
```

### Environment Variables (if needed)
```bash
railway variable add PORT=5000
railway variable add ENVIRONMENT=production
```

## Common Issues & Solutions

### Issue: Deployment Hangs
**Solution:** 
- Check logs: `railway logs`
- Ensure `start.sh` is executable: `chmod +x start.sh`
- Verify `railway.json` format

### Issue: Route /waves Not Found
**Solution:**
- Verify `app.py` has the `/waves` route
- Check app.py was deployed: `railway logs`
- Restart: `railway redeploy`

### Issue: Large Model File Timeout
**Solution:**
- Model file is already in repo (tsunami_detection_binary_focal.keras)
- May take 5-10 minutes on first deploy
- Increase timeout if needed

### Issue: CSS/JS Not Loading
**Solution:**
- Hard refresh browser: `Ctrl+Shift+R`
- Clear cache: Dev Tools → Storage → Clear All
- Check Network tab for failed requests

### Issue: Animation Not Smooth
**Solution:**
- Expected performance varies by device
- On slower connections: 20-30 FPS is normal
- Not a deployment issue

## Continuous Deployment

### Automatic Redeployment on Push
Railway automatically redeploys when you push to main:

```bash
# Make changes to code
git add .
git commit -m "Update wave animation feature"
git push origin main

# Railway automatically detects changes and redeploys
# Check status: railway logs
```

### Disable Auto-Deploy (Optional)
In Railway dashboard:
1. Go to Project Settings
2. Find "Auto-Deploy"
3. Toggle off if desired

## Rollback (if needed)

If something breaks after deployment:

```bash
# View deployment history
railway logs

# Redeploy previous version
git revert HEAD
git push origin main

# Railway will redeploy with previous code
```

## Performance Monitoring

### Check Metrics in Railway Dashboard
1. Open https://railway.app/dashboard
2. Select your project
3. View:
   - CPU Usage
   - Memory Usage
   - Network I/O
   - Logs

### Optimize if Needed
- Increase memory if model loading times out
- Add caching headers for static files
- Monitor for unusual traffic patterns

## Final Verification Checklist

- [ ] Code pushed to GitHub
- [ ] No deployment errors in logs
- [ ] Health endpoint responds: `/health`
- [ ] Main dashboard loads: `/`
- [ ] Wave visualization accessible: `/waves`
- [ ] All 3 wave modes working
- [ ] Controls are responsive
- [ ] Statistics update in real-time
- [ ] Mobile layout responsive
- [ ] No JavaScript errors in browser console

## Troubleshooting Commands

```bash
# Check deployment status
railway status

# View last 100 lines of logs
railway logs -n 100

# View real-time logs
railway logs -f

# Check environment variables
railway variable list

# SSH into running container (optional)
railway shell

# View project details
railway project show

# List all projects
railway project list
```

## Support Resources

- **Railway Docs:** https://docs.railway.app
- **Railway Community:** https://discord.gg/railway
- **Project GitHub:** https://github.com/vsiva763-git/India-specific-tsunami-early-warning-system

## Next Steps After Deployment

1. **Share the URL** with stakeholders
2. **Monitor logs** for first 24 hours
3. **Collect feedback** on wave visualization
4. **Plan next features** (3D visualization, WebSocket, etc.)

---

**Deployment Date:** January 23, 2026
**Wave Animation Version:** 1.0
**Status:** Production Ready ✓

