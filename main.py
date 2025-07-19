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

@app.get("/")
async def read_root():
    return FileResponse("index.html")

@app.post("/generate")
async def generate_model(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Submit a new model generation task"""
    try:
        task_id = str(uuid.uuid4())
        
        # Submit task to Celery
        task = celery_app.send_task(
            "worker.generate_model_task",
            args=[request.prompt, task_id]
        )
        
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a generation task"""
    try:
        # For now, we'll use a simple approach - check if the model file exists
        # In a production system, you'd want to track task status in Redis or a database
        model_path = f"/app/models/{task_id}.glb"
        
        if os.path.exists(model_path):
            return {"status": "SUCCESS", "result": {"model_filename": f"{task_id}.glb"}}
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