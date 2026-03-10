# GitHub Upload Instructions

## Step 1: Create a New Repository on GitHub

1. Go to https://github.com/MJAdil?tab=repositories
2. Click "New" button (green button)
3. Repository name: `resume-filter` (or your preferred name)
4. Description: "Production-ready resume filtering system with FastAPI + MongoDB"
5. Choose: Public or Private
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Update Git Remote

Run these commands in the `filter` directory:

```bash
# Remove the old remote
git remote remove origin

# Add your new repository as origin
git remote add origin https://github.com/MJAdil/resume-filter.git

# Verify the remote
git remote -v
```

## Step 3: Stage and Commit Changes

```bash
# Add all new and modified files
git add .

# Commit with a descriptive message
git commit -m "Modernize to FastAPI + MongoDB with production features

- Migrate from Flask to FastAPI with async support
- Replace file-based storage with MongoDB
- Add health checks, structured logging, CORS
- Implement profile scraping from GitHub, LeetCode, Codeforces, LinkedIn
- Add multi-criteria ranking with adaptive weights
- Include comprehensive test suite
- Update documentation with credits to original project"
```

## Step 4: Push to GitHub

```bash
# Push to main branch
git push -u origin main
```

If you encounter authentication issues:
- Use GitHub Personal Access Token instead of password
- Or use GitHub CLI: `gh auth login`

## Step 5: Verify Upload

1. Go to https://github.com/MJAdil/resume-filter
2. Verify all files are uploaded
3. Check that README.md displays correctly
4. Verify .gitignore is working (no .env, venv, node_modules, etc.)

## Files That Will Be Uploaded

### Backend (FastAPI)
- `backend/api/` - FastAPI application and routes
- `backend/services/` - Database, embeddings, ranking, scraping
- `backend/utils/` - Logging utilities
- `backend/config.py` - Configuration management
- `backend/run_server.py` - Server entry point
- `backend/requirements.txt` - Python dependencies
- `backend/test_*.py` - Test files
- `backend/.env.example` - Example environment variables

### Frontend
- `src/` - React components
- `public/` - Static assets
- `package.json` - Node dependencies
- `vite.config.ts` - Vite configuration
- `tsconfig.json` - TypeScript configuration

### Documentation
- `README.md` - Main documentation with credits
- `.gitignore` - Git ignore rules

### Data (if you want to include sample data)
- `data/candidates/` - Sample candidate profiles
- `data/jobs/` - Sample job postings

## Files That Will Be Ignored

Thanks to `.gitignore`:
- `venv/` - Python virtual environment
- `node_modules/` - Node dependencies
- `.env` - Environment variables (sensitive)
- `__pycache__/` - Python cache
- `.kiro/` - Kiro specs (optional)
- `.vscode/` - IDE settings

## Optional: Add Topics to Repository

After uploading, add topics to your repository for better discoverability:
1. Go to your repository on GitHub
2. Click "Add topics" (near the About section)
3. Suggested topics:
   - `fastapi`
   - `mongodb`
   - `machine-learning`
   - `resume-parser`
   - `candidate-ranking`
   - `python`
   - `react`
   - `typescript`
   - `job-matching`

## Optional: Update Repository Settings

1. Go to Settings > General
2. Add a description
3. Add a website (if you deploy it)
4. Enable/disable features (Issues, Wiki, Projects, etc.)

## Troubleshooting

### If you get "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/MJAdil/resume-filter.git
```

### If you get authentication errors
```bash
# Use GitHub CLI
gh auth login

# Or use Personal Access Token
# Generate at: https://github.com/settings/tokens
# Use token as password when prompted
```

### If you want to exclude .kiro/ specs
The `.gitignore` already includes `.kiro/`, so they won't be uploaded.
If you want to include them, remove that line from `.gitignore`.

## Next Steps After Upload

1. Add a GitHub Actions workflow for CI/CD (optional)
2. Set up branch protection rules (optional)
3. Add collaborators if needed
4. Create issues for future enhancements
5. Add a LICENSE file if needed
6. Consider adding badges to README (build status, license, etc.)

---

**Note**: Make sure to never commit the `.env` file with sensitive credentials!
