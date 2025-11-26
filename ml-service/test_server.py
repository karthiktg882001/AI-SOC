#!/usr/bin/env python3
"""Simple test server to verify uvicorn works"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Test server is working", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("Starting test server on 0.0.0.0:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

