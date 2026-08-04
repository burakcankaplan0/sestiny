/** Backend API cevap tipleri. Backend'deki Pydantic şemalarıyla eşleşir. */

export interface HealthResponse {
  status: string;
  message: string;
}
