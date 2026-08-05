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
    startButton: "Başla",
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

  microphone: {
    title: "Mikrofon kontrolü",
    intro: "Testlere başlamadan önce mikrofonuna erişime izin vermemiz gerekiyor.",
    environmentTip:
      "Sessiz bir ortamda ve mikrofona yaklaşık 15-20 santimetre mesafede olduğundan emin ol.",
    grantButton: "Mikrofona izin ver",
    requesting: "Mikrofon izni isteniyor…",
    retryButton: "Tekrar dene",
    continueButton: "Devam et",
    levelIdleHint: "Bir şeyler söyleyerek mikrofonu test edebilirsin.",
    levelActiveHint: "Mikrofon sesini algılıyor.",
    permissionDenied:
      "Mikrofon izni reddedildi. Tarayıcı ayarlarından mikrofon iznini kontrol edip tekrar dene.",
    noDevice: "Mikrofon bulunamadı. Cihazında çalışan bir mikrofon olduğundan emin ol.",
    deviceBusy: "Mikrofona erişilemedi. Başka bir uygulama mikrofonu kullanıyor olabilir.",
    genericError: "Mikrofona erişilemedi. Tarayıcı ayarlarından mikrofon iznini kontrol et.",
    unsupported:
      "Tarayıcın ses kaydını desteklemiyor. Güncel bir Chrome, Edge veya Safari sürümü kullanmayı dene.",
  },

  voiceTest: {
    progress: (current: number, total: number) => `Test ${current}/${total}`,
    recommendedDuration: (min: number, max: number) => `Önerilen süre: ${min}-${max} saniye`,
    minDurationHint: (seconds: number) => `Kayıt en az ${seconds} saniye olmalı. Daha uzun bir kayıt dene.`,
    startButton: "Kaydı başlat",
    stopButton: "Kaydı durdur",
    deleteButton: "Kaydı sil",
    reRecordButton: "Yeniden kaydet",
    recordingInProgress: "Kayıt yapılıyor",
    recordingSaved: "Kayıt tamamlandı. Dinleyip devam edebilirsin.",
    nextTest: "Sonraki test",
    goToReview: "İncelemeye geç",
    backToReview: "İncelemeye dön",
  },

  review: {
    title: "Kayıtlarını gözden geçir",
    intro: "Analize geçmeden önce üç kaydını da dinleyip kontrol edebilirsin.",
    statusDone: "Kaydedildi",
    statusMissing: "Henüz kaydedilmedi",
    reRecordButton: "Yeniden kaydet",
    analyzeButton: "Analiz et",
    analyzeDisabledHint: "Analiz edebilmek için önce üç testi de tamamlamalısın.",
    analyzeComingSoon: "Analiz özelliği bir sonraki geliştirme aşamasında eklenecek.",
  },
} as const;
