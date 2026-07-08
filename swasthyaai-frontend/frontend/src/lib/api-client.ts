import { config } from "@/config";
import { supabase } from "@/lib/supabase-client";
import type { ApiErrorBody } from "@/types/api";

/**
 * A normalized error type every caller (React Query hooks, forms) can rely
 * on, regardless of whether the failure came from the network, from
 * FastAPI's structured error envelope, or from something unexpected. This
 * is what makes a single <ErrorState/> component able to render any error
 * in the app sensibly.
 */
export class ApiError extends Error {
  code: string;
  status: number;
  details: unknown;

  constructor(message: string, code: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

async function getAuthHeader(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseErrorResponse(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as ApiErrorBody;
    if (body?.error) {
      return new ApiError(body.error.message, body.error.code, response.status, body.error.details);
    }
  } catch {
    // response body wasn't JSON — fall through to a generic error below
  }
  return new ApiError(
    response.status === 429
      ? "Too many requests — please wait a moment and try again."
      : "Something went wrong talking to the server.",
    response.status === 429 ? "RATE_LIMITED" : "UNKNOWN_ERROR",
    response.status
  );
}

interface RequestOptions {
  auth?: boolean;
  signal?: AbortSignal;
}

async function request<T>(method: string, path: string, body?: unknown, options: RequestOptions = {}): Promise<T> {
  const { auth = true, signal } = options;
  const headers: Record<string, string> = { "Content-Type": "application/json" };

  if (auth) {
    Object.assign(headers, await getAuthHeader());
  }

  const response = await fetch(`${config.apiBaseUrl}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (!response.ok) {
    throw await parseErrorResponse(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

/** For multipart/form-data uploads (voice recordings) — separate from
 * `request` because it must not set a JSON Content-Type header. */
async function requestForm<T>(path: string, formData: FormData, options: RequestOptions = {}): Promise<T> {
  const { auth = true, signal } = options;
  const headers: Record<string, string> = {};
  if (auth) {
    Object.assign(headers, await getAuthHeader());
  }

  const response = await fetch(`${config.apiBaseUrl}${path}`, {
    method: "POST",
    headers,
    body: formData,
    signal,
  });

  if (!response.ok) {
    throw await parseErrorResponse(response);
  }
  return (await response.json()) as T;
}

export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) => request<T>("GET", path, undefined, options),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) => request<T>("POST", path, body, options),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) => request<T>("PATCH", path, body, options),
  delete: <T>(path: string, options?: RequestOptions) => request<T>("DELETE", path, undefined, options),
  postForm: <T>(path: string, formData: FormData, options?: RequestOptions) => requestForm<T>(path, formData, options),
};
