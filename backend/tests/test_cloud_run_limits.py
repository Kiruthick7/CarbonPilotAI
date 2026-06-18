from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_large_payload_rejection():
    """
    Test that uploading an excessively large file fails gracefully with a 413,
    protecting the Poppler OCR process from DoW (Denial of Wallet) and OOM crashes.
    """
    # Create a dummy payload larger than 5MB
    large_content = b"0" * (6 * 1024 * 1024)

    response = client.post(
        "/v1/ocr/upload",
        files={"files": ("large_dummy.pdf", large_content, "application/pdf")}
    )

    assert response.status_code == 413
    assert "File exceeds 5MB limit" in response.json()["detail"]
