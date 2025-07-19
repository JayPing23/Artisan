import os
import subprocess
import requests
import json
from celery import Celery

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery_app.task(name="worker.generate_model_task")
def generate_model_task(prompt: str, task_id: str):
    # 1. Generate Blender script with Ollama
    meta_prompt = f"""
You are an expert Blender Python script generator. Your sole purpose is to create a Python script that can be executed with Blender's command-line interface to generate a 3D model based on a user's prompt.

**User Prompt:** '{prompt}'

**Constraints & Requirements:**
- You must only output a single, raw JSON object. Do not include any other text, explanations, or markdown formatting like ```json.
- The JSON object must contain a single key: "python_script".
- The value of "python_script" must be a string containing the complete, executable Blender Python script.
- The script must be self-contained and use only the standard Blender Python API (bpy).
- The script must first clear the default Blender scene (cube, light, camera).
- The script must generate a model matching the user's prompt, preferably with a low-poly aesthetic.
- The script MUST export the final model as a GLB file to a specific path. Use the placeholder 'EXPORT_PATH' for the filepath. The application will replace this placeholder before execution.
  Example export line: `bpy.ops.export_scene.gltf(filepath='EXPORT_PATH', export_format='GLB')`

**Example of a valid JSON output:**
{{
  "python_script": "import bpy\\n\\n# Clear existing objects\\n...\\n\\n# Create model\\n...\\n\\n# Export model\\nbpy.ops.export_scene.gltf(filepath='EXPORT_PATH', export_format='GLB')"
}}

Now, generate the JSON output for the user prompt provided above.
"""
    
    ollama_url = "http://host.docker.internal:11434/api/generate"
    payload = {
        "model": "codellama",
        "prompt": meta_prompt,
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(ollama_url, json=payload, timeout=120)
        response.raise_for_status()
        
        response_data = response.json()
        
        generated_json_str = response_data.get("response")
        if not generated_json_str:
            raise ValueError("Ollama response did not contain 'response' field.")
            
        script_data = json.loads(generated_json_str)
        blender_script = script_data.get("python_script")

        if not blender_script or not isinstance(blender_script, str):
            raise ValueError("Generated JSON from Ollama does not contain a valid 'python_script' string.")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to connect to Ollama API at {ollama_url}. Ensure Ollama is running on the host machine. Error: {e}")
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        raise Exception(f"Failed to parse Ollama response. It might be malformed. Error: {e}")

    # 2. Run Blender script
    output_dir = "/app/models"
    os.makedirs(output_dir, exist_ok=True)
    model_filename = f"{task_id}.glb"
    export_path = os.path.join(output_dir, model_filename)

    final_script = blender_script.replace("EXPORT_PATH", export_path)

    script_filename = f"/tmp/{task_id}.py"
    with open(script_filename, "w") as f:
        f.write(final_script)

    try:
        blender_executable = "/usr/local/blender/blender"
        subprocess.run(
            [blender_executable, "--background", "--python", script_filename],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        blender_error_log = f"Blender STDOUT: {e.stdout}\\nBlender STDERR: {e.stderr}"
        raise Exception(f"Blender script execution failed: {blender_error_log}")
    finally:
        if os.path.exists(script_filename):
            os.remove(script_filename)

    return {"status": "completed", "model_filename": model_filename}
