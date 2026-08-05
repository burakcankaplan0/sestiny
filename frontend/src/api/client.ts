/**
 * Backend istekleri için ince bir fetch sarmalayıcısı.
 *
 * Amaç: ham teknik hataların (traceback, HTTP kodu, dosya yolu) kullanıcı arayüzüne
 * sızmasını engellemek. Her hata, gösterilebilir Türkçe bir mesaja çevrilir.
 */

import { texts } from "../texts";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;

export const API_V1_URL = `${API_BASE_URL}/api/v1`;

/** Kullanıcıya gösterilebilir mesaj taşıyan hata tipi. */
export class ApiError extends Error {
  /** Geliştirme logları için ham detay; kullanıcıya gösterilmez. */
  readonly detail?: string;

  constructor(userMessage: string, detail?: string) {
    super(userMessage);
    this.name = "ApiError";
    this.detail = detail;
  }
}

async function handleJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new ApiError(texts.errors.server, `HTTP ${response.status}`);
  }

  try {
    return (await response.json()) as T;
  } catch (cause) {
    throw new ApiError(texts.errors.unexpected, String(cause));
  }
}

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_V1_URL}${path}`, { signal });
  } catch (cause) {
    // fetch yalnızca ağ seviyesinde başarısız olursa throw eder (sunucu kapalı, DNS, CORS).
    throw new ApiError(texts.errors.network, String(cause));
  }

  return handleJsonResponse<T>(response);
}

/** multipart/form-data POST isteği. Content-Type başlığı bilerek ayarlanmaz —
 * tarayıcı, FormData sınırını (boundary) kendisi doğru şekilde ekler. */
export async function apiPostForm<T>(path: string, form: FormData, signal?: AbortSignal): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_V1_URL}${path}`, { method: "POST", body: form, signal });
  } catch (cause) {
    throw new ApiError(texts.errors.network, String(cause));
  }

  return handleJsonResponse<T>(response);
}
