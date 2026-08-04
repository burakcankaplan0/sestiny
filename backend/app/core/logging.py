"""Log yapılandırması.

Gizlilik kuralı: ses dosyası içeriği, ham binary veri veya kullanıcı sesinden
türetilmiş kimliklendirici bilgi hiçbir log seviyesinde yazılmaz. Bu modül yalnızca
biçimlendirme ve seviye ayarını yapar.
"""

import logging

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configure_logging(debug: bool) -> None:
    """Kök logger'ı yapılandırır. debug=True ise DEBUG, değilse INFO seviyesi."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format=LOG_FORMAT,
        force=True,  # Uvicorn'un kendi basicConfig çağrısının üzerine yazabilmek için
    )


def get_logger(name: str) -> logging.Logger:
    """Modüle özel logger döndürür."""
    return logging.getLogger(name)
