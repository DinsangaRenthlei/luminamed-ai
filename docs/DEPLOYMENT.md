# LuminaMed AI - Deployment Guide

**Target Platforms**: Railway, Render, AWS, Self-Hosted  
**Estimated Setup Time**: 30 minutes (Railway) to 2 hours (AWS)  
**Skill Level**: Intermediate

---

## 🚀 Quick Deploy (Railway - Recommended)

### Why Railway?

- ✅ Fastest deployment (5 minutes)
- ✅ Free $5/month credit (500 hours)
- ✅ Automatic HTTPS
- ✅ Built-in databases (PostgreSQL, Redis)
- ✅ GitHub auto-deploy
- ✅ Zero configuration needed

### Deployment Steps

**1. Prepare Your Repository**
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit: LuminaMed AI platform"

# Push to GitHub
gh repo create luminamed-ai --public --source=. --remote=origin
git push -u origin main
```

**2. Create Railway Account**

- Go to: https://railway.app
- Sign up with GitHub
- Verify email

**3. Create New Project**

- Click **"New Project"**
- Select **"Deploy from GitHub repo"**
- Choose your `luminamed-ai` repository
- Railway will detect your services automatically

**4. Add Required Services**

Click **"+ New"** to add:

**Service 1: Redis**
- Template: Redis
- No configuration needed

**Service 2: Qdrant**
- Template: Qdrant
- No configuration needed

**Service 3: PostgreSQL** (future use)
- Template: PostgreSQL
- Note the connection string

**5. Configure Environment Variables**

For each application service, add these variables:

**API Service:**
```bash
GOOGLE_API_KEY=your-google-api-key
MODEL_NAME=models/gemini-flash-latest
REDIS_URL=${{Redis.REDIS_URL}}
QDRANT_URL=${{Qdrant.QDRANT_URL}}
ENVIRONMENT=production
DEBUG=false
```

**Radiologist Portal:**
```bash
API_URL=${{API.RAILWAY_PUBLIC_DOMAIN}}
```

**Patient Portal:**
```bash
NEXT_PUBLIC_API_URL=${{API.RAILWAY_PUBLIC_DOMAIN}}
```

**6. Deploy Services**

Railway auto-deploys on push! Each service gets a URL:
```
API: https://luminamed-api.up.railway.app
Radiologist: https://luminamed-radiologist.up.railway.app
Patient: https://luminamed-patient.up.railway.app
```

**7. Load Initial Knowledge**
```bash
# SSH into API service or run locally
python services/rag/load_knowledge.py
```

**8. Verify Deployment**

Test each endpoint:
- https://luminamed-api.up.railway.app/health
- https://luminamed-api.up.railway.app/docs
- https://luminamed-radiologist.up.railway.app
- https://luminamed-patient.up.railway.app

---

## 🐳 Docker Production Deployment

### Create Production Dockerfiles

**File: `Dockerfile.api`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY apps/api ./apps/api
COPY packages ./packages
COPY services ./services

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**File: `apps/radiologist/Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install streamlit and dependencies
COPY apps/radiologist/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY apps/radiologist/ ./

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**File: `apps/consumer/Dockerfile`**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY apps/consumer/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application
COPY apps/consumer/ ./

# Build Next.js app
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### Production Docker Compose

**File: `docker-compose.prod.yml`**
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      - redis
      - qdrant
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  radiologist:
    build:
      context: ./apps/radiologist
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
    restart: always

  patient:
    build:
      context: ./apps/consumer
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      - api
    restart: always

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant-data:/qdrant/storage
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    restart: always

  orthanc:
    image: jodogne/orthanc-plugins:latest
    ports:
      - "8042:8042"
    volumes:
      - orthanc-data:/var/lib/orthanc/db
      - ./infra/docker/orthanc/orthanc.json:/etc/orthanc/orthanc.json:ro
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infra/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./infra/nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
      - radiologist
      - patient
    restart: always

volumes:
  qdrant-data:
  redis-data:
  orthanc-data:
```

---

## ☁️ Cloud Deployment Options

### Option 1: Railway (Easiest)

**Cost**: $5 free credit → ~$20/month production

**Pros:**
- Automatic scaling
- Built-in monitoring
- Zero DevOps
- Custom domains included

**Setup:**
1. Connect GitHub repo
2. Add environment variables
3. Deploy with one click

### Option 2: Render

**Cost**: Free tier → $25/month production

**Pros:**
- True free tier (750 hours/month)
- Docker support
- Auto-deploy from GitHub

**Cons:**
- Free tier spins down after 15 min inactivity
- 30s cold start time

### Option 3: AWS (Production-Grade)

**Cost**: ~$50-200/month

**Services Used:**
- ECS Fargate (containers)
- Application Load Balancer
- RDS PostgreSQL
- ElastiCache Redis
- S3 (DICOM storage)
- CloudWatch (monitoring)

**Pros:**
- HIPAA-eligible with BAA
- Complete control
- Professional-grade

**Cons:**
- Complex setup
- Higher cost
- Requires AWS expertise

---

## 🔒 Production Checklist

### Security

- [ ] HTTPS enabled (SSL certificates)
- [ ] API authentication (JWT tokens)
- [ ] CORS restricted to known domains
- [ ] API keys in environment variables (never in code)
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (use ORMs)
- [ ] XSS prevention (sanitize outputs)

### Performance

- [ ] Redis caching enabled
- [ ] Database connection pooling
- [ ] Static file CDN (Cloudflare)
- [ ] Image optimization
- [ ] Gzip compression
- [ ] HTTP/2 enabled

### Monitoring

- [ ] Health check endpoints
- [ ] Prometheus metrics collection
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Log aggregation (Loki/CloudWatch)
- [ ] Alerts configured (PagerDuty/Slack)

### Compliance

- [ ] HIPAA compliance checklist
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Data retention policies defined
- [ ] Audit logging enabled
- [ ] PHI handling procedures documented

---

## 🔧 Configuration Management

### Environment-Specific Configs

**Development (.env.development):**
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
API_HOST=0.0.0.0
```

**Production (.env.production):**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
ALLOWED_HOSTS=luminamed.app,*.railway.app
```

---

## 📊 Performance Optimization

### API Optimization
```python
# Enable caching
@lru_cache(maxsize=128)
def get_embedder():
    return MedicalEmbedder()

# Connection pooling
redis_pool = redis.ConnectionPool(...)

# Async where possible
async def process_image(image: bytes):
    ...
```

### Database Optimization
```sql
-- Indexes for fast queries
CREATE INDEX idx_study_date ON reports(study_date);
CREATE INDEX idx_modality ON reports(modality);
```

---

## 🆘 Troubleshooting

### Common Issues

**1. API won't start**
```bash
# Check logs
docker logs luminamed-api

# Common causes:
# - Missing environment variables
# - Port already in use
# - Database connection failed
```

**2. Qdrant connection failed**
```bash
# Verify Qdrant is running
docker ps | grep qdrant

# Check logs
docker logs luminamed-qdrant
```

**3. High latency**
```bash
# Check Redis cache hit rate
redis-cli INFO stats | grep hits

# Monitor API metrics
curl http://localhost:8000/metrics
```

---

## 📞 Support

For deployment issues:
- GitHub Issues: https://github.com/crillypienaah/luminamed-ai/issues
- Email: pienaah.c@northeastern.edu
- Discord: 

---

**Last Updated**: December 6, 2025