# SLR Agentic Platform - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide walks you through setting up and starting the SLR Agentic Platform service.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.9+** (`python --version`)
- **pip** (Python package manager)
- **Git** (for cloning)
- **~2GB disk space** (for dependencies)
- **Internet connection** (for PubMed API)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/SuyeshaMitra/SLR-Agentic-Platform.git
cd SLR-Agentic-Platform
```

---

## Step 2: Create Virtual Environment

### On Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### On Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

---

## Step 3: Install Dependencies

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed aiohttp-3.8.5 pydantic-settings-2.1.0 scikit-learn-1.3.2 ...
```

---

## Step 4: Configure Environment (Optional but Recommended)

Create a `.env` file in the `backend/` directory:

```bash
cd backend
cat > .env << EOF
# PubMed Configuration
PUBMED_EMAIL=your-email@example.com
PUBMED_API_KEY=your-optional-api-key

# Application
DEBUG=True
LOG_LEVEL=INFO

# Database (for future use)
DATABASE_URL=postgresql://user:password@localhost/slr_db
NEO4J_URI=bolt://localhost:7687
EOF
```

---

## Step 5: Start the Service

### Option A: Development Mode (Hot Reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Output you should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Option B: Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option C: Using Gunicorn (Recommended for Production)

```bash
pip install gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Step 6: Verify Service is Running

Open your browser or use curl:

### Check Health
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"ok","service":"slr-backend"}
```

### View API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Step 7: Test the Service

### Test 1: Start SLR Job

```bash
curl -X POST http://localhost:8000/api/v1/slr/start \
  -H "Content-Type: application/json" \
  -d '{
    "disease": "Type 2 Diabetes",
    "study_type": "randomized controlled trial",
    "max_results": 100
  }'
```

**Expected response:**
```json
{
  "job_id": "abc12345",
  "status": "STARTED",
  "criteria": {
    "disease": "Type 2 Diabetes",
    "study_type": "randomized controlled trial",
    "max_results": 100
  },
  "total_studies": 0,
  "included_studies": 0,
  "excluded_studies": 0
}
```

### Test 2: Chat Interface

```bash
curl -X POST http://localhost:8000/api/v1/slr/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "Start a systematic review for Type 2 Diabetes"}'
```

### Test 3: Check Job Status

```bash
curl http://localhost:8000/api/v1/slr/status/abc12345
```

### Test 4: Get Results

```bash
curl http://localhost:8000/api/v1/slr/results/abc12345
```

---

## Common Issues & Solutions

### Issue 1: "Port 8000 already in use"

**Solution**: Use a different port
```bash
uvicorn app.main:app --reload --port 8001
```

Or kill the process:

**On Linux/macOS:**
```bash
lsof -i :8000
kill -9 <PID>
```

**On Windows (PowerShell):**
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess
Stop-Process -Id <PID> -Force
```

### Issue 2: "ModuleNotFoundError"

**Solution**: Make sure virtual environment is activated
```bash
# Check if (venv) prefix appears in terminal
which python  # Should show path inside venv/

# If not, activate it:
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate.bat  # Windows
```

### Issue 3: "PubMed API connection timeout"

**Solution**: Check internet connection and try again
```bash
# Test PubMed connectivity
curl https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
```

### Issue 4: "pydantic.errors.PydanticImportError"

**Solution**: Upgrade pydantic
```bash
pip install --upgrade pydantic pydantic-settings
```

---

## Docker Setup (Alternative)

If you prefer to use Docker:

```bash
# Build image
docker build -t slr-agentic-platform backend/

# Run container
docker run -p 8000:8000 slr-agentic-platform
```

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Using the API

### Python Client Example

```python
import httpx
import asyncio

async def test_slr():
    client = httpx.AsyncClient()
    
    # Start job
    response = await client.post(
        "http://localhost:8000/api/v1/slr/start",
        json={
            "disease": "Type 2 Diabetes",
            "study_type": "clinical trial",
            "max_results": 1000
        }
    )
    job_data = response.json()
    print(f"Job started: {job_data['job_id']}")
    
    # Check status
    status = await client.get(
        f"http://localhost:8000/api/v1/slr/status/{job_data['job_id']}"
    )
    print(f"Status: {status.json()}")

asyncio.run(test_slr())
```

### JavaScript/Node.js Example

```javascript
const fetch = require('node-fetch');

async function testSLR() {
    // Start job
    const startResponse = await fetch('http://localhost:8000/api/v1/slr/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            disease: 'Type 2 Diabetes',
            study_type: 'clinical trial',
            max_results: 1000
        })
    });
    
    const job = await startResponse.json();
    console.log(`Job started: ${job.job_id}`);
    
    // Check status
    const statusResponse = await fetch(
        `http://localhost:8000/api/v1/slr/status/${job.job_id}`
    );
    const status = await statusResponse.json();
    console.log(status);
}

testSLR();
```

---

## Monitoring & Logs

### View Real-time Logs

**In development mode**, logs appear in terminal. For production:

```bash
# Save logs to file
uvicorn app.main:app --log-config logging.yaml > app.log 2>&1 &

# View logs
tail -f app.log

# Search for errors
grep ERROR app.log
```

### Health Check Script

```bash
#!/bin/bash
# save as check-health.sh

echo "Checking SLR Platform Health..."
curl -s http://localhost:8000/health | jq .
echo "API Docs available at http://localhost:8000/docs"
```

---

## Next Steps

1. **Read Implementation Summary**: See `IMPLEMENTATION_SUMMARY.md` for architecture details
2. **Explore API**: Visit http://localhost:8000/docs for interactive API docs
3. **Configure Database**: Set up PostgreSQL + Neo4j (optional)
4. **Deploy**: Use Docker or cloud platform (AWS/GCP/Azure)
5. **Monitor**: Set up logging and metrics collection

---

## Production Deployment

### Using Systemd (Linux)

Create `/etc/systemd/system/slr-platform.service`:

```ini
[Unit]
Description=SLR Agentic Platform
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/slr-platform/backend
Environment="PATH=/var/www/slr-platform/venv/bin"
ExecStart=/var/www/slr-platform/venv/bin/gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl start slr-platform
sudo systemctl enable slr-platform  # Auto-start on boot
sudo systemctl status slr-platform
```

### Using AWS ECS

See `docker-compose.yml` example:

```yaml
version: '3.8'

services:
  slr-backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PUBMED_EMAIL=${PUBMED_EMAIL}
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: slr_db
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

Deploy:

```bash
docker-compose up -d
```

---

## Troubleshooting

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG

# Or via environment
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload
```

### Test PubMed API Directly

```bash
# Search for Type 2 Diabetes studies
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=type%202%20diabetes&retmax=10&rettype=json"
```

### Performance Check

```bash
# Load test with 100 concurrent requests
ab -n 1000 -c 100 http://localhost:8000/health
```

---

## Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **Architecture**: See `IMPLEMENTATION_SUMMARY.md`
- **Issues**: GitHub Issues page
- **Email**: support@example.com

---

**Version**: 1.0.0  
**Last Updated**: Dec 29, 2025  
**Status**: ✅ Ready for Production
