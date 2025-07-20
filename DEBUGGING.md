# Artisan AI Text-to-3D Generator - Debugging Guide

## Quick Debugging

### 1. Run the Debug Script
```bash
python debug_artisan.py
```

This comprehensive script will test all components and provide detailed feedback.

### 2. Manual Testing Steps

#### Check Docker Services
```bash
docker-compose ps
```

#### Test Web Interface
```bash
curl http://localhost:8000
```

#### Test Ollama Connection
```bash
curl http://localhost:11434/api/tags
```

#### Check Worker Logs
```bash
docker-compose logs worker
```

#### Check Web Logs
```bash
docker-compose logs web
```

## Common Issues and Solutions

### Issue: "Pending" Status Never Changes

**Symptoms:**
- Frontend shows "PENDING" indefinitely
- Status polling continues without success
- No error messages in logs

**Diagnosis:**
1. Check if worker completed the task:
   ```bash
   docker-compose logs worker --tail=20
   ```

2. Check if model file was created:
   ```bash
   docker-compose exec web ls -la /app/models/
   ```

3. Test Blender installation:
   ```bash
   docker-compose exec worker python test_blender.py
   ```

**Solutions:**
- If worker completed but no file exists: Blender script failed silently
- If worker never completed: Check Ollama connection and model availability
- If file exists but status still pending: Check file permissions and size

### Issue: Ollama Connection Failed

**Symptoms:**
- 500 Internal Server Error
- "Failed to connect to Ollama API" error

**Solutions:**
1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

2. Check if model is available:
   ```bash
   ollama list
   ```

3. Pull the required model:
   ```bash
   ollama pull codellama:7b
   ```

### Issue: Blender Script Execution Failed

**Symptoms:**
- Worker completes but no model file is created
- Blender error messages in logs

**Solutions:**
1. Test Blender installation:
   ```bash
   docker-compose exec worker python test_blender.py
   ```

2. Check Blender executable:
   ```bash
   docker-compose exec worker ls -la /usr/local/blender/blender
   ```

3. Verify system libraries:
   ```bash
   docker-compose exec worker ldd /usr/local/blender/blender
   ```

### Issue: Docker Services Not Starting

**Symptoms:**
- `docker-compose up` fails
- Port conflicts or resource issues

**Solutions:**
1. Stop all containers:
   ```bash
   docker-compose down
   ```

2. Remove volumes (if needed):
   ```bash
   docker-compose down -v
   ```

3. Rebuild containers:
   ```bash
   docker-compose build --no-cache
   ```

4. Start services:
   ```bash
   docker-compose up -d
   ```

## Testing Individual Components

### Test Ollama Response Format
```bash
docker-compose exec worker python test_ollama.py
```

### Test Blender File Creation
```bash
docker-compose exec worker python test_blender.py
```

### Test Full Workflow
```bash
python debug_artisan.py
```

## Log Analysis

### Worker Logs
Look for:
- Task received messages
- Ollama API responses
- Blender execution results
- File creation confirmations

### Web Logs
Look for:
- Status polling requests
- File serving attempts
- Error responses

### Redis Logs
Look for:
- Connection issues
- Task queue status

## Performance Optimization

### Memory Issues
- Increase Docker memory limits
- Use smaller models (7B instead of 13B)
- Monitor memory usage during generation

### Timeout Issues
- Increase timeout values in worker.py
- Check system resources
- Monitor Ollama response times

## Troubleshooting Checklist

- [ ] Docker Desktop is running
- [ ] All containers are started (`docker-compose ps`)
- [ ] Ollama is running (`ollama serve`)
- [ ] Required model is downloaded (`ollama list`)
- [ ] Web interface is accessible (`http://localhost:8000`)
- [ ] Worker can connect to Ollama
- [ ] Blender is properly installed in worker container
- [ ] Models directory is writable
- [ ] Redis is responding
- [ ] Celery worker is active

## Getting Help

If you're still experiencing issues:

1. Run the debug script and share the output
2. Check the logs for specific error messages
3. Verify your system meets the requirements
4. Try the manual testing steps above

## System Requirements

- Docker Desktop with at least 8GB RAM allocated
- Windows 10/11 or macOS
- At least 16GB system RAM
- Stable internet connection for model downloads 