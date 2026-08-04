"""Uygulama ayarları.

Tüm yapılandırma tek yerde toplanır. Ses analizi eşikleri de (Aşama 4'ten itibaren)
buraya eklenecek — sihirli sayılar kodun içine dağılmaz.

Değerler ortam değişkenlerinden veya backend/.env dosyasından okunur.
Gizli bilgi kaynak koda yazılmaz.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

API_V1_PREFIX = "/api/v1"

# Yüklenen her ses dosyası için varsayılan üst sınır: 10 MB.
# 20 saniyelik sıkıştırılmış tarayıcı kaydı için fazlasıyla yeterli,
# kötü niyetli büyük yüklemeleri de engeller.
DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class Settings(BaseSettings):
    """Ortam değişkenlerinden okunan uygulama ayarları."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SESTINY_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    # Virgülle ayrılmış liste olarak yazılır: "http://localhost:5173,http://127.0.0.1:5173"
    # Vite hem localhost hem 127.0.0.1 üzerinden açılabildiği için ikisi de varsayılan.
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    max_upload_bytes: int = DEFAULT_MAX_UPLOAD_BYTES

    @property
    def allowed_origins_list(self) -> list[str]:
        """CORS için izinli origin listesi. Boş girdiler ayıklanır."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Ayarları tek sefer okuyup önbelleğe alır."""
    return Settings()
