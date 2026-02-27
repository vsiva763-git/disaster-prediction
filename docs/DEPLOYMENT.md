# India Tsunami Early Warning System - Deployment Guide

## 🚀 Deploy with GitHub Student Pack

Your project is now configured for easy deployment! Choose your preferred platform:

---

## Option 1: Railway (Recommended - Easiest)

**What you get:** $5/month credit with GitHub Student Pack

### Steps:
1. Go to [Railway.app](https://railway.app/)
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select `India-specific-tsunami-early-warning-system`
5. Railway auto-detects Python and deploys! ✅
6. Your app will be live at: `https://your-app.railway.app`

**Student Benefit:** Link GitHub Student Pack at railway.app/account for $5/month credit

---

## Option 2: Render (Free Tier Available)

**What you get:** Free hosting + enhanced features with Student Pack

### Steps:
1. Go to [Render.com](https://render.com/)
2. Sign up with GitHub
3. Click **"New"** → **"Web Service"**
4. Connect your repo: `vsiva763-git/India-specific-tsunami-early-warning-system`
5. Render uses `render.yaml` automatically
6. Click **"Create Web Service"**
7. Your app will be live at: `https://tsunami-warning-system.onrender.com`

**Note:** Free tier sleeps after inactivity (wakes up in ~30 seconds on first request)

---

## Option 3: DigitalOcean App Platform

**What you get:** $200 credit for 1 year with Student Pack

### Steps:
1. Sign up at [DigitalOcean.com](https://www.digitalocean.com/)
2. Apply GitHub Student Pack credits at [education.github.com/pack](https://education.github.com/pack)
3. Go to **App Platform** → **Create App**
4. Connect GitHub repo
5. Choose **Python** app type
6. Build Command: `pip install -r requirements.txt`
7. Run Command: `gunicorn app:app --bind 0.0.0.0:8080 --workers 2`
8. Click **Deploy**

**Cost:** ~$5-12/month (covered by $200 credit)

---

## Option 4: Microsoft Azure (For ML Apps)

**What you get:** $100 Azure credit with Student Pack

### Steps:
1. Sign up at [Azure for Students](https://azure.microsoft.com/en-us/free/students/)
2. Create **Web App**
3. Runtime: Python 3.11
4. Deploy using GitHub Actions or Azure CLI
5. Configure:
   - Startup Command: `gunicorn app:app --bind=0.0.0.0 --timeout 120`

**Good for:** ML models, scaling, enterprise features

---

## Quick Deploy Commands (After Platform Selection)

### Test locally first:
```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 2
```

### For Railway/Render:
Just push to GitHub - auto-deploys! 🎉

### For DigitalOcean/Azure:
```bash
# Install doctl (DigitalOcean CLI)
doctl apps create --spec railway.json

# Or use Azure CLI
az webapp up --name tsunami-warning --runtime PYTHON:3.11
```

---

## Environment Variables (Set in Platform Dashboard)

For production deployment, set these (optional):
- `PORT` - Auto-set by most platforms
- `FLASK_ENV` - Set to `production`
- `WORKERS` - Number of gunicorn workers (default: 2)

---

## Post-Deployment Checklist

✅ Visit `/health` endpoint to verify model loaded  
✅ Test `/live-data` endpoint for earthquake data  
✅ Check `/summary` page loads correctly  
✅ Test map interactions on `/` homepage  
✅ Monitor logs for any errors  

---

## 🎓 Getting GitHub Student Pack

If you haven't activated it yet:
1. Go to [education.github.com/pack](https://education.github.com/pack)
2. Click **"Get your Pack"**
3. Verify with your student email (.edu)
4. Access all partner offers (Railway, DigitalOcean, Azure, Namecheap, etc.)

---

## Custom Domain (Optional)

**Free domain with Student Pack:**
- Namecheap: 1 year free .me domain + SSL
- Register at [namecheap.com](https://www.namecheap.com/github-students/)
- Point to your deployment URL using CNAME

---

## Need Help?

- Railway Docs: https://docs.railway.app/
- Render Docs: https://render.com/docs
- DigitalOcean Docs: https://docs.digitalocean.com/products/app-platform/
- Issues: Open an issue on GitHub

**Your app is ready to deploy! Choose a platform above and go live in 5 minutes! 🚀**
