from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/v1/simulate")
def simulate_endpoint(data: dict):
    return {"projected_emissions": 300.0, "reduction": 200.0}

client = TestClient(app)

def test_simulate_api_endpoint():
    response = client.post("/v1/simulate", json={"scenario": {"type": "switch_diet", "new_diet": "vegan"}})
    assert response.status_code == 200
    assert response.json() == {"projected_emissions": 300.0, "reduction": 200.0}
