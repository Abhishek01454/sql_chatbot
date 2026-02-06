# Vercel Deployment Guide

This guide will help you deploy the Mistral AI Chatbot to Vercel.

## Prerequisites

- A [Vercel account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/docs/cli) installed (optional, for CLI deployment)
- A Mistral API key from [Mistral AI](https://console.mistral.ai/)

## Project Structure

This project uses a monorepo structure:
- `frontend/` - React + Vite application
- `backend/` - FastAPI Python backend

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub/GitLab/Bitbucket**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Import Project to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your Git repository
   - Vercel will automatically detect the `vercel.json` configuration

3. **Configure Environment Variables**
   - In the project settings, go to "Environment Variables"
   - Add the following variable:
     - `MISTRAL_API_KEY`: Your Mistral API key
   - Click "Save"

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your application
   - You'll get a production URL like `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Project Root**
   ```bash
   vercel
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add MISTRAL_API_KEY
   ```
   Enter your Mistral API key when prompted.

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

## Configuration Details

### vercel.json

The `vercel.json` file configures:
- **Frontend Build**: Static build of the React app from `frontend/` directory
- **Backend**: Serverless function from `backend/main.py`
- **Routing**: 
  - `/api/*` routes to the Python backend
  - All other routes serve the frontend
- **Environment Variables**: Secure storage for API keys
- **Function Settings**: Memory and timeout limits for serverless functions

### Build Configuration

- **Frontend**: 
  - Build command: `npm run build` (defined in `frontend/package.json`)
  - Output directory: `frontend/build`
  
- **Backend**:
  - Python runtime with FastAPI
  - Dependencies from `backend/requirements.txt`

## Environment Variables

The following environment variables are required:

| Variable | Description | Example |
|----------|-------------|---------|
| `MISTRAL_API_KEY` | Your Mistral AI API key | `sk-...` |

### Adding Environment Variables

**Via Dashboard:**
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add `MISTRAL_API_KEY` with your key

**Via CLI:**
```bash
vercel env add MISTRAL_API_KEY production
```

## API Routes

After deployment, your API will be available at:
- `https://your-project.vercel.app/api/` - API root
- `https://your-project.vercel.app/api/chat` - Chat endpoint
- `https://your-project.vercel.app/api/chat/stream` - Streaming chat endpoint
- `https://your-project.vercel.app/api/conversations` - Conversations endpoint

## Frontend Routes

The frontend will be available at:
- `https://your-project.vercel.app/` - Main application

## Limitations & Considerations

### Serverless Function Limits
- **Execution Time**: Maximum 30 seconds (can be increased with Pro plan)
- **Memory**: 1024 MB (configured in vercel.json)
- **Cold Starts**: First request may be slower

### Storage
- **In-Memory Storage**: The current implementation uses in-memory storage for conversations
- **Recommendation**: For production, integrate a database like:
  - Vercel Postgres
  - MongoDB Atlas
  - Supabase
  - Redis

### CORS
- The backend is configured to allow all origins (`allow_origins=["*"]`)
- For production, restrict this to your Vercel domain:
  ```python
  allow_origins=["https://your-project.vercel.app"]
  ```

## Troubleshooting

### Build Failures

**Frontend Build Issues:**
```bash
# Test locally
cd frontend
npm install
npm run build
```

**Backend Issues:**
```bash
# Test locally
cd backend
pip install -r requirements.txt
python main.py
```

### API Not Working

1. Check environment variables are set correctly
2. Verify API key is valid
3. Check Vercel function logs in the dashboard
4. Ensure routes in `vercel.json` are correct

### CORS Errors

- Update CORS settings in `backend/main.py`
- Add your Vercel domain to `allow_origins`

## Local Development

Before deploying, test locally:

1. **Install Dependencies**
   ```bash
   # Frontend
   cd frontend
   npm install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   Create `backend/.env`:
   ```
   MISTRAL_API_KEY=your_key_here
   ```

3. **Run Backend**
   ```bash
   cd backend
   python main.py
   # Backend runs on http://localhost:8000
   ```

4. **Run Frontend**
   ```bash
   cd frontend
   npm run dev
   # Frontend runs on http://localhost:3000
   ```

## Updating Deployment

### Automatic Updates (Recommended)
- Push changes to your Git repository
- Vercel automatically rebuilds and deploys

### Manual Updates
```bash
vercel --prod
```

## Custom Domain

1. Go to your project settings on Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed
5. Vercel handles SSL certificates automatically

## Monitoring

- **Logs**: View in Vercel Dashboard → Project → Functions
- **Analytics**: Enable Vercel Analytics in project settings
- **Monitoring**: Use Vercel's built-in monitoring tools

## Security Best Practices

1. **Environment Variables**: Never commit API keys to Git
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Authentication**: Add user authentication for production use
5. **API Key Rotation**: Regularly rotate your Mistral API key

## Cost Considerations

- **Free Tier**: Suitable for hobby projects and testing
- **Pro Plan**: Required for:
  - Longer function execution times
  - Higher bandwidth
  - More concurrent executions
- **Usage**: Monitor API usage to avoid unexpected costs

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Mistral AI Documentation](https://docs.mistral.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues related to:
- **Vercel Platform**: [Vercel Support](https://vercel.com/support)
- **This Application**: Create an issue in the project repository
- **Mistral AI**: [Mistral AI Support](https://mistral.ai/contact)

---

**Note**: This configuration is optimized for Vercel's serverless platform. For alternative deployment platforms (AWS, Google Cloud, Azure), different configurations will be required.