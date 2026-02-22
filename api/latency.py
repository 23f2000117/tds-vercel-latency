from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

# Load telemetry safely (important for Vercel path)
file_path = os.path.join(os.path.dirname(__file__), "..", "telemetry.json")

with open(file_path) as f:
    data = json.load(f)

@app.post("/")
def compute_metrics(body: RequestBody):
    result = {}

    for region in body.regions:
        region_data = [r for r in data if r["region"] == region]

        if not region_data:
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(l > body.threshold_ms for l in latencies)
        }

    return result