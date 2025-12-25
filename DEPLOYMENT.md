# Navio Deployment Guide

This guide covers deploying the Navio Academic Advisor application to production using Fly.io (backend) and Vercel (frontend).

## Overview

- **Backend**: FastAPI application deployed to Fly.io with PostgreSQL database
- **Frontend**: Next.js application deployed to Vercel
- **Architecture**: Separate deployments with CORS-enabled API communication

## Prerequisites

### Required Accounts
- [Fly.io account](https://fly.io/app/sign-up) (backend hosting)
- [Vercel account](https://vercel.com/signup) (frontend hosting)
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Anthropic API key](https://console.anthropic.com/)

### Required Tools
- [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
- [Vercel CLI](https://vercel.com/docs/cli) (optional, can use web dashboard)
- [Git](https://git-scm.com/downloads)
- [Docker](https://docs.docker.com/get-docker/) (optional, for local testing)

---

## Part 1: Backend Deployment (Fly.io)

### Step 1: Install Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Verify installation:
```bash
fly version
```

### Step 2: Login to Fly.io

```bash
fly auth login
```

### Step 3: Create PostgreSQL Database

```bash
# Create a Postgres cluster
fly postgres create --name navio-db --region sjc

# Note the connection string shown - you'll need it later
```

**Important**: Save the connection details shown after creation. You'll need:
- Username
- Password
- Hostname
- Database name

### Step 4: Configure Environment Variables

The backend requires several environment variables. Set them as Fly.io secrets:

```bash
# Navigate to backend directory
cd backend

# Set required secrets
fly secrets set \
  DATABASE_URL="postgresql://user:password@hostname.internal:5432/database" \
  OPENAI_API_KEY="sk-proj-your-key" \
  ANTHROPIC_API_KEY="sk-ant-your-key" \
  AUTH_SECRET_KEY="$(openssl rand -hex 32)" \
  FRONTEND_URL="https://your-app.vercel.app"

# Optional: Set custom demo passwords
fly secrets set \
  DEMO_ADMIN_PASSWORD="your-secure-admin-password" \
  DEMO_USER_PASSWORD="your-secure-user-password"

# Optional: Firecrawl API key
fly secrets set FIRECRAWL_API_KEY="fc-your-key"
```

**Generating a secure AUTH_SECRET_KEY**:
```bash
# On Linux/macOS
openssl rand -hex 32

# On Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### Step 5: Deploy Backend

#### Option A: Using the deployment script (recommended)

```bash
cd backend
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

#### Option B: Manual deployment

```bash
cd backend

# First deployment (creates the app)
fly launch --copy-config --yes

# Subsequent deployments
fly deploy
```

### Step 6: Verify Backend Deployment

```bash
# Check app status
fly status

# View logs
fly logs

# Test health endpoint
curl https://navio-api.fly.dev/health

# Open in browser
fly open
```

Expected health check response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-25T10:30:45.123Z",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    }
  }
}
```

### Step 7: Seed the Database (Optional)

After deployment, you can seed the database with initial data:

```bash
# SSH into the Fly.io machine
fly ssh console

# Run the seeding script
cd /app
python scripts/seed_database.py

# Exit
exit
```

Or use the API endpoint (requires admin authentication):
```bash
# Get authentication token
TOKEN=$(curl -X POST https://navio-api.fly.dev/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your-admin-password" \
  | jq -r '.access_token')

# Trigger seeding
curl -X POST https://navio-api.fly.dev/api/seed \
  -H "Authorization: Bearer $TOKEN"
```

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### Step 2: Deploy Frontend

#### Option A: Using Vercel Dashboard (Recommended for first deployment)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

5. Set Environment Variables:
   - `NEXT_PUBLIC_API_URL` = `https://navio-api.fly.dev`

6. Click "Deploy"

#### Option B: Using Vercel CLI

```bash
cd frontend

# First deployment
vercel

# Production deployment
vercel --prod
```

When prompted:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name: `navio-frontend`
- Directory: `./`
- Override settings? **N**

Set environment variable:
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://navio-api.fly.dev
```

### Step 3: Update Backend CORS

After deploying the frontend, update the backend's `FRONTEND_URL` secret:

```bash
cd backend
fly secrets set FRONTEND_URL="https://your-app.vercel.app"
```

### Step 4: Verify Frontend Deployment

1. Visit your Vercel deployment URL
2. Test the demo page at `/demo`
3. Verify API connectivity by trying to get course recommendations

---

## Part 3: Post-Deployment Configuration

### Custom Domains

#### Backend (Fly.io)

```bash
cd backend

# Add custom domain
fly certs create api.yourdomain.com

# Follow instructions to add DNS records
```

Add DNS record:
- **Type**: CNAME
- **Name**: api
- **Value**: navio-api.fly.dev

#### Frontend (Vercel)

1. Go to Project Settings → Domains
2. Add your domain
3. Configure DNS records as instructed

### SSL Certificates

Both Fly.io and Vercel provide automatic SSL certificates via Let's Encrypt. No additional configuration needed.

### Monitoring Setup

#### Fly.io Monitoring

```bash
# View metrics
fly dashboard metrics

# Set up alerts
fly monitor
```

#### Application Monitoring

Health checks are automatically configured in `fly.toml`:
- Endpoint: `GET /health`
- Interval: 15 seconds
- Timeout: 10 seconds

Access monitoring endpoints:
- Health: `https://navio-api.fly.dev/health`
- Metrics: `https://navio-api.fly.dev/metrics`
- API Docs: `https://navio-api.fly.dev/docs`

---

## Part 4: Scaling and Performance

### Backend Scaling

#### Vertical Scaling (Increase Resources)

Edit `fly.toml`:
```toml
[vm]
  cpu_kind = "shared"
  cpus = 2              # Increase CPUs
  memory_mb = 1024      # Increase memory
```

Then deploy:
```bash
fly deploy
```

#### Horizontal Scaling (Add Machines)

```bash
# Scale to 2 machines
fly scale count 2

# Scale to specific regions
fly scale count 2 --region sjc,iad
```

### Frontend Scaling

Vercel automatically scales based on traffic. No manual configuration needed.

### Database Scaling

```bash
# Scale Postgres
fly postgres update navio-db --vm-size performance-1x
```

---

## Part 5: Maintenance

### Viewing Logs

#### Backend Logs
```bash
cd backend
fly logs

# Follow logs in real-time
fly logs -f

# Filter logs
fly logs --json | jq 'select(.level == "ERROR")'
```

#### Frontend Logs
1. Go to Vercel Dashboard → Project → Logs
2. Or use CLI: `vercel logs <deployment-url>`

### Database Backups

```bash
# Manual backup
fly postgres backup create navio-db

# List backups
fly postgres backup list navio-db

# Restore from backup
fly postgres backup restore navio-db <backup-id>
```

### Updating Secrets

```bash
# Update a single secret
fly secrets set OPENAI_API_KEY="new-key"

# View secret names (not values)
fly secrets list

# Remove a secret
fly secrets unset SECRET_NAME
```

### Rolling Updates

Fly.io performs zero-downtime deployments by default:

```bash
fly deploy --strategy rolling
```

---

## Part 6: Troubleshooting

### Backend Issues

#### App won't start
```bash
# Check logs for errors
fly logs

# Check app status
fly status

# SSH into machine for debugging
fly ssh console
```

#### Database connection fails
```bash
# Verify database is running
fly postgres db list navio-db

# Check connection string
fly secrets list | grep DATABASE_URL

# Test connection manually
fly ssh console
psql $DATABASE_URL -c "SELECT 1"
```

#### Health check failing
```bash
# Check health endpoint directly
curl https://navio-api.fly.dev/health

# View health check logs
fly logs | grep health
```

### Frontend Issues

#### API requests failing
1. Check CORS settings in backend
2. Verify `NEXT_PUBLIC_API_URL` is set correctly
3. Check browser console for errors
4. Test API endpoint directly: `curl https://navio-api.fly.dev/health`

#### Build failures
```bash
# Check build logs in Vercel dashboard
# Or redeploy with verbose logging
vercel --debug
```

### Common Error Solutions

#### Error: "Rate limit exceeded"
- Increase rate limits in `app/core/rate_limit.py`
- Deploy updated configuration

#### Error: "Database connection pool exhausted"
- Scale database: `fly postgres update navio-db --vm-size performance-1x`
- Or increase max connections in PostgreSQL config

#### Error: "CORS policy blocked"
- Update `FRONTEND_URL` secret on Fly.io
- Verify frontend URL matches exactly (including https://)

---

## Part 7: CI/CD Setup (Optional)

### GitHub Actions for Backend

Create `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend to Fly.io

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Fly CLI
        uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy to Fly.io
        run: flyctl deploy --remote-only
        working-directory: ./backend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Set `FLY_API_TOKEN` in GitHub repository secrets:
```bash
# Get token
fly auth token

# Add to GitHub: Settings → Secrets → Actions → New repository secret
```

### Vercel Auto-Deployment

Vercel automatically deploys when you push to your connected Git repository:
- **Production**: Commits to `main` branch
- **Preview**: Pull requests and other branches

Configure in Vercel Dashboard → Project Settings → Git

---

## Part 8: Security Checklist

- [ ] Changed default `AUTH_SECRET_KEY`
- [ ] Changed demo user passwords
- [ ] Set strong database password
- [ ] Enabled HTTPS (automatic on Fly.io and Vercel)
- [ ] Configured CORS to only allow your frontend domain
- [ ] API keys stored as secrets (not in code)
- [ ] Database backups enabled
- [ ] Rate limiting configured
- [ ] Health checks enabled
- [ ] Monitoring and alerts set up

---

## Part 9: Cost Estimation

### Fly.io (Backend)
- **Free tier**: 3 shared-cpu VMs (256MB RAM each)
- **Paid**: $1.94/month per shared-cpu-1x (256MB)
- **Database**: Free tier includes 1 Postgres cluster (1GB storage)
- **Estimated cost**: $0-20/month (depending on scale)

### Vercel (Frontend)
- **Hobby**: Free for personal projects
- **Pro**: $20/month (includes team features)
- **Estimated cost**: $0-20/month

### Third-party APIs
- **OpenAI**: Pay per use (~$0.002/1K tokens)
- **Anthropic**: Pay per use (~$0.003/1K tokens)
- **Estimated cost**: Variable based on usage

**Total estimated monthly cost**: $0-60 for small-scale deployment

---

## Support and Resources

### Documentation
- [Fly.io Docs](https://fly.io/docs/)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

### Getting Help
- Fly.io Community: https://community.fly.io/
- Vercel Discord: https://vercel.com/discord
- GitHub Issues: Open an issue in your repository

---

## Quick Reference Commands

```bash
# Backend (Fly.io)
fly deploy                          # Deploy backend
fly logs                            # View logs
fly ssh console                     # SSH into machine
fly status                          # Check status
fly secrets set KEY=value          # Set secret
fly postgres connect navio-db      # Connect to database

# Frontend (Vercel)
vercel                             # Deploy to preview
vercel --prod                      # Deploy to production
vercel logs                        # View logs
vercel env add                     # Add environment variable

# Database
fly postgres backup create navio-db    # Create backup
fly postgres connect navio-db -d navio # Connect to database
```

---

## Next Steps

After deployment:
1. Test all API endpoints
2. Verify database seeding
3. Test authentication flow
4. Monitor application metrics
5. Set up automated backups
6. Configure custom domains (if desired)
7. Set up monitoring alerts

Happy deploying! 🚀
