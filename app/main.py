from fastapi import FastAPI, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.orchestrator import start_flow
from app.memory.session_store import SessionStore
from app.logger import logger
from app.routes import router as ui_router

import uuid


# ------------------------------------------------------------------
# SINGLE FASTAPI APP
# ------------------------------------------------------------------
app = FastAPI(title="StudyMate Agent - A2A Demo")

# CORS for browser form submit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="app/templates")

session_store = SessionStore()
STATUS = {}
LAST_OUTPUT = {}   # <- IMPORTANT


# ------------------------------------------------------------------
# HOME PAGE (index.html)
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ------------------------------------------------------------------
# RUN PIPELINE (Fixes 422 error)
# ------------------------------------------------------------------
@app.post("/run")
async def run_pipeline(
    request: Request,
    topic: str = Form(...),
    notes: str = Form("")
):
    logger.info(f"POST /run → topic={topic} | notes_len={len(notes)}")

    payload = {"topic": topic.strip(), "notes": notes.strip()}

    result = start_flow("job1", payload, {}, session_store)

    # now show dashboard on browser instead of JSON
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "topic": topic,
            "result": result
        }
    )


# ------------------------------------------------------------------
# DASHBOARD PAGE
# ------------------------------------------------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "result": LAST_OUTPUT
    })


# ------------------------------------------------------------------
# LONG TASK (NOT USED BY UI, ONLY CLI)
# ------------------------------------------------------------------
@app.post("/start")
async def start_task(payload: dict, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    STATUS[job_id] = {"status": "queued", "progress": 0}

    logger.info(f"[ASYNC START] Job {job_id}")

    background_tasks.add_task(start_flow, job_id, payload, STATUS, session_store)

    return {"job_id": job_id, "status_url": f"/status/{job_id}"}


@app.get("/status/{job_id}")
async def status(job_id: str):
    return STATUS.get(job_id, {"error": "job not found"})


# Include UI routes for downloads
app.include_router(ui_router)
