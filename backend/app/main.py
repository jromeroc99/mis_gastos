from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mis Gastos API",
    version="1.0.0",
    description="API para control de gastos personales"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mis Gastos API v1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
