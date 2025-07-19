# Artisan: AI Text-to-3D Generator

Artisan is a **free, powerful, and locally-run** Text-to-3D generation tool that democratizes 3D content creation. Transform simple text prompts into game-ready 3D models using AI-powered Blender script generation.

## 🎯 Features

- **🆓 Completely Free** - No API costs or external dependencies
- **🏠 Local Processing** - Everything runs on your machine
- **🎮 Game-Ready Assets** - Generate low-poly models perfect for games
- **⚡ Real-time Generation** - Watch your models come to life
- **🌐 Modern Web Interface** - Beautiful, responsive UI
- **📦 Containerized** - Easy deployment with Docker

## 🏗️ Architecture

Artisan uses a sophisticated AI-to-Blender-Script pipeline that combines the power of local AI models with professional 3D software:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Celery        │
│   (HTML/JS/CSS) │◄──►│   Web Server    │◄──►│   Worker        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis         │    │   Blender       │
                       │   (Message      │    │   (3D Model     │
                       │    Broker)      │    │    Generation)  │
                       └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Ollama        │    │   model-data    │
                       │   (Code Llama)  │    │   (Volume)      │
                       └─────────────────┘    └─────────────────┘
```

### Service Components

| Service | Technology | Purpose |
|---------|------------|---------|
| **`web`** | FastAPI, Uvicorn | Serves the web interface and API endpoints |
| **`worker`** | Celery, Python | Processes generation tasks and runs Blender |
| **`ollama`** | Ollama, Code Llama | Generates Blender Python scripts from prompts |
| **`redis`** | Redis | Message broker and task queue |
| **`model-data`** | Docker Volume | Persistent storage for generated models |

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **8GB+ RAM** - Required for Ollama and Blender
- **10GB+ Free Disk Space** - For models and Docker images

### Local Installation & Deployment

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Artisan
   ```

2. **Start the Application**
   ```bash
   docker-compose up --build
   ```

3. **Install the AI Model** (First Run Only)
   ```bash
   docker-compose exec ollama ollama pull codellama
   ```

4. **Access the Application**
   - Open http://localhost:8000 in your browser
   - Enter a prompt like "a low-poly rocket ship"
   - Click Generate and wait for your 3D model!

### ☁️ Cloud Deployment

#### Oracle Cloud Free Tier (Recommended)

Oracle Cloud Free Tier is perfect for hosting Artisan with generous resources:
- **4 ARM VMs with 24GB RAM each** (Always Free)
- **200GB storage** and **10TB bandwidth**
- **No expiration** - truly free forever

**Quick Deploy:**
```bash
# 1. Create Oracle Cloud account at cloud.oracle.com
# 2. Launch an ARM-based VM (VM.Standard.A1.Flex)
# 3. SSH into your instance and run:
wget https://raw.githubusercontent.com/your-repo/Artisan/main/deploy-oracle.sh
chmod +x deploy-oracle.sh
./deploy-oracle.sh
```

**Manual Deploy:**
See [oracle-deployment.md](oracle-deployment.md) for detailed step-by-step instructions.

#### Other Cloud Providers

- **AWS Free Tier** - 12 months free, then pay-as-you-go
- **Google Cloud Free Tier** - $300 credit for 90 days
- **Azure Free Tier** - $200 credit for 30 days
- **DigitalOcean** - $200 credit for 60 days

## 📖 Usage Guide

### Generating Your First Model

1. **Enter a Descriptive Prompt**
   - Be specific: "a stylized ancient sword with glowing runes"
   - Use descriptive terms: "low-poly", "cartoon", "realistic"
   - Include details: "with wings", "made of metal", "with spikes"

2. **Wait for Generation**
   - The system will show real-time status updates
   - Generation typically takes 30-60 seconds
   - You can view the model immediately when ready

3. **Interact with Your Model**
   - Rotate, zoom, and pan the 3D viewer
   - Download the GLB file for use in other applications
   - Generate variations with different prompts

### Example Prompts

- "a low-poly spaceship with glowing engines"
- "a cartoon-style treasure chest with gold coins"
- "a stylized medieval castle on a hill"
- "a futuristic robot with articulated arms"
- "a magical crystal staff with floating gems"

## 🔧 Configuration

### Environment Variables

The application uses these environment variables (configured in docker-compose.yml):

```yaml
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Customization

- **Port**: Change the web service port in `docker-compose.yml`
- **Model**: Switch to different Ollama models by modifying `worker.py`
- **Blender Version**: Update the Blender version in `Dockerfile.worker`

## 🛠️ Development

### Project Structure

```
Artisan/
├── main.py              # FastAPI application
├── worker.py            # Celery worker with Blender integration
├── index.html           # Web interface
├── script.js            # Frontend JavaScript
├── style.css            # Styling
├── requirements.txt     # Python dependencies
├── Dockerfile           # Web service container
├── Dockerfile.worker    # Worker service container
├── docker-compose.yml   # Service orchestration
└── README.md           # This file
```

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Services Individually**
   ```bash
   # Start Redis
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Start Ollama
   docker run -d -p 11434:11434 ollama/ollama:latest
   
   # Run FastAPI
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Run Celery Worker
   celery -A worker worker --loglevel=info
   ```

## 🐛 Troubleshooting

### Common Issues

**Ollama Fails to Start**
- Ensure you have at least 8GB RAM available
- Check Docker has enough memory allocated
- Verify the ollama service is running: `docker-compose logs ollama`

**Models Don't Generate**
- Check worker logs: `docker-compose logs worker`
- Verify Code Llama is installed: `docker-compose exec ollama ollama list`
- Ensure Blender is working: `docker-compose exec worker blender --version`

**Web Interface Not Loading**
- Check web service logs: `docker-compose logs web`
- Verify port 8000 is not in use
- Try accessing http://localhost:8000 directly

### Useful Commands

```bash
# View all service logs
docker-compose logs

# Restart a specific service
docker-compose restart worker

# Stop all services
docker-compose down

# Clean up volumes (removes all generated models)
docker-compose down -v

# Rebuild containers
docker-compose up --build --force-recreate
```

## 🔮 Future Roadmap

### Planned Features

- **🎨 Advanced Materials** - PBR textures and material generation
- **🦴 Basic Rigging** - Skeletal animation support
- **👥 User Accounts** - Model gallery and history
- **🔄 Iterative Generation** - Modify existing models
- **☁️ Cloud Deployment** - Public hosting options
- **🎯 Custom Models** - Fine-tuned specialized models

### Contributing

We welcome contributions! Please see our contributing guidelines for:
- Bug reports and feature requests
- Code contributions and pull requests
- Documentation improvements
- Testing and validation

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Ollama** - For providing the local LLM infrastructure
- **Blender** - For the powerful 3D creation platform
- **FastAPI** - For the modern Python web framework
- **Celery** - For robust task queue management

---

**Artisan** - Democratizing 3D content creation, one prompt at a time. 🎨✨
