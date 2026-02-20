import csv
import os
import codecs
import logging
from typing import List
from models import School
from config import settings
from services.db_service import db_service
from services.setup_service import setup_service

logger = logging.getLogger(__name__)

class DataLoader:
    def load_data(self):
        csv_path = settings.CSV_FILE
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found at {csv_path}")
            return

        file_size = os.path.getsize(csv_path)
        logger.info(f"Starting data I/O from {csv_path} ({file_size / 1024 / 1024:.2f} MB)...")
        
        encodings = ['utf-8', 'latin-1', 'cp1252']
        schools_buffer = []
        bytes_read = 0
        
        for encoding in encodings:
            try:
                logger.info(f"Attempting to read CSV using encoding: {encoding}")
                
                with codecs.open(csv_path, 'r', encoding=encoding) as f:
                    # Sniff basic validation
                    reader = csv.DictReader(f)
                    if not self._validate_headers(reader.fieldnames):
                         logger.warning(f"Invalid headers with {encoding}, trying next...")
                         continue
                    
                    # Estimate position for progress using f.tell() roughly
                    # Note: f.tell() can be tricky with codecs, but useful for estimate
                    
                    for i, row in enumerate(reader):
                        # Update progress every 1000 rows
                        if i % 1000 == 0:
                             # Approximate progress based on text reading
                             # Since codecs buffers, tell() might be approximate
                             try:
                                 curr = f.tell()
                                 setup_service.update_db_progress(curr, file_size, rows_loaded=i)
                             except:
                                 pass # Ignore progress error
                                 
                        school = self._parse_row(row)
                        if school:
                            schools_buffer.append(school)
                        
                        if len(schools_buffer) >= 5000:
                            db_service.insert_schools(schools_buffer)
                            schools_buffer = [] 
                            
                    # Flush remaining
                    if schools_buffer:
                        db_service.insert_schools(schools_buffer)
                    
                    # Store total count
                    total_rows = i + 1
                
                # Final 100%
                setup_service.update_db_progress(file_size, file_size, rows_loaded=total_rows)
                logger.info(f"Successfully loaded data using {encoding}")
                break 
                
            except UnicodeDecodeError:
                logger.warning(f"Decoding failed for {encoding}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error during data load: {e}", exc_info=True)
                break

    def _validate_headers(self, headers: List[str]) -> bool:
        required = {'NCESSCH', 'SCHNAM05', 'LCITY05', 'LSTATE05'}
        if not headers:
            return False
        return required.issubset(set(headers))

    def _parse_row(self, row: dict) -> School:
        try:
            if not row.get('NCESSCH') or not row.get('SCHNAM05'):
                return None
            return School(
                NCESSCH=row['NCESSCH'],
                SCHNAM05=row['SCHNAM05'],
                LCITY05=row['LCITY05'],
                LSTATE05=row['LSTATE05']
            )
        except Exception:
            return None

data_loader = DataLoader()
