"""Sağlık kontrolü endpoint testleri."""

from fastapi.testclient import TestClient

from app.core.config import API_V1_PREFIX
from app.main import app

client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get(f"{API_V1_PREFIX}/health")
    assert response.status_code == 200


def test_health_response_shape() -> None:
    """Frontend'in beklediği alanlar cevapta bulunmalı."""
    payload = client.get(f"{API_V1_PREFIX}/health").json()
    assert payload == {"status": "ok", "message": "Backend bağlantısı başarılı"}


def test_unversioned_health_is_not_exposed() -> None:
    """API versiyonlu olmalı; /health doğrudan erişilebilir olmamalı."""
    assert client.get("/health").status_code == 404


def test_cors_allows_local_frontend() -> None:
    """Vite geliştirme sunucusundan gelen istek CORS'a takılmamalı."""
    origin = "http://localhost:5173"
    response = client.get(f"{API_V1_PREFIX}/health", headers={"Origin": origin})
    assert response.headers.get("access-control-allow-origin") == origin


def test_cors_blocks_unknown_origin() -> None:
    """Bilinmeyen bir origin için izin başlığı dönmemeli (wildcard yok)."""
    response = client.get(
        f"{API_V1_PREFIX}/health", headers={"Origin": "http://kotu-site.example"}
    )
    assert "access-control-allow-origin" not in response.headers
