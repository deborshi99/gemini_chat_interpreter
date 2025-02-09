from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import shutil
import threading
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

def create_temp_dir():
    temp_dir = f"./temp/{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    logger.info(f"Created temporary directory: {temp_dir}")
    return temp_dir

@app.post("/execute")
async def execute_code(code: str = Form(...), file: UploadFile = None):
    logger.info("Received code execution request")
    temp_dir = create_temp_dir()
    script_path = os.path.join(temp_dir, "script.py")
    
    # Find all PNG filenames in plt.savefig() calls
    savefig_pattern = r"plt\.savefig\(['\"]([\w_]+\.png)['\"]"
    image_paths = re.findall(savefig_pattern, code)
    
    for img_path in image_paths:
        new_path = os.path.join(temp_dir, os.path.basename(img_path))
        code = code.replace(img_path, new_path)
        logger.info(f"Replaced image path: {img_path} -> {new_path}")

    # Save the CSV file if provided
    csv_path = None
    if file:
        csv_path = os.path.join(temp_dir, file.filename)
        logger.info(f"Saving uploaded file to {csv_path}")
        with open(csv_path, "wb") as f:
            content = await file.read()
            f.write(content)
            logger.info(f"File saved successfully: {file.filename}")
        # Save the Python script
        logger.info(f"Saving Python script to {script_path}")
        with open(script_path, "w") as f:
            f.write(code.replace(file.filename, csv_path))
    else:
        logger.info(f"Saving Python script to {script_path}")
        with open(script_path, "w") as f:
            f.write(code)   
    
    
    try:
        # Execute the script
        logger.info("Executing Python script")
        result = subprocess.run(
            ["python", script_path], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        logger.info(f"Script execution completed with return code: {result.returncode}")

        # Find generated images
        logger.info("Searching for generated images")
        image_files = [f for f in os.listdir(temp_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        image_urls = [f"/download/{os.path.basename(temp_dir)}/{img}" for img in image_files]
        logger.info(f"Found {len(image_files)} images: {image_files}")

        # Schedule cleanup
        logger.info(f"Scheduling cleanup for directory: {temp_dir}")
        threading.Thread(target=lambda: cleanup_dir(temp_dir), daemon=True).start()

    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "status": result.returncode,
        "images": image_urls
    }

def cleanup_dir(temp_dir: str):
    # Wait 60 seconds before cleanup
    threading.Event().wait(60)
    logger.info(f"Cleaning up directory: {temp_dir}")
    shutil.rmtree(temp_dir, ignore_errors=True)
    logger.info(f"Cleanup completed for: {temp_dir}")

@app.get("/download/{dir_name}/{file_name}")
def download_file(dir_name: str, file_name: str):
    file_path = f"./temp/{dir_name}/{file_name}"
    logger.info(f"Download request for file: {file_path}")
    if os.path.exists(file_path):
        logger.info(f"Serving file: {file_path}")
        return FileResponse(file_path)
    logger.warning(f"File not found: {file_path}")
    return {"error": "File not found"}