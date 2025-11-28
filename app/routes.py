from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.orchestrator import start_flow
from app.memory.session_store import SessionStore
from app.logger import logger
import uuid
import os


router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
STATUS = {}
session_store = SessionStore()


@router.get("/ui", response_class=HTMLResponse)
def ui_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/run", response_class=HTMLResponse)
async def run_pipeline(request: Request, topic: str = Form(...), notes: str = Form("")):
    job_id = str(uuid.uuid4())
    payload = {"topic": topic, "notes": notes}
    STATUS[job_id] = {"status": "queued", "progress": 0}
# run synchronously for simplicity (blocking)
    result = start_flow(job_id, payload, STATUS, session_store)


# result contains: plan, summary, mcqs, publish_path, summary_chars, mcq_count
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "result": result, "topic": topic}
)


@router.get('/download/md')
def download_md(path: str):
    if not os.path.exists(path):
        return RedirectResponse(url='/ui')
    return FileResponse(path, filename=os.path.basename(path), media_type='text/markdown')


@router.get('/download/html')
def download_html(path: str):
    if not os.path.exists(path):
        return RedirectResponse(url='/ui')
    return FileResponse(path, filename=os.path.basename(path), media_type='text/html')


@router.get('/download/pdf')
def download_pdf(path: str):
    if not os.path.exists(path):
        return RedirectResponse(url='/ui')
    return FileResponse(path, filename=os.path.basename(path), media_type='application/pdf')