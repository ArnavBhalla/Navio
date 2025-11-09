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

# Enable pgvector
psql navio -c "CREATE EXTENSION vector;"
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
```env
DATABASE_URL=postgresql://localhost:5432/navio
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

## 3. Seed Database

```bash
# Still in backend/ directory with venv activated
python scripts/seed_database.py
```

You should see:
```
✓ Database initialized with pgvector extension
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

### "ModuleNotFoundError: No module named 'pgvector'"
```bash
pip install pgvector
```

### "relation 'embeddings' does not exist"
```bash
python scripts/seed_database.py
```

### "OpenAI API key not found"
Check your `backend/.env` file has the correct API keys

### Frontend can't connect to backend
Make sure `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`

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
