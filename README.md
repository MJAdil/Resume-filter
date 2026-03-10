# Resume Filter - Production-Ready Candidate Ranking Platform

An intelligent job matching system that evaluates candidates across multiple platforms using ML-based semantic matching and adaptive scoring algorithms.

## Credits

This project is a modernized fork of the original [Filter](https://github.com/yaseen2402/filter) project by [yaseen2402](https://github.com/yaseen2402). We've migrated it from Flask + file-based storage to FastAPI + MongoDB with production-ready features.

## What's New in This Version

-  **FastAPI Backend**: Migrated from Flask to FastAPI with async support
-  **MongoDB Integration**: Replaced file-based storage with MongoDB for scalability
-  **Production-Ready**: Health checks, structured logging, error handling, CORS
-  **Async Operations**: All database and HTTP operations are async for better performance
-  **Profile Scraping**: Automated scraping from GitHub, LeetCode, Codeforces, LinkedIn
-  **Multi-Criteria Ranking**: Adaptive weight redistribution with confidence scoring
-  **Semantic Matching**: BGE-small-en-v1.5 embeddings for intelligent job-candidate matching

## Key Features

- **Multi-Platform Aggregation**: Collects data from GitHub, LeetCode, Codeforces, LinkedIn, and resumes
- **Adaptive Ranking Algorithm**: Fairly evaluates candidates with varying data completeness
- **Confidence-Based Scoring**: Provides confidence scores showing ranking reliability
- **AI-Powered Embeddings**: Uses BGE-small-en-v1.5 model (384-dimensional) for semantic matching
- **Real-Time Processing**: Instant candidate evaluation and ranking
- **RESTful API**: Well-documented FastAPI endpoints with automatic OpenAPI docs

## Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Database**: MongoDB with Motor (async driver)
- **ML Model**: BAAI/bge-small-en-v1.5 (384-dimensional embeddings)
- **HTTP Client**: httpx (async HTTP requests)
- **Validation**: Pydantic v2 models

### Frontend
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **PDF Processing**: pdf-parse, pdfjs-dist

## Prerequisites

- Python 3.8+
- Node.js 22.11+
- MongoDB (local or Atlas)
- npm or yarn

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/MJAdil/filter.git
cd filter/filter
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/resume_filter

# Optional API Keys
GITHUB_TOKEN=your_github_token_here
LINKEDIN_API_KEY=your_linkedin_api_key_here
LINKEDIN_PROVIDER=scrapingdog

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

### 4. Start MongoDB

**Local MongoDB:**
```bash
# Windows (if installed via winget or installer)
# MongoDB service should start automatically

# Mac (via Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

**MongoDB Atlas:**
- Use the connection string from your Atlas cluster in `MONGODB_URI`

### 5. Frontend Setup

```bash
# From the filter/filter directory
npm install
```

## Running the Application

You need to run TWO services simultaneously:

### Terminal 1 - Backend (FastAPI)
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

python run_server.py
```
Runs at: http://localhost:8000
API Docs: http://localhost:8000/docs

### Terminal 2 - Frontend (Vite Dev Server)
```bash
# From filter/filter directory
npm run dev
```
Runs at: http://localhost:5173

## API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Health Check
```http
GET /health
```
Returns system status and database connectivity.

#### Create Candidate Profile
```http
POST /api/candidates
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "resume_data": {
    "extractedText": "Resume text...",
    "skills": ["Python", "FastAPI"],
    "education": [...],
    "experience": [...]
  }
}
```

#### Fetch Profile Data from Platforms
```http
POST /api/fetch-profile-data
Content-Type: application/json

{
  "username": "john_doe",
  "urls": {
    "github": "https://github.com/username",
    "leetcode": "https://leetcode.com/u/username",
    "codeforces": "https://codeforces.com/profile/username",
    "linkedin": "https://www.linkedin.com/in/username"
  }
}
```

#### Create Job Posting
```http
POST /api/jobs
Content-Type: application/json

{
  "job_title": "Senior Python Developer",
  "company": "TechCorp",
  "location": "Remote",
  "job_type": "Full-time",
  "description": "Job description...",
  "requirements": "Required skills...",
  "salary": "$120k - $150k"
}
```

#### Match Candidates to Job
```http
POST /api/match-candidates
Content-Type: application/json

{
  "job_id": "uuid-here",
  "top_k": 10
}
```

#### Rank Candidates (Multi-Criteria)
```http
POST /api/rank-candidates
Content-Type: application/json

{
  "job_id": "uuid-here",
  "top_k": 10
}
```

## Project Structure

```
filter/
├── backend/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   ├── models/              # Pydantic models
│   │   │   ├── candidate.py
│   │   │   ├── job.py
│   │   │   └── requests.py
│   │   └── routes/              # API endpoints
│   │       ├── candidates.py
│   │       ├── jobs.py
│   │       ├── matching.py
│   │       └── profiles.py
│   ├── services/
│   │   ├── database.py          # MongoDB connection
│   │   ├── embeddings.py        # BGE model service
│   │   ├── ranking.py           # Multi-criteria ranking
│   │   └── scraper_async.py     # Profile scraping
│   ├── utils/
│   │   └── logging.py           # Structured logging
│   ├── config.py                # Configuration management
│   ├── run_server.py            # Server entry point
│   ├── requirements.txt         # Python dependencies
│   └── test_*.py                # Test files
├── src/
│   ├── components/
│   │   ├── CompanyDashboard.tsx
│   │   └── JobSeekerDashboard.tsx
│   └── utils/
│       └── pdfParser.ts
├── package.json
├── vite.config.ts
└── README.md
```

## Testing

All endpoints have comprehensive test coverage:

```bash
cd backend

# Test database connection
python test_db_connection.py

# Test embeddings
python test_embeddings.py

# Test API endpoints
python test_api.py
python test_jobs_api.py
python test_matching_api.py
python test_ranking_api.py
python test_profile_fetch_api.py
python test_health_check.py
```

## Adaptive Ranking Algorithm

The system uses a sophisticated multi-criteria ranking algorithm:

### Platform Scoring

1. **GitHub Score** (0-100)
   - Public repos, stars, followers
   - Normalized with logarithmic scaling

2. **LeetCode Score** (0-100)
   - Easy: 1 point, Medium: 3 points, Hard: 5 points
   - Normalized to 0-100 range

3. **Codeforces Score** (0-100)
   - Rating and contest participation
   - Normalized based on rating tiers

4. **LinkedIn Score** (0-100)
   - Profile completeness (experience + education)

5. **Resume Score** (0-100)
   - Skills count, education level, experience years

### Adaptive Weight Redistribution

**Default Weights:**
- GitHub: 25%
- LeetCode: 20%
- Codeforces: 15%
- LinkedIn: 15%
- Resume: 25%

When platforms are missing, their weights are redistributed proportionally to available platforms.

### Confidence Scoring

```
confidence = 0.70 + (0.30 × completeness_ratio)
```

- 5 platforms: confidence = 1.00 (100%)
- 4 platforms: confidence = 0.94 (94%)
- 3 platforms: confidence = 0.88 (88%)
- 2 platforms: confidence = 0.82 (82%)
- 1 platform: confidence = 0.76 (76%)

## MongoDB Schema

### Candidates Collection
```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String,
  phone: String,
  resume_data: Object,
  embedding: Array<Float>,
  profile_data: {
    github: Object,
    leetcode: Object,
    codeforces: Object,
    linkedin: Object
  },
  created_at: DateTime,
  updated_at: DateTime
}
```

### Jobs Collection
```javascript
{
  _id: ObjectId,
  job_id: String (unique),
  job_title: String,
  company: String,
  location: String,
  job_type: String,
  description: String,
  requirements: String,
  salary: String,
  embedding: Array<Float>,
  created_at: DateTime
}
```

## Configuration

### Adjust Ranking Weights

Edit `backend/services/ranking.py`:

```python
DEFAULT_WEIGHTS = {
    "github": 0.25,
    "leetcode": 0.20,
    "codeforces": 0.15,
    "linkedin": 0.15,
    "resume": 0.25
}
```

### Customize Confidence Formula

Edit `backend/services/ranking.py`:

```python
confidence = 0.70 + (0.30 * completeness_ratio)
```

## Development

### Run Linter
```bash
npm run lint
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Deployment

### Vercel (Planned)
- Frontend: Automatic deployment from main branch
- Backend: Serverless functions
- MongoDB: Atlas connection

Configuration files for Vercel deployment are in progress.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project maintains the same license as the original [Filter](https://github.com/yaseen2402/filter) project.

## Acknowledgments

- Original project by [yaseen2402](https://github.com/yaseen2402)
- BGE embedding model by BAAI
- FastAPI framework by Sebastián Ramírez
- MongoDB and Motor driver

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review test files for usage examples

---

**Note**: This is a modernized version focused on production readiness and scalability. The original project can be found at https://github.com/yaseen2402/filter
