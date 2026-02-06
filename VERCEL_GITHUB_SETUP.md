# Vercel + GitHub Auto-Deployment Setup

## ✅ GitHub Actions Removed

The GitHub Actions CI/CD workflow has been **removed** to prevent conflicts with Vercel's automatic deployment system.

---

## 🚀 Enable Vercel Auto-Deployment

Follow these steps to set up automatic deployments from GitHub to Vercel:

### Step 1: Connect GitHub Repository to Vercel

1. **Go to Vercel Dashboard**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"

2. **Import Your Repository**
   - Select "Import Git Repository"
   - Choose your GitHub account
   - Find and select `core-ai-chatbot` repository
   - Click "Import"

3. **Configure Build Settings**
   
   Vercel should auto-detect the configuration, but verify these settings:
   
   - **Framework Preset**: `Other` or `Vite`
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/build`
   - **Install Command**: `npm install --prefix frontend`

4. **Add Environment Variables**
   - Click "Environment Variables"
   - Add: `MISTRAL_API_KEY` with your API key
   - Select all environments (Production, Preview, Development)
   - Click "Add"

5. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete
   - Your app will be live at `https://your-project.vercel.app`

---

## 🔄 Auto-Deployment Behavior

Once connected, Vercel will automatically:

### Production Deployments
- **Trigger**: Every push to `main` branch
- **URL**: Your production domain (e.g., `core-ai-chatbot.vercel.app`)
- **Automatic**: Yes, deploys immediately after push

### Preview Deployments
- **Trigger**: Every push to any other branch or pull request
- **URL**: Unique preview URL (e.g., `core-ai-chatbot-git-feature-user.vercel.app`)
- **Automatic**: Yes, creates a preview for every PR

### How to Deploy
```bash
# Automatic deployment - just push to GitHub
git add .
git commit -m "Your changes"
git push origin main  # Triggers production deployment

# Or push to feature branch
git push origin feature-branch  # Triggers preview deployment
```

---

## 🎯 Current Project Structure for Vercel

Your project is configured with:

```
core-ai-chatbot/
├── frontend/              # React + Vite app (builds to static files)
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── api/                   # Backend API (Vercel serverless functions)
│   ├── index.py          # FastAPI app
│   └── requirements.txt
│
├── vercel.json           # Vercel configuration
├── package.json          # Root package file
└── .vercelignore         # Files to exclude from deployment
```

---

## 🔧 Vercel Configuration Explained

**vercel.json** is configured to:

1. **Build Frontend**: Runs `npm run build` in frontend directory
2. **Output Static Files**: Serves frontend from `frontend/build`
3. **API Routes**: Routes `/api/*` to Python serverless functions
4. **SPA Routing**: Redirects all other routes to `index.html`

---

## 🛠️ Troubleshooting Auto-Deployment

### Issue: Vercel Not Deploying on Push

**Solution 1: Check GitHub Integration**
1. Go to Vercel Dashboard → Your Project
2. Click "Settings" → "Git"
3. Verify repository is connected
4. Check "Production Branch" is set to `main`

**Solution 2: Check Repository Permissions**
1. Go to GitHub → Settings → Applications
2. Find Vercel in "Installed GitHub Apps"
3. Click "Configure"
4. Ensure repository access is granted

**Solution 3: Trigger Manual Deployment**
```bash
# Via Vercel CLI
vercel --prod

# Or via Vercel Dashboard
# Go to Deployments → Click "Redeploy"
```

### Issue: Build Fails on Vercel

**Check Build Logs:**
1. Go to Vercel Dashboard → Your Project
2. Click "Deployments"
3. Click the failed deployment
4. Review "Build Logs" for errors

**Common Build Issues:**
- Missing dependencies in `package.json`
- Wrong build command
- Incorrect output directory
- Missing environment variables

### Issue: GitHub Actions Still Running

**Verify Removal:**
```bash
# Check if .github/workflows is empty
ls -la .github/workflows/

# If files exist, remove them
rm -rf .github/workflows/ci.yml
git add .github/workflows/
git commit -m "Remove GitHub Actions workflow"
git push
```

---

## 📊 Monitoring Deployments

### View Deployment Status

**In Vercel Dashboard:**
- **Deployments Tab**: See all deployments with status
- **Build Logs**: View real-time build output
- **Function Logs**: Debug API issues

**In GitHub:**
- **Commits**: Check marks indicate successful deployment
- **Pull Requests**: Preview URLs appear as comments

### Deployment Notifications

Enable notifications in Vercel:
1. Go to Account Settings → Notifications
2. Enable email/Slack notifications for:
   - Deployment succeeded
   - Deployment failed
   - Deployment started

---

## 🔐 Environment Variables Management

### Adding Variables

**Via Dashboard:**
```
Settings → Environment Variables → Add
```

**Via CLI:**
```bash
vercel env add VARIABLE_NAME production
```

### Required Variables for This Project

| Variable | Environment | Required |
|----------|-------------|----------|
| `MISTRAL_API_KEY` | Production | ✅ Yes |
| `MISTRAL_API_KEY` | Preview | ⚠️ Recommended |
| `MISTRAL_API_KEY` | Development | ⚠️ Recommended |

### Updating Variables

After adding/updating environment variables:
```bash
# Trigger a redeploy for changes to take effect
vercel --prod
```

Or click "Redeploy" in the Vercel Dashboard.

---

## 🌿 Branch Deployment Strategy

### Recommended Workflow

```bash
# Feature development
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
# → Creates preview deployment

# Create pull request on GitHub
# → Vercel comments with preview URL

# After review, merge to main
git checkout main
git merge feature/new-feature
git push origin main
# → Triggers production deployment
```

### Preview URLs

Every pull request gets a unique preview URL:
- **Format**: `https://project-git-branch-user.vercel.app`
- **Lifetime**: Active until PR is closed/merged
- **Environment**: Isolated from production

---

## 📝 Deployment Checklist

Before pushing to main:

- [ ] Code tested locally
- [ ] Frontend builds successfully (`cd frontend && npm run build`)
- [ ] Backend works with current dependencies
- [ ] Environment variables are set in Vercel
- [ ] `.vercelignore` doesn't exclude necessary files
- [ ] `vercel.json` configuration is correct
- [ ] No GitHub Actions workflows in `.github/workflows/`

---

## 🚫 What NOT to Do

❌ **Don't** commit `.env` files
❌ **Don't** commit `node_modules/` or `venv/`
❌ **Don't** hardcode API keys in code
❌ **Don't** use GitHub Actions and Vercel auto-deploy together
❌ **Don't** push directly to main without testing

✅ **Do** use environment variables
✅ **Do** test in preview deployments first
✅ **Do** use pull requests for code review
✅ **Do** check build logs if deployment fails

---

## 🔄 Manual Deployment (If Needed)

If auto-deployment isn't working, you can deploy manually:

### Via CLI
```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Via Dashboard
1. Go to your project on Vercel
2. Click "Deployments" tab
3. Click "Redeploy" on any previous deployment
4. Or click "Create Deployment" to deploy from a specific branch

---

## 🎉 Success Indicators

Your setup is working correctly when:

✅ Pushing to `main` triggers automatic production deployment
✅ Opening a PR creates a preview deployment
✅ Preview URL appears as a comment in the PR
✅ Build completes successfully (check mark on GitHub commit)
✅ Application is accessible at your Vercel URL
✅ API endpoints respond correctly
✅ No GitHub Actions workflows run on push

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Git Integration](https://vercel.com/docs/concepts/git)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [Environment Variables Guide](https://vercel.com/docs/concepts/projects/environment-variables)

---

## 💡 Pro Tips

1. **Use Preview Deployments**: Test changes before merging to main
2. **Custom Domains**: Add in Project Settings → Domains
3. **Deployment Protection**: Enable password protection for preview deployments
4. **Analytics**: Enable Vercel Analytics for usage insights
5. **Edge Functions**: Consider using Edge Functions for better performance

---

## 🆘 Need Help?

If you're still having issues:

1. Check [Vercel Status Page](https://www.vercel-status.com/)
2. Review deployment logs in Vercel Dashboard
3. Visit [Vercel Community](https://github.com/vercel/vercel/discussions)
4. Contact Vercel Support (for Pro/Enterprise plans)

---

**Status**: ✅ GitHub Actions removed, ready for Vercel auto-deployment

**Last Updated**: 2024

---

Remember: After connecting your repo to Vercel, simply push to GitHub and Vercel handles the rest! 🚀