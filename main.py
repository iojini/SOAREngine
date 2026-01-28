from fastapi import FastAPI

app = FastAPI(
    title="SOAREngine",
    description="Security Orchestration, Automation & Response Platform",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "SOAREngine"}