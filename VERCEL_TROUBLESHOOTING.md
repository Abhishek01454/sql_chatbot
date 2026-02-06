# Vercel 404 Error Troubleshooting Guide

## Problem: Getting 404 Error on Vercel Deployment

If you're seeing `404 Not Found` when accessing your deployed Vercel app, follow these steps to fix it.

## Quick Fix Options

### Option 1: Use Separate Vercel Projects (Recommended)

The easiest solution is to deploy frontend and backend as separate Vercel projects.

#### Step 1: Deploy Frontend

1. **Create a new Vercel project for frontend only:**
   ```bash
   cd frontend
   vercel
   ```

2. **Follow the prompts:**
   - Set up and deploy? `Yes`
   - Which scope? `Your account`
   - Link to existing project? `No`
   - Project name? `core-ai-chatbot-frontend`
   - In which directory is your code located? `./`

3. **Deploy to production:**
   ```bash
   vercel --prod
   ```

4. **Note your frontend URL:** `https://core-ai-chatbot-frontend.vercel.app`

#### Step 2: Deploy Backend

1. **Create a new Vercel project for backend:**
   ```bash
   cd ../backend
   vercel
   ```

2. **Follow the prompts:**
   - Set up and deploy? `Yes`
   - Which scope? `Your account`
   - Link to existing project? `No`
   - Project name? `core-ai-chatbot-backend`
   - In which directory is your code located? `./`

3. **Add environment variable:**
   ```bash
   vercel env add MISTRAL_API_KEY production
   ```
   Paste your Mistral API key when prompted.

4. **Deploy to production:**
   ```bash
   vercel --prod
   ```

5. **Note your backend URL:** `https://core-ai-chatbot-backend.vercel.app`

#### Step 3: Update Frontend API Configuration

Update your frontend to point to the backend URL:

**frontend/src/api.js:**
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://core-ai-chatbot-backend.vercel.app';
```

Or create **frontend/.env.production:**
```
VITE_API_URL=https://core-ai-chatbot-backend.vercel.app
```

Then update your API client to use:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

#### Step 4: Update Backend CORS

Update **backend/main.py** to allow your frontend domain:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://core-ai-chatbot-frontend.vercel.app",
        "http://localhost:3000",  # for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy backend:
```bash
cd backend
vercel --prod
```

---

### Option 2: Fix Monorepo Structure

If you want to keep everything in one Vercel project, follow these steps:

#### Step 1: Move Frontend Files to Root

```bash
# From project root
cp -r frontend/* .
cp frontend/.gitignore .gitignore
```

#### Step 2: Create Vercel-Compatible Structure

Create **api/index.py** at the root:
```python
from backend.main import app

# This makes it work with Vercel's API routes
handler = app
```

Or copy your entire backend/main.py content to api/index.py.

#### Step 3: Create Simple vercel.json

```json
{
  "version": 2,
  "buildCommand": "npm install && npm run build",
  "outputDirectory": "build",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/index.py"
    }
  ]
}
```

#### Step 4: Update package.json

Make sure root **package.json** has:
```json
{
  "scripts": {
    "build": "vite build",
    "dev": "vite"
  }
}
```

---

### Option 3: Use Vercel's Framework Preset

#### Step 1: Configure as Vite Project

In Vercel Dashboard:
1. Go to Project Settings
2. General → Build & Development Settings
3. Framework Preset: `Vite`
4. Build Command: `cd frontend && npm run build`
5. Output Directory: `frontend/build`
6. Install Command: `cd frontend && npm install`

#### Step 2: Configure API Routes

In **vercel.json**:
```json
{
  "functions": {
    "api/*.py": {
      "runtime": "python3.9"
    }
  },
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"
    }
  ]
}
```

---

## Common Issues and Fixes

### Issue 1: "No Output Directory Found"

**Solution:** Check your build output directory matches Vite config.

**frontend/vite.config.js:**
```javascript
export default defineConfig({
  build: {
    outDir: 'build',  // or 'dist'
  }
})
```

**vercel.json:**
```json
{
  "outputDirectory": "frontend/build"  // match the outDir above
}
```

### Issue 2: Static Files Not Loading

**Solution:** Add proper routing for assets.

**vercel.json:**
```json
{
  "routes": [
    {
      "src": "/assets/(.*)",
      "dest": "/assets/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### Issue 3: API Routes Not Working

**Solution:** Ensure Python dependencies are installed.

Create **api/requirements.txt**:
```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
httpx>=0.25.0
python-dotenv>=1.0.0
```

### Issue 4: Environment Variables Not Working

**Solution:** Check variable names match exactly.

In Vercel Dashboard:
- Variable name: `MISTRAL_API_KEY` (exact match to your code)
- Environment: Select Production, Preview, and Development
- Save and **Redeploy**

### Issue 5: CORS Errors After Deployment

**Solution:** Update CORS origins in backend.

```python
allow_origins=[
    "https://your-project.vercel.app",
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]
```

---

## Verification Steps

After deploying, verify each part works:

### 1. Check Frontend
```bash
curl https://your-project.vercel.app/
# Should return HTML
```

### 2. Check API
```bash
curl https://your-project.vercel.app/api/
# Should return: {"message":"Mistral AI Chatbot API is running"}
```

### 3. Check Browser Console
- Open DevTools (F12)
- Check for errors in Console tab
- Check Network tab for failed requests

### 4. Check Vercel Logs
1. Go to Vercel Dashboard
2. Select your project
3. Click "Deployments"
4. Click on the latest deployment
5. Check "Build Logs" and "Function Logs"

---

## Recommended: Separate Projects Method

For most use cases, deploying frontend and backend as separate projects is the simplest and most reliable approach:

**Pros:**
- ✅ Simple deployment process
- ✅ Independent scaling
- ✅ Clearer separation of concerns
- ✅ Easier to debug
- ✅ No monorepo complications

**Cons:**
- ❌ Need to manage CORS
- ❌ Two separate URLs (can fix with custom domains)

---

## Need More Help?

1. **Check Vercel Build Logs:** Look for specific error messages
2. **Test Locally First:** Make sure `npm run build` works in frontend directory
3. **Verify File Paths:** Ensure index.html exists in build output
4. **Check Framework Detection:** Vercel should auto-detect Vite

---

## Working Example Configuration

If all else fails, here's a minimal working setup:

### Project Structure
```
project-root/
├── api/
│   ├── index.py          # Your FastAPI app
│   └── requirements.txt
├── src/                  # Your React source
├── public/
├── index.html
├── package.json
├── vite.config.js
└── vercel.json
```

### vercel.json
```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/index.py"
    }
  ]
}
```

This puts frontend at root and backend in `/api` folder - the simplest structure for Vercel.

---

## Still Getting 404?

If you've tried everything:

1. **Delete the Vercel project** and start fresh
2. **Use the separate projects approach** (Option 1 above)
3. **Check the example projects:** Look at Vercel's template repo for Vite + Python
4. **Contact Vercel Support:** They can check your specific deployment

Remember: The separate projects approach (Option 1) is the most reliable for monorepo setups!