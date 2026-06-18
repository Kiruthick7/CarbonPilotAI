from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/v1/calculate")
def calculate_endpoint(data: dict):
    return {"total_emissions": 500.0, "status": "success"}

client = TestClient(app)

def test_calculate_api_endpoint():
    response = client.post("/v1/calculate", json={"distance": 1000})
    assert response.status_code == 200
    assert response.json() == {"total_emissions": 500.0, "status": "success"}
