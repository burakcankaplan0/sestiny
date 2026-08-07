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
QUALITY_LABEL_GOOD_MIN = 80

# ---------- Pitch analizi (librosa.pyin) ----------
# Arama aralığı yaklaşık C2-C7: insan konuşma/şarkı sesi için yeterince geniş,
# anlamsız gürültüyü büyük ölçüde dışarıda bırakır (bkz. CLAUDE.md bölüm 11).
PYIN_FMIN_HZ = 65.4  # ~C2
PYIN_FMAX_HZ = 2093.0  # ~C7
PYIN_FRAME_LENGTH = 2048
PYIN_HOP_LENGTH = 512

# pyin'in ürettiği voiced_prob bu değerin altındaysa frame güvenilmez sayılır.
VOICED_PROB_THRESHOLD = 0.5

# Art arda gelen (zamanda birbirine yakın) güvenilir frame'ler arasında bu kadar
# yarı tondan büyük bir sıçrama, muhtemel bir oktav hatası veya izleme hatası
# sayılır ve elenir. Aralarında sessiz bir boşluk olan frame'ler karşılaştırılmaz
# (örn. konuşmadaki iki ayrı hece arası) — bu sadece gerçek süreklilik içindeki
# fiziksel olarak anlamsız sıçramaları hedefler.
MAX_SEMITONE_JUMP = 6.0

# ---------- Stabilite skoru (bilimsel/klinik standart değildir, bkz. CLAUDE.md bölüm 13) ----------
STABILITY_CENTS_DIVISOR = 4.0  # sapma arttıkça puan kırar: her ~4 cent ~1 puan
STABILITY_MAX_DEVIATION_PENALTY = 50.0
STABILITY_DROPOUT_WEIGHT = 40.0
STABILITY_MAX_DROPOUT_PENALTY = 30.0
STABILITY_JUMP_PENALTY = 3.0
STABILITY_MAX_JUMP_PENALTY = 20.0
STABILITY_LOW_VOICED_RATIO_THRESHOLD = 0.5
STABILITY_LOW_VOICED_PENALTY = 15.0

STABILITY_LABEL_STABLE_MIN = 80
STABILITY_LABEL_MODERATE_MIN = 55

# ---------- Tahmini rahat bölge (glide testi, bkz. CLAUDE.md bölüm 14) ----------
# Uç değerler doğrudan kullanılmaz; güvenilir F0 dağılımının bu yüzdelik
# dilimleri "gözlemlenen uç" kabul edilir, tahmini rahat bölge bundan daha dardır.
COMFORTABLE_RANGE_LOW_PERCENTILE = 5
COMFORTABLE_RANGE_HIGH_PERCENTILE = 95
# Bu güven/frame sayısının altında rahat bölge tahmini yapılmaz — "güvenilir
# şekilde belirlenemedi" durumuna düşülür.
GLIDE_COMFORTABLE_RANGE_MIN_CONFIDENCE = 0.4
GLIDE_COMFORTABLE_RANGE_MIN_FRAMES = 40

# ---------- Tahmini profil (bilimsel/klinik sınıflandırma değildir, bkz. CLAUDE.md bölüm 4) ----------
# Glide testinde gözlemlenen aralığın orta noktası (MIDI) bu sınırlara göre beş
# kaba "merkez bölge" kategorisinden birine yerleştirilir. Klasik ses türü
# sınıflandırması (bariton/tenor/...) DEĞİLDİR.
PROFILE_CENTER_LOW_MAX_MIDI = 43  # ~G2 altı → düşük merkezli
PROFILE_CENTER_LOW_MID_MAX_MIDI = 50  # ~D3 altı → orta-düşük merkezli
PROFILE_CENTER_MID_MAX_MIDI = 57  # ~A3 altı → orta merkezli
PROFILE_CENTER_MID_HIGH_MAX_MIDI = 64  # ~E4 altı → orta-yüksek merkezli; üstü → yüksek merkezli

PROFILE_RANGE_NARROW_MAX_SEMITONES = 12  # 1 oktavdan dar
PROFILE_RANGE_WIDE_MIN_SEMITONES = 19  # ~1.5 oktavdan geniş

# ---------- Şarkı önerileri (bkz. CLAUDE.md bölüm 5) ----------
# Bir şarkı kullanıcının aralığını en fazla bu kadar yarı ton aşıyorsa ton
# değiştirme (transpoze) önerisi denenir. Bunun üstü "çok büyük fark" sayılır.
TRANSPOSITION_MAX_SEMITONES = 3
# Ton değiştirmeyle de kapatılamayan her kalan taşma yarı tonu, 100 üzerinden
# eşleşme skorundan bu kadar puan kırar.
OVERSHOOT_PENALTY_PER_SEMITONE = 8
# Tessitura verisi olan şarkılarda, şarkının uç notalarının (full range)
# tessitura'nın ötesinde kullanıcı aralığını aşan kısmı yalnızca hafif bir ceza
# alır (bkz. K-064). Fikir: sesin çoğunlukla gezdiği bölge (tessitura) rahat
# oturuyorsa, birkaç ad-lib/tiz uç notasının biraz taşması şarkıyı elemez —
# sadece küçük bir dezavantaj. Birincil (tessitura) cezasından belirgin düşük.
FULL_RANGE_SECONDARY_PENALTY_PER_SEMITONE = 3
# İkincil ceza tavanı: çok geniş full range'li bir şarkı bile en fazla bu kadar
# puan kaybeder. Böylece full range asla tessitura sinyalini bastıramaz —
# tessitura'daki 2 yarı tonluk sapma (16 puan) bile her türlü uç-nota
# taşmasından (en fazla bu tavan) daha ağır basar. "Tessitura'yı full range'den
# fazla önemse" isteğinin sayısal garantisi budur.
FULL_RANGE_SECONDARY_MAX_PENALTY = 15
# Aynı aralık uyumunda daha zor bir şarkı hafifçe geride kalır (CLAUDE.md madde 5,
# adım 6: "Zorluk seviyesini eşleşme skoruna dahil et").
DIFFICULTY_SCORE_PENALTY: dict[str, int] = {"kolay": 0, "orta": 5, "zor": 10}
# CLAUDE.md: "En uygun 5-10 sonucu sırala."
MAX_RECOMMENDATIONS = 10

# ---------- Şarkı verisi kaynak katmanları (bkz. K-059) ----------
# Her şarkının nota aralığı farklı güvenilirlikte kaynaklardan geliyor. Katman,
# verinin nereden geldiğini; confidence ise buna karşılık gelen güveni belirtir.
# Skor bu güvenle ağırlıklandırılır — düşük güvenli veri havuza girebilir ama
# üst sıraları işgal edemez.
SOURCE_TIER_PUBLISHED_RANGE = 1  # yayınlanmış vokal aralığı veritabanı (singingcarrots)
SOURCE_TIER_MACHINE_READABLE_SCORE = 2  # makine okunur nota verisi (SymbTr MIDI)
SOURCE_TIER_MEASURED = 3  # izole vokalden ölçüm
SOURCE_TIER_REPORTED_BY_EAR = 4  # kulakla bildirim
# Demo veri kurgudur (bkz. K-042); havuzda gerçek şarkı varken kullanıcıya
# gösterilmesinin bir değeri yok. En düşük güvenle son çare olarak kalır —
# algoritmanın veri yokken de çalıştığını gösterdiği için silinmiyor (K-049).
SOURCE_TIER_DEMO = 5

SOURCE_TIER_CONFIDENCE: dict[int, float] = {
    SOURCE_TIER_PUBLISHED_RANGE: 1.0,
    SOURCE_TIER_MACHINE_READABLE_SCORE: 0.9,
    SOURCE_TIER_MEASURED: 0.7,
    SOURCE_TIER_REPORTED_BY_EAR: 0.4,
    SOURCE_TIER_DEMO: 0.2,
}

# Serbest transpoze edilebilen eserler (Türk makam müziği) için kaydırma sınırı.
# Makam müziğinde eserin sabit bir mutlak aralığı yoktur; icracı kendi sesine
# uygun "ahenk"i (perde seviyesini) seçer. Bu yüzden notasyondaki mutlak yerleşim
# değil, yalnızca aralık genişliği anlamlıdır (bkz. K-060).
# Sınır 3 oktav: SymbTr notasyonu teorik bir referans perdeden yazıldığı için
# (medyan merkez ~D5) pes bir ses için gereken kaydırma 24 yarı tonu aşabiliyor;
# bir oktav yetersiz kalıyordu. 36, her insan sesini kapsamaya fazlasıyla yeter.
FREE_TRANSPOSITION_MAX_SEMITONES = 36

# ---------- Öneri çeşitliliği (bkz. K-061) ----------
# Havuzda bir dilin/kaynağın eser sayısı diğerlerini çok aşabiliyor (ör. 1587
# makam eseri, 56 yabancı şarkı). Kota olmadan kalabalık grup tüm listeyi
# süpürür ve kullanıcı tek tip öneri görür.
MAX_RECOMMENDATIONS_PER_LANGUAGE = 6
MAX_RECOMMENDATIONS_PER_ARTIST = 2

# ---------- Hız sınırlama (Aşama 8: yayına hazırlık, bkz. K-053) ----------
# CPU-yoğun analiz uç noktası (librosa pitch analizi) herkese açık internete
# çıktığında IP başına bu sıklıkla sınırlanır. Format, slowapi/limits
# kütüphanesinin beklediği "<sayı>/<birim>" string'idir.
ANALYZE_SESSION_RATE_LIMIT = "5/minute"


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
    # Varsayılan olarak kapalı (K-052): ayarlanmamış bir ortamda (ör. bir PaaS'a
    # SESTINY_DEBUG env var'ı unutularak deploy edilirse) güvenli tarafta kalınır.
    # Bu, FastAPI'nin traceback sızdıran debug modunu ETKİLEMEZ (main.py'de zaten
    # hiç kullanılmıyor, o her zaman kapalı) — yalnızca log seviyesini belirler
    # (bkz. app/core/logging.py: configure_logging).
    debug: bool = False

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
