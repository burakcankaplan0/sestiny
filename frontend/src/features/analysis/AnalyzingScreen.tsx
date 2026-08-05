import { useEffect, useState } from "react";

import { ScreenLayout } from "../../components/ScreenLayout";
import { texts } from "../../texts";
import "./AnalyzingScreen.css";

/** Sahte bir yüzde göstergesi yerine, gerçek işlem aşamalarına karşılık gelen
 * mesajlar sırayla gösterilir (bkz. CLAUDE.md bölüm 16). Backend isteği tek bir
 * atomik çağrı olduğundan bu mesajlar kesin bir sunucu ilerlemesini değil,
 * yaklaşık bir sırayı temsil eder — son mesajda kalıp isteği beklemeye devam eder. */
const STAGE_MESSAGES = [texts.analyzing.stage1, texts.analyzing.stage2, texts.analyzing.stage3];
const STAGE_INTERVAL_MS = 1800;

export function AnalyzingScreen() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setStageIndex((previous) => Math.min(previous + 1, STAGE_MESSAGES.length - 1));
    }, STAGE_INTERVAL_MS);
    return () => window.clearInterval(interval);
  }, []);

  return (
    <ScreenLayout title={texts.analyzing.title}>
      <div className="analyzing" role="status" aria-live="polite">
        <span className="analyzing__spinner" aria-hidden="true" />
        <p className="analyzing__message">{STAGE_MESSAGES[stageIndex]}</p>
      </div>
    </ScreenLayout>
  );
}
