import os

class Settings:
    PROJECT_NAME: str = "School Search API"
    VERSION: str = "1.0.0"
    
    # Data Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "seed")
    CSV_FILE = os.path.join(DATA_DIR, "school_data.csv")
    
    # Database
    DB_FILE = os.path.join(BASE_DIR, "schools.db") # Using file-based for persistence during dev, can switch to :memory:

settings = Settings()
