from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import uuid
from celery.result import AsyncResult
from worker import celery_app

app = FastAPI(title="Artisan: AI Text-to-3D Generator")

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

class GenerateRequest(BaseModel):
    prompt: str
    style: str = ''
    environment: str = ''
    lighting: str = ''
    color_scheme: str = ''
    special_features: str = ''
    scale: str = ''
    level_of_detail: str = ''
    material_appearance: str = ''
    symmetry: str = ''
    animation: str = ''
    output_format: str = ''
    other_requirements: str = ''
    quality: str = 'low'

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.post("/generate")
async def generate_model(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Submit a new model generation task"""
    try:
        task_id = str(uuid.uuid4())
        # Submit task to Celery with all fields
        task = celery_app.send_task(
            "worker.generate_model_task",
            args=[
                request.prompt,
                task_id,
                request.quality,
                request.style,
                request.environment,
                request.lighting,
                request.color_scheme,
                request.special_features,
                request.scale,
                request.level_of_detail,
                request.material_appearance,
                request.symmetry,
                request.animation,
                request.output_format,
                request.other_requirements
            ]
        )
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a generation task"""
    try:
        # First, try to get the task result from Celery
        # We need to find the actual Celery task ID that was used
        # For now, let's check if the model file exists as a fallback
        model_path = f"/app/models/{task_id}.glb"
        
        if os.path.exists(model_path):
            # Verify file is not empty
            if os.path.getsize(model_path) > 0:
                return {"status": "SUCCESS", "result": {"model_filename": f"{task_id}.glb"}}
            else:
                return {"status": "FAILED", "error": "Generated file is empty"}
        else:
            return {"status": "PENDING"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/{task_id}")
async def get_model(task_id: str):
    """Serve the generated 3D model file"""
    try:
        model_path = f"/app/models/{task_id}.glb"
        
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Check if file is not empty
        if os.path.getsize(model_path) == 0:
            raise HTTPException(status_code=500, detail="Generated model file is empty")
        
        return FileResponse(
            model_path,
            media_type="model/gltf-binary",
            headers={"Content-Disposition": f"attachment; filename={task_id}.glb"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 