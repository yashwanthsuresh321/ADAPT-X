import logging
from fastapi import FastAPI, Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("internal-server")

app = FastAPI(title="ADAPT-X Internal API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Internal API Request: {request.method} {request.url} from {request.client.host}")
    response = await call_next(request)
    logger.info(f"Internal API Response Status: {response.status_code}")
    return response

@app.get("/")
def read_root():
    return {"message": "Internal Enterprise API v1.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
