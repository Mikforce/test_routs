import unittest
from fastapi.testclient import TestClient
from main import app

class TestOptimalRoute(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_optimal_route_by_id(self):

        # Проверим успешный запрос к API
        response = self.client.get("/api/routes/4")
        self.assertEqual(response.status_code, 200)

        # Проверим содержимое ответа
        response_json = response.json()
        expected_result = {"id": 4, "points": [{"lat": -14.21984, "lng": -170.37005}]}
        self.assertEqual(response_json, expected_result)

if __name__ == '__main__':
    unittest.main()