import logging
from fastapi import FastAPI, Request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("web-server")

app = FastAPI(title="ADAPT-X Web Server")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming Request: {request.method} {request.url} from {request.client.host}")
    response = await call_next(request)
    logger.info(f"Response Status: {response.status_code}")
    return response

@app.get("/")
def read_root():
    return {"message": "Welcome to the ADAPT-X Enterprise Portal"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
