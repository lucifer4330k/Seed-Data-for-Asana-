import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DB_PATH = os.path.join(BASE_DIR, "output", "asana_simulation.sqlite")

# Simulation Settings
NUM_USERS = int(os.getenv("NUM_USERS", 5000)) # Scale up to 5000
START_DATE_OFFSET_DAYS = 365 * 2 # Increase history to 2 years for user joining

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Probability Distributions
ARCHIVED_PROJECT_RATE = 0.15
UNASSIGNED_TASK_RATE = 0.15
