from fastapi.testclient import TestClient

from codehealthanalyzer.web.server import DashboardServer


def test_dashboard_metrics_endpoint_returns_expected_shape(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("x = 1\n", encoding="utf-8")
    app = DashboardServer(str(tmp_path)).app
    client = TestClient(app)

    response = client.get("/api/metrics")

    assert response.status_code == 200
    payload = response.json()
    assert "timestamp" in payload
    assert "quality_score" in payload
    assert "violations_by_type" in payload
