import { useEffect, useState } from "react";

/** Analiz penceresi boyutu. Küçük tutmak tepki süresini hızlandırır; seviye göstergesi için yeterlidir. */
const ANALYSER_FFT_SIZE = 512;
/** Ham RMS değeri normal konuşma sesinde göz ile görülür olsun diye büyütülür. Bilimsel bir ölçüm değildir, yalnızca görsel geri bildirimdir. */
const LEVEL_VISUAL_GAIN = 4;

/**
 * Aktif mikrofon akışının ses seviyesini kabaca 0-1 arasında döndürür.
 * Yalnızca "mikrofon çalışıyor" görsel geri bildirimi içindir; kayıt veya analiz için kullanılmaz.
 * AudioContext desteklenmiyorsa veya kurulumu herhangi bir nedenle başarısız olursa
 * sessizce 0 döner — bu küçük görsel özellik asla tüm uygulamayı çökertmemeli.
 */
export function useMicrophoneLevel(stream: MediaStream | null): number {
  const [level, setLevel] = useState(0);

  useEffect(() => {
    if (!stream || typeof window.AudioContext === "undefined") {
      setLevel(0);
      return;
    }

    let audioContext: AudioContext | undefined;
    let source: MediaStreamAudioSourceNode;
    let analyser: AnalyserNode;
    try {
      audioContext = new AudioContext();
      source = audioContext.createMediaStreamSource(stream);
      analyser = audioContext.createAnalyser();
      analyser.fftSize = ANALYSER_FFT_SIZE;
      source.connect(analyser);
    } catch {
      void audioContext?.close();
      setLevel(0);
      return;
    }

    const buffer = new Uint8Array(analyser.frequencyBinCount);
    let frameId: number;

    const tick = () => {
      analyser.getByteTimeDomainData(buffer);
      let sumSquares = 0;
      for (let i = 0; i < buffer.length; i += 1) {
        const normalized = (buffer[i] - 128) / 128;
        sumSquares += normalized * normalized;
      }
      const rms = Math.sqrt(sumSquares / buffer.length);
      setLevel(Math.min(1, rms * LEVEL_VISUAL_GAIN));
      frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(frameId);
      source.disconnect();
      analyser.disconnect();
      void audioContext.close();
    };
  }, [stream]);

  return level;
}
