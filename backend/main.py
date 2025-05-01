from fastapi import FastAPI
from incident_loader import load_incidents

app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/incidents")
def get_incidents():
    return load_incidents()
