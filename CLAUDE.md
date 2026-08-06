# CLAUDE.md — Sestiny Proje Kuralları

Bu dosya, bu depoda çalışan her yapay zekâ asistanı için bağlayıcı kuralları içerir.

## Proje

**Sestiny**, kullanıcıdan üç kısa ses kaydı alarak **tahmini** bir ses profili çıkaran ve
bu profile uygun şarkılar önermeyi hedefleyen web tabanlı bir uygulamadır.

## Ürün sınırları (ihlal edilemez)

- Sestiny bir **sağlık uygulaması, tıbbi analiz aracı veya profesyonel vokal teşhis sistemi değildir**.
- Kesin ifade kullanılmaz: "Kesin baritonsun", "Ses tellerinde sorun var",
  "Sesin sağlıklı/sağlıksız", "Profesyonel şarkıcı olmaya uygunsun" gibi cümleler yasaktır.
- Bunun yerine: "Tahmini ses profilin", "Kaydında gözlemlenen ses aralığı",
  "Bu, kayıt kalitesine göre oluşturulmuş yaklaşık bir değerlendirmedir" dili kullanılır.
- Klasik ses türü sınıflandırması (bariton, tenor, alto, mezzo-soprano, soprano)
  ilk sürümde **kesin sonuç olarak gösterilmez**.
- Biyolojik cinsiyet ses kaydından tahmin edilmez.
- Her sonuç ekranında profesyonel teşhis olmadığı uyarısı bulunur.

## Teknik sınırlar (ilk sürüm)

- Frontend: React + TypeScript + Vite. Global state kütüphanesi (Redux/MobX) **yok**.
- Backend: Python 3.11+ + FastAPI + librosa/NumPy/SciPy/SoundFile.
- Kullanıcı hesabı **yok**, veritabanı **yok**, ödeme **yok**, harici AI API **yok**.
- Gerçek zamanlı pitch takibi **yok**. Docker **yok**. Supabase **yok**.
- Proje varsayılan olarak tamamen lokal geliştirilir. Yayına alma (deploy),
  yalnızca kullanıcının Aşama 8 için ayrıca ve açıkça verdiği onayla,
  ücretsiz katman PaaS üzerinde (bkz. K-051) yapılabilir — bu durumda bile
  yukarıdaki diğer kısıtlar (hesap yok, veritabanı yok, ödeme yok, harici AI
  API yok, Docker yok, Supabase yok) aynen geçerliliğini korur.
- Arayüz dili Türkçe.

## Gizlilik

- Ses kayıtları yalnızca analiz için işlenir, **kalıcı saklanmaz**.
- Analiz bitince geçici dosyalar silinir.
- Ses içeriği veya ham binary veri **loglanmaz**.
- Hata mesajlarında dosya yolu, traceback veya gizli bilgi gösterilmez.
- Gizli anahtar/şifre koda yazılmaz; `.env` Git'e eklenmez.

## Veri dürüstlüğü

- **Gerçek şarkıların nota aralıkları uydurulmaz.**
- Doğrulanmamış veri `verified: false` ile işaretlenir.
- Demo veriler açıkça kurgu isimlerle ("Demo Şarkı 1") oluşturulur, gerçek şarkı gibi sunulmaz.
- Analiz sırasında sabit/uydurma sonuç döndürülmez. Ses yetersizse nota uydurulmaz,
  "güvenilir şekilde belirlenemedi" denir.

## Çalışma şekli

- Proje **aşamalar** hâlinde geliştirilir (bkz. `docs/PROJECT_PLAN.md`).
- **Her ana aşama sonunda durulur ve kullanıcının "devam" onayı beklenir.**
- Mevcut aşamadaki hataları çözmek, test çalıştırmak ve aşamayı bitirmek için onay gerekmez.
- Proje klasörü dışındaki hiçbir dosyaya dokunulmaz.
- Dosya silme, klasör taşıma, `sudo`, Homebrew ile sistem geneline kurulum veya
  geri dönüşü zor işlemler **önce izin ister**.
- Proje içi dosya oluşturma/düzenleme ve proje bağımlılığı kurma serbesttir.
- Kullanıcı kodlama bilmiyor: teknik kararlar sade Türkçe açıklanır, hata gizlenmez.

## Kalite kuralları

- **Testler başarısızken aşama "tamamlandı" olarak raporlanmaz.**
- Uygulama çalıştırılmadan "çalışıyor" denmez.
- Yapılamayan veya doğrulanamayan şey açıkça belirtilir.
- TypeScript'te `any` kullanılmaz; Python fonksiyonlarında type hint kullanılır.
- Sihirli sayılar açıklamalı sabit olur; ses analizi eşikleri merkezi config'te tutulur.
- Hatalar sessizce yutulmaz. Kullanılmayan kod bırakılmaz.
- Yorumlar kodun **nedenini** anlatır.

## Belgeleme

- Her önemli teknik karar → `docs/DECISIONS.md`
- Her aşamada yapılanlar → `docs/PROGRESS.md`
