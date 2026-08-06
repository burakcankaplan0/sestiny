"""Ayarların (Settings) güvenli varsayılanlarını doğrulayan testler."""

from app.core.config import Settings


def test_debug_field_defaults_to_false() -> None:
    """Alan tanımının kendisi test edilir (get_settings() DEĞİL) — aksi hâlde
    yerel bir backend/.env dosyası (SESTINY_DEBUG=true) test sonucunu
    yanıltıcı şekilde etkileyebilir. Bu, ayarlanmamış bir ortamın (ör. bir
    PaaS'a env var unutularak deploy edilmesi) güvenli tarafta kaldığını
    doğrular."""
    assert Settings.model_fields["debug"].default is False
