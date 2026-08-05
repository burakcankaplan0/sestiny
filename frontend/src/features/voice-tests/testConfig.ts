import type { TestId } from "../../types/recording";

export interface VoiceTestConfig {
  id: TestId;
  title: string;
  instruction: string;
  sentenceToRead?: string;
  minSeconds: number;
  recommendedMinSeconds: number;
  recommendedMaxSeconds: number;
  maxSeconds: number;
}

/**
 * Üç zorunlu ses testinin sabit tanımı: talimat metni ve süre sınırları CLAUDE.md'de
 * belirlenen değerlerdir, burada tek merkezde tutulur.
 */
export const VOICE_TESTS: VoiceTestConfig[] = [
  {
    id: "speech",
    title: "Konuşma testi",
    instruction:
      "Telefonunu veya bilgisayarını ağzından yaklaşık 20 santimetre uzakta tut. Cümleyi bağırmadan, fısıldamadan ve günlük konuşma tonunla oku.",
    sentenceToRead: "Merhaba, bugün sesimi analiz etmek için kısa bir kayıt yapıyorum.",
    minSeconds: 3,
    recommendedMinSeconds: 5,
    recommendedMaxSeconds: 10,
    maxSeconds: 15,
  },
  {
    id: "sustained_vowel",
    title: 'Uzun "A" sesi',
    instruction:
      'Rahat bir nota seç. Derin bir nefes al ve sesini zorlamadan "Aaaa" sesini mümkün olduğunca sabit tut. En yüksek veya en düşük sesine çıkmaya çalışma.',
    minSeconds: 2,
    recommendedMinSeconds: 5,
    recommendedMaxSeconds: 12,
    maxSeconds: 20,
  },
  {
    id: "glide",
    title: "Kalından inceye kaydırma",
    instruction:
      'Rahatça çıkarabildiğin kalın bir sesten başla. "Aaaa" diyerek sesini yavaşça incelt. Bağırma, sesi sıkıştırma ve canını acıtan bir noktaya ulaşmaya çalışma.',
    minSeconds: 3,
    recommendedMinSeconds: 6,
    recommendedMaxSeconds: 12,
    maxSeconds: 20,
  },
];
