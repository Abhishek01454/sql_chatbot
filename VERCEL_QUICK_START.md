# Vercel Quick Start Guide

## 🚀 Deploy in 5 Minutes

### Step 1: Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

### Step 2: Deploy
```bash
# Login to Vercel
vercel login

# Deploy from project root
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Select your account
# - Link to existing project? No
# - What's your project's name? (default is fine)
# - In which directory is your code located? ./
```

### Step 3: Add Environment Variable
```bash
vercel env add MISTRAL_API_KEY production
```
Paste your Mistral API key when prompted.

### Step 4: Deploy to Production
```bash
vercel --prod
```

## ✅ That's It!

Your app is now live at: `https://your-project.vercel.app`

---

## 🌐 Alternative: Deploy via Dashboard

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Vercel auto-detects configuration

3. **Add Environment Variable**
   - Go to Project Settings → Environment Variables
   - Add `MISTRAL_API_KEY` with your API key

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Done! 🎉

---

## 📋 Checklist

- [ ] Vercel account created
- [ ] Mistral API key obtained from https://console.mistral.ai/
- [ ] Code pushed to Git (for dashboard deployment)
- [ ] Environment variable `MISTRAL_API_KEY` added
- [ ] Deployment successful

---

## 🔧 Test Your Deployment

```bash
# Test API endpoint
curl https://your-project.vercel.app/api/

# Expected response:
# {"message":"Mistral AI Chatbot API is running"}
```

---

## 🐛 Troubleshooting

**Build fails?**
```bash
# Test locally first
cd frontend && npm install && npm run build
cd ../backend && pip install -r requirements.txt && python main.py
```

**API not responding?**
- Check environment variables are set in Vercel dashboard
- Verify your Mistral API key is valid
- Check function logs in Vercel dashboard

**CORS errors?**
- Update `allow_origins` in `backend/main.py` to include your Vercel domain

---

## 📚 Need More Info?

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

---

## 💡 Pro Tips

1. **Automatic Deployments**: Every push to `main` branch auto-deploys
2. **Preview Deployments**: Every pull request gets a preview URL
3. **Custom Domain**: Add in Project Settings → Domains
4. **View Logs**: Dashboard → Your Project → Functions → View logs
5. **Monitor Usage**: Dashboard → Your Project → Analytics

---

**Ready to deploy? Run:** `vercel --prod` 🚀