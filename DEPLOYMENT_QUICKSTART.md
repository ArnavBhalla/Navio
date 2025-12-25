# Navio Deployment Quick Start

Quick reference for deploying Navio to production.

## Prerequisites Checklist

- [ ] Fly.io account created
- [ ] Vercel account created
- [ ] OpenAI API key obtained
- [ ] Anthropic API key obtained
- [ ] Fly CLI installed (`brew install flyctl`)
- [ ] Git repository set up

## 30-Minute Deployment

### 1. Backend (Fly.io) - 15 minutes

```bash
# 1. Login to Fly.io
fly auth login

# 2. Create database
fly postgres create --name navio-db --region sjc

# 3. Navigate to backend
cd backend

# 4. Set secrets (update with your values)
fly secrets set \
  DATABASE_URL="<from step 2>" \
  OPENAI_API_KEY="sk-proj-xxx" \
  ANTHROPIC_API_KEY="sk-ant-xxx" \
  AUTH_SECRET_KEY="$(openssl rand -hex 32)" \
  FRONTEND_URL="https://your-app.vercel.app"

# 5. Deploy
fly launch --copy-config --yes

# 6. Verify
fly open
```

### 2. Frontend (Vercel) - 10 minutes

#### Via Dashboard (Recommended)
1. Go to https://vercel.com/new
2. Import your Git repository
3. Set root directory to `frontend`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://navio-api.fly.dev`
5. Click "Deploy"

#### Via CLI
```bash
cd frontend
vercel --prod
# Set NEXT_PUBLIC_API_URL when prompted
```

### 3. Update CORS - 2 minutes

```bash
cd backend
fly secrets set FRONTEND_URL="https://your-actual-vercel-url.vercel.app"
```

### 4. Seed Database - 3 minutes

```bash
cd backend

# Get admin token
TOKEN=$(curl -X POST https://navio-api.fly.dev/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  | jq -r '.access_token')

# Trigger seeding
curl -X POST https://navio-api.fly.dev/api/seed \
  -H "Authorization: Bearer $TOKEN"
```

## Verification

Test these endpoints:

```bash
# Backend health
curl https://navio-api.fly.dev/health

# Frontend
open https://your-app.vercel.app

# API docs
open https://navio-api.fly.dev/docs
```

## Common Issues

**Database connection failed**
```bash
# Check database status
fly postgres db list navio-db

# Verify DATABASE_URL secret is set
fly secrets list
```

**CORS errors**
```bash
# Ensure FRONTEND_URL matches your Vercel URL exactly
fly secrets set FRONTEND_URL="https://your-app.vercel.app"
```

**Build failed**
```bash
# View logs
fly logs

# Check Dockerfile
docker build -t navio-test .
```

## Next Steps

1. Change demo passwords:
   ```bash
   fly secrets set DEMO_ADMIN_PASSWORD="your-password"
   ```

2. Set up custom domain (optional)
3. Configure monitoring alerts
4. Enable automated backups

## Full Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment guide.

## Quick Commands Reference

```bash
# Deploy backend
cd backend && fly deploy

# Deploy frontend
cd frontend && vercel --prod

# View logs
fly logs -f

# Scale backend
fly scale count 2

# Update secrets
fly secrets set KEY=value
```

## Cost Calculator

- **Free tier**: $0/month (Fly.io free tier + Vercel Hobby)
- **Small production**: ~$20-40/month
- **Medium scale**: ~$60-100/month

API costs (OpenAI/Anthropic) are usage-based and variable.

---

**Deployment time**: ~30 minutes
**Difficulty**: ⭐⭐☆☆☆ (Beginner-friendly)
