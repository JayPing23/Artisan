# Local Testing Guide 🧪

## 🚀 Quick Local Setup

### Prerequisites
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **8GB+ RAM** available for Docker
- **Git** for version control

### 🎯 One-Click Start (Recommended)

**Windows:**
```bash
# Double-click or run:
start-artisan.bat
```

**Linux/Mac:**
```bash
# Make executable and run:
chmod +x start-artisan.sh
./start-artisan.sh
```

### 🔧 Manual Setup (Alternative)

**Step 1: Start All Services**
```bash
# Start everything with Docker
docker-compose up --build -d

# Install Code Llama model (first time only)
docker-compose exec -T ollama ollama pull codellama
```

**Step 2: Access Application**
- Open http://localhost:8000
- Test with prompt: "a low-poly rocket ship"

### 📋 Useful Commands
```bash
# View all logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Check service status
docker-compose ps
```

## 🧪 Testing Scenarios

### 1. Basic Functionality Test
```bash
# Test API endpoints
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a simple cube"}'

# Check status
curl http://localhost:8000/status/YOUR_TASK_ID
```

### 2. Model Generation Test
**Test Prompts:**
- "a low-poly tree"
- "a stylized sword"
- "a cartoon house"
- "a futuristic car"
- "a medieval castle"

**Expected Results:**
- Task submission returns task_id
- Status polling shows progress
- Model file is generated (.glb)
- 3D viewer displays the model

### 3. Error Handling Test
**Test Cases:**
- Empty prompt
- Very long prompt
- Special characters in prompt
- Network interruption during generation
- Invalid task_id in status check

### 4. Performance Test
```bash
# Monitor resource usage
docker stats

# Check service logs
ollama list
docker-compose logs redis
```

## 🔧 Development Workflow

### Real-time Editing
```bash
# FastAPI auto-reloads on file changes
# Edit main.py, worker.py, etc. and see changes immediately

# For frontend changes, refresh browser
# Edit index.html, script.js, style.css
```

### Debugging Tips
```bash
# View FastAPI logs
uvicorn main:app --reload --log-level debug

# View Celery logs
celery -A worker worker --loglevel=debug

# Check Docker logs
docker-compose logs -f [service_name]
```

### Common Issues & Solutions

#### Issue: Ollama Connection Failed
```bash
# Check if Ollama is running
ollama list

# Start Ollama service (if not running)
ollama serve

# Check if model is available
ollama list | grep codellama
```

#### Issue: Celery Worker Not Starting
```bash
# Check Redis connection
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Check Celery logs
celery -A worker worker --loglevel=info
```

#### Issue: Model Generation Fails
```bash
# Check Blender installation in worker
docker-compose exec worker blender --version

# Check worker logs
docker-compose logs worker

# Verify model directory permissions
docker-compose exec worker ls -la /app/models
```

## 📊 Testing Checklist

### Core Functionality
- [ ] FastAPI server starts without errors
- [ ] Celery worker connects to Redis
- [ ] Ollama responds to API calls
- [ ] Task submission works
- [ ] Status polling works
- [ ] Model generation completes
- [ ] 3D viewer displays models
- [ ] Model files are saved correctly

### User Interface
- [ ] Web interface loads properly
- [ ] Form submission works
- [ ] Loading states display correctly
- [ ] Error messages are clear
- [ ] 3D viewer controls work
- [ ] Responsive design on mobile

### Performance
- [ ] Generation time is reasonable (30-60 seconds)
- [ ] Memory usage stays within limits
- [ ] CPU usage is acceptable
- [ ] No memory leaks during testing
- [ ] Multiple generations work sequentially

### Error Handling
- [ ] Invalid prompts show appropriate errors
- [ ] Network errors are handled gracefully
- [ ] Service failures are reported clearly
- [ ] Recovery from errors works
- [ ] Logs provide useful debugging info

## 🔄 Iterative Development

### Making Changes
1. **Edit code** in your preferred editor
2. **Test changes** immediately (FastAPI auto-reloads)
3. **Check logs** for any errors
4. **Verify functionality** in browser
5. **Commit changes** when satisfied

### Testing New Features
```bash
# Add new endpoint in main.py
@app.get("/test")
async def test_endpoint():
    return {"status": "working"}

# Test immediately
curl http://localhost:8000/test
```

### Database/Storage Testing
```bash
# Check model storage
ls -la models/

# Test file permissions
touch models/test.glb
rm models/test.glb
```

## 🚀 Preparing for Production

### Performance Optimization
```bash
# Monitor resource usage
htop
docker stats

# Optimize Docker images
docker-compose build --no-cache

# Test with production settings
docker-compose -f docker-compose.prod.yml up
```

### Security Testing
```bash
# Test input validation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<script>alert(\"xss\")</script>"}'

# Test rate limiting (if implemented)
# Test authentication (if implemented)
```

### Load Testing
```bash
# Test multiple concurrent requests
for i in {1..5}; do
  curl -X POST http://localhost:8000/generate \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"test model $i\"}" &
done
```

## 📝 Development Notes

### File Structure for Local Development
```
Artisan/
├── main.py              # FastAPI app (edit here)
├── worker.py            # Celery worker (edit here)
├── index.html           # Frontend (edit here)
├── script.js            # Frontend logic (edit here)
├── style.css            # Styling (edit here)
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Local services (Redis, Ollama)
└── models/              # Generated models (created automatically)
```

### Useful Commands
```bash
# Start all services
docker-compose up -d

# View all logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up --build

# Clean up
docker-compose down -v
docker system prune -f
```

---

**Happy Testing!** 🎨 Once you're satisfied with local functionality, you can deploy to Oracle Cloud using the deployment scripts we created. 