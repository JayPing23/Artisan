# Artisan: AI Text-to-3D Generator

Artisan is a full-stack application that transforms natural language prompts into 3D models using a local AI model and Blender. It provides a simple web interface to enter a prompt and view the generated model.

## Architecture

The application is containerized using Docker and Docker Compose, consisting of three main services:

-   **`web`**: A FastAPI server that serves the frontend, provides API endpoints for job management, and communicates with the worker via Redis.
-   **`worker`**: A Celery worker that listens for generation tasks. It calls a local LLM (via Ollama) to generate a Blender Python script and then executes that script in a headless Blender instance to create the 3D model.
-   **`redis`**: A Redis instance that acts as the message broker for Celery.

A shared Docker volume (`model-data`) is used to persist the generated models and make them accessible to the web server.

## Prerequisites

Before you begin, ensure you have the following installed on your host machine:

1.  **Docker and Docker Compose**: Required to build and run the containerized application stack.
2.  **Ollama and the `codellama` model**: Follow the detailed setup guide below.

### Setting Up Ollama: A Step-by-Step Guide

Artisan relies on a locally-running Ollama instance to generate Blender scripts. It is **critical** that Ollama is installed and serving the `codellama` model on your host machine *before* you start the Docker application.

**Step 1: Download and Install Ollama**

Download the appropriate version for your operating system from the official website: [ollama.com](https://ollama.com/).

-   [Download for macOS](https://ollama.com/download)
-   [Download for Windows (Preview)](https://ollama.com/download/windows)
-   [Download for Linux](https://ollama.com/download/linux)

Follow the installation instructions provided on the website. For macOS and Windows, run the downloaded installer. For Linux, the typical installation command is:
curl -fsSL https://ollama.com/install.sh | sh
