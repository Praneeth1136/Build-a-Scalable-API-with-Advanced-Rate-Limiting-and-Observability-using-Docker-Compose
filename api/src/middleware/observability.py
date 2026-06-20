import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram
from pythonjsonlogger import jsonlogger

# Set up JSON logger
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.handlers = [handler]

# Prometheus metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "api_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

RATE_LIMIT_HITS = Counter(
    "api_rate_limit_hits_total",
    "Total rate limit hits (429)",
    ["endpoint"]
)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        endpoint = request.url.path
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            process_time = time.time() - start_time
            
            # Record metrics
            REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=status_code).inc()
            REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(process_time)
            
            if status_code == 429:
                RATE_LIMIT_HITS.labels(endpoint=endpoint).inc()
            
            # Log structured JSON
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "status_code": status_code,
                "duration_ms": round(process_time * 1000, 2),
                "client_ip": request.client.host if request.client else "unknown"
            }
            if status_code >= 400:
                logger.error(f"HTTP request failed: {status_code}", extra=log_data)
            else:
                logger.info("HTTP request successful", extra=log_data)

        return response
