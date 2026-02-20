import logging
import time
import os
import asyncio
from typing import List

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings
from models import SearchResult
from services.db_service import db_service
from services.data_loader import data_loader
from services.search_engine import search_engine
from services.setup_service import setup_service

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/favicon.ico")
async def favicon():
    return FileResponse('examen.png')

@app.on_event("startup")
async def startup_event():
    port = os.getenv("PORT", "8000")
    logger.info("Application starting up...")
    logger.info(f"🚀 App accessible at: http://localhost:{port}")
    
    # Ensure seed directory exists
    seed_dir = os.path.dirname(settings.CSV_FILE)
    if not os.path.exists(seed_dir):
        logger.info(f"Seed directory {seed_dir} not found. Creating it...")
        os.makedirs(seed_dir, exist_ok=True)
    
    # Check if data exists
    if not os.path.exists(settings.CSV_FILE):
        logger.warning(f"Data file not found at {settings.CSV_FILE}. Waiting for setup via Frontend...")
        return

    # If data exists, trying loading
    try:
        conn = db_service.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM schools")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            logger.info("Database empty. Triggering initial load from CSV...")
            data_loader.load_data()
        else:
            logger.info(f"Database already contains {count} records.")
        
        # Build Index
        logger.info("Hydrating In-Memory Search Index...")
        schools = list(db_service.get_all_schools())
        search_engine.index_data(schools)
        logger.info("Startup sequence complete. API is ready.")
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)

# --- Setup Endpoints ---
@app.get("/setup/status")
def get_setup_status():
    return setup_service.get_status()

@app.post("/setup/start")
async def start_setup(background_tasks: BackgroundTasks):
    if setup_service.status["is_running"]:
        logger.warning("Setup start requested but already running.")
        return {"message": "Setup already running"}
        
    logger.info("Initiating Setup Process via API.")
    background_tasks.add_task(run_setup_process)
    return {"message": "Setup started"}

async def run_setup_process():
    # 1. Setup Files (Download/Merge) - Non-blocking
    await setup_service.start_setup()
    
    # 2. Load DB & Index (Blocking CPU/Disk I/O) - Must offload
    if setup_service.status["stage"] == "completed":
        logger.info("Setup phase complete. Triggering Database Ingestion...")
        loop = asyncio.get_event_loop()
        try:
             # Run sync load_data in thread pool
             await loop.run_in_executor(None, _load_and_index_sync)
             
             logger.info("Full System Setup Complete!")
        except Exception as e:
            logger.error(f"Post-setup loading failed: {e}", exc_info=True)
            setup_service.status["stage"] = "error"
            setup_service.status["message"] = f"DB Load Error: {str(e)}"

def _load_and_index_sync():
    """Helper to run blocking load/index steps in executor"""
    # Refresh DB
    db_service.clear_data()
    data_loader.load_data()
    
    # Refresh Index
    logger.info("Re-indexing data...")
    schools = list(db_service.get_all_schools())
    search_engine.index_data(schools)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}

@app.get("/search", response_model=List[SearchResult], response_model_by_alias=False)
def search_schools(response: Response, query: str = Query(..., min_length=1), limit: int = 3):
    # Lazy Load fallback
    if not search_engine.documents:
         logger.info("Search requested but index empty. Attempting lazy load...")
         conn = db_service.get_connection()
         cursor = conn.cursor()
         cursor.execute("SELECT count(*) FROM schools")
         if cursor.fetchone()[0] > 0:
             schools = list(db_service.get_all_schools())
             search_engine.index_data(schools)

    start = time.perf_counter()
    results = search_engine.search(query, limit=limit)
    took = (time.perf_counter() - start) * 1000 # ms
    
    logger.info(f"Search query='{query}' limit={limit} results={len(results)} took={took:.3f}ms")
    
    from fastapi import Response
    response.headers["X-Server-Time-MS"] = str(took)
    return results

@app.post("/data/refresh")
def refresh_data():
    logger.info("Manual data refresh requested.")
    try:
        db_service.clear_data()
        data_loader.load_data()
        
        # Re-index
        schools = list(db_service.get_all_schools())
        search_engine.index_data(schools)
        
        return {"status": "success", "message": "Data reloaded and re-indexed"}
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
