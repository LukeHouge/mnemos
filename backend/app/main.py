from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mnemos API",
    description="Second Brain for Receipts / Manuals / PDFs",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Mnemos API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
