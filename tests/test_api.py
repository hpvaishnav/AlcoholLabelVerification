import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_get_config(self):
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("app_name", data)
        self.assertIn("bom_summary", data)

    def test_get_sample_data(self):
        response = self.client.get("/api/sample-data")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("sample_cases", data)

    def test_record_override(self):
        payload = {
            "application_id": "COLA-TEST-001",
            "field_name": "Brand Name",
            "previous_status": "REJECT",
            "new_status": "PASS",
            "reason": "Verified brand trademark documentation on file."
        }
        response = self.client.post("/api/override", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("audit_record", data)

if __name__ == "__main__":
    unittest.main()
