from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/health")
async def root():
    return {"ok":True}

@app.get("/api/albums")
async def root():
    return []