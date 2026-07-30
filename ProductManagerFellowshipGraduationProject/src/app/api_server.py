from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.app.api.data_loader import DataLoader
from src.app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to pre-load data into memory on server startup."""
    print("FastAPI Server Startup: Initializing DataLoader cache...")
    DataLoader.get_instance().reload()
    yield
    print("FastAPI Server Shutdown: Cleaning up resources.")


app = FastAPI(
    title="Blinkit Discovery Engine API",
    description="AI-Powered Discovery Engine for Category Exploration & Customer Insights",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", include_in_schema=False)
def root():
    """Redirects root URL to Interactive OpenAPI documentation."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.api_server:app", host="0.0.0.0", port=8000, reload=True)
