"""Uygulama ayarları.

Tüm yapılandırma tek yerde toplanır. Ses analizi eşikleri de burada tutulur —
sihirli sayılar kodun içine dağılmaz (bkz. CLAUDE.md kalite kuralları).

Değerler ortam değişkenlerinden veya backend/.env dosyasından okunur.
Gizli bilgi kaynak koda yazılmaz.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

API_V1_PREFIX = "/api/v1"

# Yüklenen her ses dosyası için varsayılan üst sınır: 10 MB.
# 20 saniyelik sıkıştırılmış tarayıcı kaydı için fazlasıyla yeterli,
# kötü niyetli büyük yüklemeleri de engeller.
DEFAULT_MAX_UPLOAD_BYTES = 10 * 1024 * 1024

TestId = Literal["speech", "sustained_vowel", "glide"]

# Tüm analiz sesi bu örnekleme oranına indirgenir (Karar K-008). İnsan sesi temel
# frekansı için fazlasıyla yeterli, pyin/pitch analizini de hızlandırır.
TARGET_SAMPLE_RATE = 22050

# Her testin minimum kabul edilebilir süresi (saniye). Frontend'deki
# features/voice-tests/testConfig.ts ile aynı değerlerdir — istemci zaten bunu
# uyguluyor, backend aynı kontrolü kendi tarafında tekrarlar (istemciye güvenilmez).
MIN_TEST_DURATION_SECONDS: dict[TestId, float] = {
    "speech": 3.0,
    "sustained_vowel": 2.0,
    "glide": 3.0,
}

# ---------- Kayıt kalitesi eşikleri ----------
# Bu değerler bilimsel veya klinik bir standarda dayanmaz; kötü kayıtları makul
# şekilde ayıklamak için seçilmiş başlangıç değerleridir (CLAUDE.md madde 13'teki
# stabilite skoru için geçerli olan aynı uyarı burada da geçerlidir).

# PyAV çıktısı -1.0..1.0 aralığında float'tır; bu genlik üstü bir örnek "clip olmuş" sayılır.
CLIPPING_SAMPLE_THRESHOLD = 0.99
# Örneklerin bu oranından fazlası clip ise kayıt reddedilir.
CLIPPING_REJECT_RATIO = 0.05
# Bu oranın üstü clip varsa kullanıcı uyarılır ama kayıt yine de kabul edilebilir.
CLIPPING_WARN_RATIO = 0.01

# Sessizlik, bu uzunluktaki pencerelerin RMS'ine bakılarak hesaplanır.
SILENCE_FRAME_MS = 20
# Bu RMS altındaki bir pencere "sessiz" sayılır.
SILENCE_RMS_THRESHOLD = 0.01
# Kaydın bu orandan fazlası sessizse reddedilir (konuşma/ses neredeyse hiç yok).
SILENCE_REJECT_RATIO = 0.95
# Bu oranın üstü sessizlik varsa kullanıcı uyarılır.
SILENCE_WARN_RATIO = 0.85

# Tüm kayıt genelinde RMS bu değerin altındaysa "ses seviyesi düşük" uyarısı verilir.
MIN_RMS_WARN = 0.02

# Her tespit edilen uyarı 100 üzerinden bu kadar puan kırar; skor bu eşiğin
# altına düşerse (veya sert bir ret koşulu tetiklenirse) kayıt reddedilir.
QUALITY_SCORE_WARNING_PENALTY = 20
QUALITY_ACCEPT_SCORE_THRESHOLD = 50


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
