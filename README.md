# Navio - AI Academic Advisor

An AI-powered course recommendation system that helps students plan their academic journey. Built with FastAPI, Next.js, and powered by GPT-4o and Claude Sonnet 4.5.

## Features

- **Smart Course Recommendations**: AI-powered suggestions based on your progress
- **RAG-Enhanced Context**: Vector database retrieval for accurate, citation-backed advice
- **Multi-University Support**: Rice, UT Austin, and Stanford (6 programs total)
- **Track Guidance**: Pre-med, pre-law, pre-grad, and pre-MBA pathways
- **Prerequisite Validation**: Automatic checking of course prerequisites
- **Interactive UI**: Modern, responsive Next.js interface

## Architecture

### Backend (FastAPI + Python)
- **FastAPI** for REST API endpoints
- **PostgreSQL** with **pgvector** for vector similarity search
- **SQLAlchemy** for ORM and database management
- **OpenAI** (GPT-4o) for course recommendations
- **Anthropic** (Claude Sonnet 4.5) for catalog summarization
- **LangChain** for RAG pipeline orchestration

### Frontend (Next.js 14 + TypeScript)
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **React** for interactive components

### Data
- Seed JSON files for 6 programs (Rice BioE/CS, UT Austin BME/CS, Stanford BioE/CS)
- Vector embeddings for courses and requirements
- Track requirements for career pathways

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 14+** with pgvector extension
- **OpenAI API Key**
- **Anthropic API Key**

## Quick Start

### 1. Clone and Setup

```bash
cd Navio
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys and database URL
```

**Required `.env` variables:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/navio
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Database Setup

```bash
# Install PostgreSQL and create database
createdb navio

# Enable pgvector extension (in psql)
psql navio
CREATE EXTENSION vector;
\q

# Seed database with course data and generate embeddings
python scripts/seed_database.py
```

This will:
- Create all tables with pgvector support
- Load 6 programs, 50+ courses, and requirements
- Generate embeddings for RAG retrieval

### 4. Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 5. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Usage

1. **Select University and Major**
   - Choose from Rice, UT Austin, or Stanford
   - Select your major (Bioengineering or Computer Science)

2. **Enter Your Progress**
   - Add completed courses using the typeahead search
   - Select a career track (optional): pre-med, pre-law, pre-grad, pre-mba
   - Adjust target credit load (12-21 credits)

3. **Get Recommendations**
   - Click "Get Recommendations"
   - View AI-generated course suggestions with:
     - Course code and title
     - Reasoning for recommendation
     - Prerequisites status
     - Requirements fulfilled
     - Citation links to source documents

4. **Provide Feedback**
   - Rate recommendations (helpful/not helpful)
   - Submit comments for improvements

## API Endpoints

### `POST /api/recommend`
Generate course recommendations

**Request:**
```json
{
  "university": "Rice",
  "program_id": "rice-bioe-2025",
  "track": "pre-med",
  "completed": ["MATH 212", "BIOE 252"],
  "credits_target": 15,
  "preferences": {}
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "code": "BIOE 372",
      "title": "Systems Physiology",
      "reason": "Core BIOE requirement, prerequisite satisfied",
      "fulfills": ["BIOE core"],
      "prereq_ok": true,
      "citations": ["https://ga.rice.edu/..."]
    }
  ],
  "notes": ["BIOE 310 includes lab component"],
  "assumptions": [],
  "warnings": []
}
```

### `GET /api/search`
Search courses by code or title

**Query Parameters:**
- `program_id`: Program to search within
- `q`: Search query
- `limit`: Max results (default: 10)

### `POST /api/seed`
Reload database from seed files (development only)

## Testing Scenarios

The brief includes 4 test scenarios to validate the system:

### 1. Rice BioE - Lab Load Note
```json
{
  "program_id": "rice-bioe-2025",
  "completed": ["MATH 212", "BIOE 252"],
  "credits_target": 15
}
```
Expected: BIOE 372 and BIOE 310 recommended with notes about lab load

### 2. Stanford CS - Pre-Grad Track
```json
{
  "program_id": "stanford-cs-2025",
  "completed": ["CS 103", "MATH 51"],
  "track": "pre-grad",
  "credits_target": 15
}
```
Expected: Algorithms, probability, and research courses

### 3. UT Austin BME - Pre-Med Track
```json
{
  "program_id": "utexas-bme-2025",
  "completed": ["CH 301", "PHY 303K"],
  "track": "pre-med",
  "credits_target": 15
}
```
Expected: Organic chemistry, biochemistry, and writing course

### 4. Missing Prerequisites
```json
{
  "program_id": "rice-cs-2025",
  "completed": [],
  "credits_target": 15
}
```
Expected: Warnings for advanced courses, foundational courses recommended

## Project Structure

```
Navio/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Config, database
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic (RAG, AI)
│   │   └── main.py          # FastAPI app
│   ├── data/seed/           # JSON seed data
│   ├── scripts/             # Utility scripts
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # React components
│   ├── lib/                 # Utilities
│   └── package.json
└── README.md
```

## Data Schema

### Programs
6 programs across 3 universities, each with catalog URL and version year

### Courses
50+ courses with:
- Code, title, credits
- Prerequisites (as array)
- Terms offered
- Tags for track matching
- Source URLs

### Requirements
Logical requirement trees:
- `AND`: All courses required
- `OR`: One of multiple options
- `ELECTIVE_GROUP`: Minimum count from list
- `COURSE`: Single course requirement

### Track Requirements
Career track guidance with "buckets":
- Minimum course counts per category
- Tag-based matching
- Disclaimers for verification

## Future Enhancements

### Phase 2: Web Scraping (Playwright + Firecrawl)
- Real-time catalog scraping from university websites
- Automated course data updates
- Claude Sonnet 4.5 for catalog summarization

### Phase 3: Additional Features
- Save plans to localStorage
- Import from unofficial transcripts
- Multi-semester planning
- Popularity hints ("common path" badges)
- Export to PDF

## Deployment

### Backend (Fly.io)
```bash
fly launch
fly secrets set OPENAI_API_KEY=...
fly secrets set ANTHROPIC_API_KEY=...
fly deploy
```

### Frontend (Vercel)
```bash
vercel
# Set NEXT_PUBLIC_API_URL to your Fly.io backend URL
```

## Contributing

This is a demo project. For production use:
- Add authentication
- Implement rate limiting
- Add comprehensive error handling
- Add automated testing
- Implement audit logging

## License

MIT License - See LICENSE file

## Acknowledgments

- Built on the Navio Demo Build Brief
- Powered by OpenAI GPT-4o and Anthropic Claude Sonnet 4.5
- Course data structured from public university catalogs

---

**Disclaimer**: This is an unofficial academic advisor. Always verify course requirements and prerequisites with your department and official university resources.
# Navio
