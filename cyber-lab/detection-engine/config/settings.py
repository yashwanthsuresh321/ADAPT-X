import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('detection-engine')

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "adaptx_lab")
DB_USER = os.getenv("POSTGRES_USER", "adaptx_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "adaptx_secret")

DETECTION_INTERVAL = int(os.getenv("DETECTION_INTERVAL_SECONDS", "10"))

SSH_BRUTE_FORCE_MIN_ATTEMPTS = int(os.getenv("SSH_BRUTE_FORCE_MIN_ATTEMPTS", "5"))
SSH_BRUTE_FORCE_FAILURE_RATE = float(os.getenv("SSH_BRUTE_FORCE_FAILURE_RATE", "0.8"))

ML_SUSPICIOUS_THRESHOLD = float(os.getenv("ML_SUSPICIOUS_THRESHOLD", "0.8"))
COMMAND_ACTIVITY_THRESHOLD = int(os.getenv("COMMAND_ACTIVITY_THRESHOLD", "10"))
