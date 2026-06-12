# Deployment Guide: Render

This guide walks you through deploying the Skills Matching app to **Render**, a modern cloud platform with a free tier.

## Prerequisites

1. **GitHub account** (required for Render to access your code)
2. **Render account** (sign up at https://render.com - free)
3. **Git installed** on your machine

## Step-by-Step Deployment

### Step 1: Initialize Git Repository

Open a terminal in your project folder and run:

```powershell
git init
git add .
git commit -m "Initial commit: Skills matching app"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `skills-matcher`)
3. **Do NOT** initialize with README/gitignore (we already have those)
4. Copy the remote URL

In your terminal, add the remote and push:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/skills-matcher.git
git branch -M main
git push -u origin main
```

### Step 3: Sign Up for Render

1. Visit https://render.com
2. Sign up with your GitHub account (or email)
3. Click "Connect GitHub account" when prompted

### Step 4: Create a New Web Service

1. Log in to Render Dashboard
2. Click **+ New** → **Web Service**
3. Select your GitHub repository (search for `skills-matcher`)
4. Click **Connect** next to the repo

### Step 5: Configure Deployment Settings

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `skills-matcher` (or any name you prefer) |
| **Environment** | `Python 3` |
| **Region** | `Oregon` (US) or your preferred region |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Plan** | Free tier (sufficient for testing) |

Click **Create Web Service** and wait ~2-3 minutes for deployment.

### Step 6: Access Your App

Once deployed, Render will give you a URL like:
```
https://skills-matcher-xxxxx.onrender.com
```

Open this URL in your browser and upload JDs and resumes to test.

---

## Local Testing Before Deploy

Before pushing to Render, test locally with gunicorn:

```powershell
# Install gunicorn
pip install gunicorn

# Run with gunicorn (like Render will)
gunicorn app:app
```

Visit http://127.0.0.1:8000 in your browser.

---

## Troubleshooting

### "Build failed" error
- Check `requirements.txt` is in the root folder
- Ensure `Procfile` exists and has correct content: `web: gunicorn app:app`
- Check `runtime.txt` exists with valid Python version

### "ModuleNotFoundError"
- Missing dependency in `requirements.txt`
- Add the package and push a new commit

### App is slow or times out
- File extraction (PDF parsing) can be slow on free tier
- Consider upgrading to Render's paid plan for better performance
- Add timeout increase in Render settings if needed

### "No web processes are running"
- Check deployment logs in Render Dashboard
- Ensure `Start Command` is exactly: `gunicorn app:app`

---

## After Deployment

**Auto-redeploy on push**: Render auto-deploys whenever you push to `main` branch.

**View logs**: 
- Go to Render Dashboard
- Click your service
- View real-time logs under the "Logs" tab

**Scale up (optional)**:
- Upgrade from Free to Starter ($7/month) for persistent storage and better performance

---

## Project Files Overview

- `app.py` - Flask backend (keyword-based skill matching)
- `requirements.txt` - Python dependencies
- `Procfile` - Tells Render how to start the app
- `runtime.txt` - Specifies Python version
- `templates/index.html` - Upload UI
- `static/app.js` - Frontend logic
- `static/styles.css` - Styling
