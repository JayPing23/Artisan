#!/bin/bash

echo "========================================"
echo "   Artisan 3D Generator - Starting"
echo "========================================"
echo

echo "[1/4] Building and starting all services..."
docker-compose up --build -d

echo
echo "[2/4] Waiting for services to start..."
sleep 10

echo
echo "[3/4] Installing Code Llama model (first time only)..."
docker-compose exec -T ollama ollama pull codellama

echo
echo "[4/4] Checking service status..."
docker-compose ps

echo
echo "========================================"
echo "   Artisan is now running!"
echo "========================================"
echo
echo "🌐 Open your browser and go to:"
echo "   http://localhost:8000"
echo
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart"
echo
echo "🎨 Happy 3D generating!"
echo 