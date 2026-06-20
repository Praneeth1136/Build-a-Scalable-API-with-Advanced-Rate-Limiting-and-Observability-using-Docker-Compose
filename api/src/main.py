from fastapi import FastAPI
from prometheus_client import make_asgi_app

from .routes import status, products, protected
from .middleware.observability import ObservabilityMiddleware

app = FastAPI(title="Scalable API with Rate Limiting")

# Add Middlewares
app.add_middleware(ObservabilityMiddleware)

# Include Routers
app.include_router(status.router, prefix="/api", tags=["Status"])
app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(protected.router, prefix="/api", tags=["Protected"])

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/")
def root():
    return {"message": "Welcome to the Scalable API"}
