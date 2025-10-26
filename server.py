from uvicorn import run
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from yamldoc import yamldoc
import shutil
import tempfile

app = FastAPI()

@app.post("/render")
async def render(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)

        uploaded_file_path = temp_path / "input.yaml"
        with uploaded_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_pdf_path = temp_path / "output.pdf"

        template_path = Path("template.html")

        yamldoc(uploaded_file_path, template_path, output_pdf_path)

        # Schedule the temp dir to be deleted after response is sent
        background_tasks.add_task(shutil.rmtree, temp_path)

        # Send response
        return FileResponse(
            path=output_pdf_path,
            media_type="application/pdf",
            filename="Resume.pdf",
            background=background_tasks
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    run("server:app", host="0.0.0.0", port=8000, reload=True)
