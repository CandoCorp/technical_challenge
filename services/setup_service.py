import os
import requests
import asyncio
import logging
from config import settings

logger = logging.getLogger(__name__)

SEARCH_URLS = {
    "sl051bai": "https://nces.ed.gov/ccd/data/zip/sl051bai_csv.zip",
    "sl051bkn": "https://nces.ed.gov/ccd/data/zip/sl051bkn_csv.zip",
    "sl051bow": "https://nces.ed.gov/ccd/data/zip/sl051bow_csv.zip"
}

class SetupService:
    def __init__(self):
        self.status = {
            "is_running": False,
            "stage": "idle", 
            "message": "Ready to start.",
            "progress": {}, # For downloads: file_key -> {current, total}
            "db_progress": {"current": 0, "total": 0, "pct": 0}, # For DB insertion
            "files": {} 
        }
    
    def get_status(self):
        self._update_file_stats()
        return self.status

    def update_db_progress(self, current_bytes, total_bytes, rows_loaded=0):
        """Called by data_loader to update ingestion progress"""
        self.status["stage"] = "populating_db"
        pct = 0
        if total_bytes > 0:
            pct = int((current_bytes / total_bytes) * 100)
        
        self.status["db_progress"] = {
            "current": current_bytes,
            "total": total_bytes,
            "pct": pct,
            "rows_loaded": rows_loaded
        }
        self.status["message"] = f"Populating Database: {pct}% ({rows_loaded} rows)"

    def _update_file_stats(self):
        if not os.path.exists(settings.DATA_DIR):
             return
        
        files_found = {}
        for filename in os.listdir(settings.DATA_DIR):
            path = os.path.join(settings.DATA_DIR, filename)
            if os.path.isfile(path):
                size_mb = os.path.getsize(path) / (1024 * 1024)
                files_found[filename] = f"{size_mb:.2f} MB"
        self.status["files"] = files_found

    async def start_setup(self):
        if self.status["is_running"]:
            return
            
        self.status["is_running"] = True
        self.status["stage"] = "starting"
        self.status["progress"] = {}
        self.status["db_progress"] = {"current": 0, "total": 0, "pct": 0}
        
        logger.info("Starting setup process...")
        loop = asyncio.get_event_loop()
        
        try:
            os.makedirs(settings.DATA_DIR, exist_ok=True)
            
            # Download (Blocking I/O offload)
            self.status["stage"] = "downloading"
            await loop.run_in_executor(None, self._download_files_sync)
            
            # Unzip (Blocking I/O offload)
            self.status["stage"] = "unpacking"
            await loop.run_in_executor(None, self._unpack_files_sync)
            
            # Merge (Blocking I/O offload)
            self.status["stage"] = "merging"
            await loop.run_in_executor(None, self._merge_csvs_sync)
            
            self.status["stage"] = "completed"
            self.status["message"] = "Setup files ready."
            logger.info("Setup files ready.")
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            self.status["stage"] = "error"
            self.status["message"] = str(e)
        finally:
            self.status["is_running"] = False

    def _download_files_sync(self):
        """Synchronous implementation to be run in executor"""
        for key, url in SEARCH_URLS.items():
            zip_path = os.path.join(settings.DATA_DIR, f"{key}.zip")
            if os.path.exists(zip_path):
                logger.info(f"Skipping download for {key}, file exists.")
                continue
                
            logger.info(f"Downloading {key} from {url}...")
            self.status["message"] = f"Downloading {key}..."
            
            try:
                with requests.get(url, stream=True) as response:
                    response.raise_for_status()
                    total_length = response.headers.get('content-length')
                    
                    if total_length is None:
                        with open(zip_path, 'wb') as f:
                            f.write(response.content)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        self.status["progress"][key] = {"current": 0, "total": total_length}
                        
                        with open(zip_path, 'wb') as f:
                            for data in response.iter_content(chunk_size=8192):
                                dl += len(data)
                                f.write(data)
                                self.status["progress"][key]["current"] = dl
                            
                logger.info(f"Finished downloading {key}")
            except Exception as e:
                raise Exception(f"Failed to download {url}: {e}")

    def _unpack_files_sync(self):
        import zipfile
        for key in SEARCH_URLS.keys():
            zip_path = os.path.join(settings.DATA_DIR, f"{key}.zip")
            logger.info(f"Unzipping {zip_path}...")
            self.status["message"] = f"Unzipping {key}..."
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(settings.DATA_DIR)
            except Exception as e:
                 logger.warning(f"Failed to unzip {zip_path}: {e}")

    def _merge_csvs_sync(self):
        logger.info("Merging CSV files...")
        self.status["message"] = "Merging CSVs..."
        output_path = settings.CSV_FILE
        
        part_files = [f for f in os.listdir(settings.DATA_DIR) if f.endswith('.csv') and 'school_data' not in f]
        part_files.sort()
        
        if not part_files:
            raise Exception("No CSV parts found to merge.")
            
        with open(output_path, 'w', encoding='latin-1') as outfile:
            for i, fname in enumerate(part_files):
                fpath = os.path.join(settings.DATA_DIR, fname)
                logger.info(f"Merging part: {fname}")
                
                with open(fpath, 'r', encoding='latin-1') as infile:
                    header = infile.readline()
                    if i == 0:
                        outfile.write(header)
                    
                    for line in infile:
                        outfile.write(line)
        
        logger.info("Merge finished.")

setup_service = SetupService()
