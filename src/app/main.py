from fastapi import FastAPI

app = FastAPI(title="AltFlex API")

@app.get("/")
async def root():
    return {"message": "Welcome to AltFlex API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
