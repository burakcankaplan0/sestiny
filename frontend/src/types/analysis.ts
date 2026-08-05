/** Backend'in POST /api/v1/analyze-session cevabı. backend/app/schemas/analysis.py ile eşleşir. */

export interface QualitySummary {
  overall_score: number;
  label: "iyi" | "orta" | "yetersiz";
  warnings: string[];
}

export interface SpeechAnalysis {
  accepted: boolean;
  warnings: string[];
  duration_seconds: number;
  median_f0_hz: number | null;
  approximate_note: string | null;
  pitch_variability_semitones: number | null;
  voiced_ratio: number;
  confidence: number;
}

export interface SustainedVowelAnalysis {
  accepted: boolean;
  warnings: string[];
  duration_seconds: number;
  median_f0_hz: number | null;
  approximate_note: string | null;
  voiced_duration_seconds: number;
  pitch_deviation_cents: number | null;
  jump_count: number;
  dropout_ratio: number;
  stability_score: number;
  stability_label: string;
  confidence: number;
}

export interface GlideAnalysis {
  accepted: boolean;
  warnings: string[];
  duration_seconds: number;
  observed_low_note: string | null;
  observed_high_note: string | null;
  observed_low_midi: number | null;
  observed_high_midi: number | null;
  range_semitones: number | null;
  estimated_comfortable_low_note: string | null;
  estimated_comfortable_high_note: string | null;
  confidence: number;
}

export interface ProfileSummary {
  label: string;
  range_label: string;
  summary: string;
}

export interface SongRecommendation {
  id: string;
  title: string;
  artist: string;
  language: string;
  genre: string;
  difficulty: "kolay" | "orta" | "zor";
  min_note: string;
  max_note: string;
  match_score: number;
  /** Negatif: aşağıdan, pozitif: yukarıdan denemek daha rahat olabilir. null: gerek yok. */
  transposition_semitones: number | null;
  verified: boolean;
  source_note: string;
}

export interface AnalyzeSessionResponse {
  session_id: string;
  status: "accepted" | "rejected";
  quality: QualitySummary;
  speech: SpeechAnalysis;
  sustained_vowel: SustainedVowelAnalysis;
  glide: GlideAnalysis;
  profile: ProfileSummary | null;
  recommendations: SongRecommendation[];
}
