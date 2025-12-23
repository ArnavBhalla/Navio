# Quick Start Guide

Get Navio running in 5 minutes.

## Prerequisites Check

```bash
python3 --version  # Should be 3.10+
node --version     # Should be 18+
psql --version     # Should be 14+
```

## 1. Set Up PostgreSQL

```bash
# Create database
createdb navio

# Note: pgvector extension is NOT required - embeddings are stored as PostgreSQL arrays
# and similarity is computed in Python
```

## 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

**Edit `backend/.env` with your keys:**

**Important:** Replace `YOUR_USERNAME` and `YOUR_PASSWORD` with your actual PostgreSQL credentials.

```env
# Format: postgresql://username:password@localhost:5432/navio
# If you don't know your PostgreSQL password, see troubleshooting section below
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/navio
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Auth / JWT (change these for your environment)
AUTH_SECRET_KEY=super-secret-change-me
AUTH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Demo users (override as you like)
DEMO_ADMIN_USERNAME=admin
DEMO_ADMIN_PASSWORD=admin123
DEMO_USER_USERNAME=demo
DEMO_USER_PASSWORD=demo123
```

**Quick check:** Your username is usually your system username. To find it, run: `whoami`

## 3. Seed Database

```bash
# Still in backend/ directory with venv activated
python scripts/seed_database.py
```

You should see:
```
✓ Database initialized
✓ Seeded 6 programs
✓ Seeded 60 courses with embeddings
✓ Seeded 27 requirements with embeddings
✓ Seeded 4 track requirements
```

## 4. Start Backend

```bash
# Still in backend/
uvicorn app.main:app --reload
```

Backend running at http://localhost:8000
Test it: http://localhost:8000/docs

## 5. Start Frontend

**Open a new terminal:**

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Frontend running at http://localhost:3000

## 6. Test It!

1. Open http://localhost:3000
2. Select "Rice" → "Bioengineering"
3. Click "Continue to Advisor"
4. Add completed courses: "MATH 212", "BIOE 252"
5. Select track: "Pre-Med"
6. Click "Get Recommendations"

You should see course recommendations with citations!

## Troubleshooting

### "password authentication failed" or "fe_sendauth: no password supplied"

**Option 1: Add password to DATABASE_URL (Recommended)**

Update your `backend/.env` file to include your PostgreSQL password:
```env
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/navio
```

If you don't know your PostgreSQL password, you can reset it:
```bash
# Connect as postgres superuser (you'll be prompted for postgres password)
psql -U postgres

# Once connected, run:
ALTER USER YOUR_USERNAME WITH PASSWORD 'your_new_password';
\q

# Then update .env with the new password
```

**Option 2: Set up passwordless authentication (Advanced)**

Edit PostgreSQL config to allow trust authentication for local connections:
```bash
# Edit pg_hba.conf (usually at /opt/homebrew/var/postgresql@14/pg_hba.conf)
# Ensure these lines exist:
# local   all             all                                     trust
# host    all             all             127.0.0.1/32            trust

# Then restart PostgreSQL:
brew services restart postgresql@14
```

### "relation 'embeddings' does not exist"
```bash
python scripts/seed_database.py
```

### "OpenAI API key not found"
Check your `backend/.env` file has the correct API keys

### Frontend can't connect to backend
Make sure `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`

### "OperationalError: connection to server failed"
- Make sure PostgreSQL is running: `brew services start postgresql@14` (or your version)
- Verify the database exists: `psql -l | grep navio`
- Check your `DATABASE_URL` format matches your PostgreSQL setup

## Next Steps

- Try different test scenarios (see README.md)
- Explore the API docs at http://localhost:8000/docs
- Customize the seed data in `backend/data/seed/`
- Modify the prompts in `backend/app/services/prompts.py`

## Stop Services

```bash
# Stop backend: Ctrl+C in backend terminal
# Stop frontend: Ctrl+C in frontend terminal

# Deactivate Python venv
deactivate
```
