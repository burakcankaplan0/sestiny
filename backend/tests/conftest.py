"""Paylaşılan pytest fixture'ları."""

import pytest

from app.core.rate_limit import limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    """Her testten önce hız sınırlayıcının bellek içi sayaçlarını sıfırlar.

    Aksi hâlde tüm test dosyaları aynı TestClient'ı (dolayısıyla aynı sahte
    IP'yi) paylaştığından, bir test dosyasındaki istekler bir sonrakinin
    limitini sessizce doldurup 429'a düşürebilir (bkz. K-053)."""
    limiter.reset()
