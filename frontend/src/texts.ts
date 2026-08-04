/**
 * Kullanıcıya gösterilen tüm Türkçe metinler burada toplanır.
 *
 * Tek yerde tutmanın nedeni: metinleri gözden geçirmek kolaylaşır ve
 * "kesin teşhis" iması taşıyan bir cümlenin araya kaçması zorlaşır.
 * Ürün dili kuralları için bkz. CLAUDE.md.
 */

export const texts = {
  app: {
    name: "Sestiny",
    tagline: "Sesine uygun şarkıları keşfet",
    intro:
      "Sestiny, üç kısa ses kaydından yaklaşık bir ses profili çıkarır ve bu profile uygun şarkılar önerir.",
  },

  disclaimer: {
    title: "Bilmen gerekenler",
    notDiagnosis:
      "Bu sonuçlar profesyonel bir vokal değerlendirme veya sağlık teşhisi değildir. Mikrofon kalitesi, ortam gürültüsü, kayıt tekniği ve o anki ses durumun sonucu etkileyebilir.",
    privacy:
      "Ses kayıtların yalnızca bu analiz için işlenir. İlk sürümde kayıtlar kalıcı olarak saklanmaz ve analiz tamamlandıktan sonra silinir.",
  },

  connection: {
    checking: "Backend bağlantısı kontrol ediliyor…",
    retry: "Tekrar dene",
    label: "Sunucu bağlantısı",
  },

  errors: {
    network:
      "Sunucuya ulaşılamadı. Backend'in çalıştığından ve bağlantından emin olup tekrar dene.",
    server: "Sunucu şu anda yanıt veremiyor. Biraz sonra tekrar dene.",
    unexpected: "Beklenmeyen bir sorun oluştu. Tekrar dene.",
  },
} as const;
