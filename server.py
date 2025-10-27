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

def get_name(uploaded_file_path: Path) -> str:
    with uploaded_file_path.open("r") as f:
        for line in f:
            if line.startswith("name:"):
                name = line.split(":")[1].strip()
                break
        else:
            name = None
    return name

def calculate_filename(name: str | None) -> str:
    if not name:
        return 'Resume.pdf'
    parts = name.split()
    first_name = parts[0]
    if len(parts) > 1:
        last_name = parts[-1]
        filename = f"{first_name}-{last_name}-Resume.pdf"
    else:
        filename = f"{first_name}-Resume.pdf"
    return filename

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

        name = get_name(uploaded_file_path)
        filename = calculate_filename(name)

        # Schedule the temp dir to be deleted after response is sent
        background_tasks.add_task(shutil.rmtree, temp_path)

        # Send response
        return FileResponse(
            path=output_pdf_path,
            media_type="application/pdf",
            filename=filename,
            background=background_tasks
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    run("server:app", host="0.0.0.0", port=8000, reload=True)
