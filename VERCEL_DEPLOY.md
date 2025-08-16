# Vercel Deployment Guide

## 🚀 Quick Deploy

After completing Vercel login, run:

```bash
vercel --prod
```

When prompted:
- **Set up and deploy?** → Yes
- **Which scope?** → Choose your account
- **Link to existing project?** → No
- **Project name?** → semiconductor-reliability-calculator (or press Enter)
- **Directory?** → Press Enter (use current directory)
- **Override settings?** → No

## 🔧 Environment Variables

After deployment, set these environment variables in Vercel dashboard:

```bash
# Required environment variables
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
DATABASE_URL=sqlite:///:memory:
DAILY_CALCULATION_LIMIT=10
```

**To set environment variables:**
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable above

## 📱 Access Your App

After deployment, Vercel will provide URLs:
- **Production**: `https://semiconductor-reliability-calculator.vercel.app`
- **Preview**: Various preview URLs for testing

## 🔧 Features Available

### ✅ Working Features
- **Frontend**: Complete UI with 3-column layout
- **Calculators**: All 6 calculators (3 active + 3 planned)
- **Authentication**: User registration and login
- **Export**: Download calculation results

### ⚠️ Limited Features (Serverless)
- **Database**: In-memory SQLite (resets on each request)
- **Usage Tracking**: Limited due to stateless nature
- **File Storage**: No persistent file storage

## 🔄 Development Workflow

### Local Development
```bash
# Start local development server
vercel dev

# This will start:
# - Frontend: http://localhost:3000
# - API: http://localhost:3000/api
```

### Deploy Updates
```bash
# Deploy to production
vercel --prod

# Deploy preview (staging)
vercel
```

## 🎯 Production Recommendations

For a production deployment with persistent database:

### Option 1: Add PostgreSQL
1. **Add Vercel Postgres**:
   ```bash
   vercel env add DATABASE_URL
   # Enter: postgresql://username:password@host:port/database
   ```

2. **Update requirements.txt**:
   ```
   psycopg2-binary==2.9.7
   ```

### Option 2: Hybrid Deployment
- **Frontend**: Vercel (static hosting)
- **Backend**: Railway/Heroku (persistent database)
- **Update API URL**: Point frontend to backend URL

## 🔍 Troubleshooting

### Common Issues
1. **Import Errors**: Check file paths in `api/main.py`
2. **Database Issues**: Verify DATABASE_URL format
3. **CORS Errors**: Check allowed origins in main.py

### Debug Commands
```bash
# Check deployment logs
vercel logs

# Local debugging
vercel dev --debug
```

## 📊 Current Status

- ✅ **Frontend**: Deployed and working
- ✅ **API**: Basic endpoints working
- ✅ **Calculators**: Mathematical functions working
- ⚠️ **Database**: In-memory (temporary)
- ⚠️ **Authentication**: Limited persistence

**Ready for demonstration and testing!**