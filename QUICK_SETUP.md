# Quick Setup Guide

## For New Users Cloning This Repository

### 1. Prerequisites
- Python 3.8+
- Node.js 22.11+
- MongoDB (local or Atlas)

### 2. Backend Setup

```bash
cd filter/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your MongoDB URI and API keys
# For local MongoDB: mongodb://localhost:27017/resume_filter
# For Atlas: mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/resume_filter
```

### 3. Frontend Setup

```bash
cd filter
npm install
```

### 4. Start MongoDB

**Local MongoDB:**
```bash
# Windows: Service should start automatically
# Mac: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

**MongoDB Atlas:**
- Create a free cluster at https://www.mongodb.com/cloud/atlas
- Get your connection string
- Add it to `.env` file

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd filter/backend
venv\Scripts\activate  # Windows
python run_server.py
```
Backend runs at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd filter
npm run dev
```
Frontend runs at: http://localhost:5173

### 6. Verify Installation

Open http://localhost:8000/docs to see the API documentation.

### 7. Run Tests (Optional)

```bash
cd filter/backend
python test_db_connection.py
python test_api.py
python test_health_check.py
```

## Common Issues

### MongoDB Connection Error
- Make sure MongoDB is running
- Check your `MONGODB_URI` in `.env`
- For local MongoDB, use: `mongodb://localhost:27017/resume_filter`

### Port Already in Use
- Backend (8000): Stop other processes using port 8000
- Frontend (5173): Stop other Vite dev servers

### Module Not Found
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### API Key Issues
- GitHub and LinkedIn API keys are optional
- System works without them (with reduced functionality)
- Get GitHub token: https://github.com/settings/tokens
- Get LinkedIn API key: https://scrapingdog.com/

## Next Steps

1. Upload a resume via the Job Seeker Dashboard
2. Create a job posting via the Company Dashboard
3. View matched candidates with rankings
4. Explore the API at http://localhost:8000/docs

## Need Help?

- Check the main README.md for detailed documentation
- Review test files for usage examples
- Open an issue on GitHub
