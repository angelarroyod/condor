import { API_URL } from "../config";

interface ApiErrorBody {
  error?: { message?: string };
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const init: RequestInit = { method };
  if (body !== undefined) {
    init.headers = { "Content-Type": "application/json" };
    init.body = JSON.stringify(body);
  }
  const res = await fetch(`${API_URL}${path}`, init);
  if (!res.ok) {
    let message = res.statusText;
    try {
      const parsed = (await res.json()) as ApiErrorBody;
      message = parsed.error?.message ?? message;
    } catch {
      // non-JSON error body — keep statusText
    }
    throw new Error(message);
  }
  return (await res.json()) as T;
}

export const apiGet = <T>(path: string): Promise<T> => request<T>("GET", path);
export const apiPost = <T>(path: string, body: unknown): Promise<T> => request<T>("POST", path, body);
export const apiDelete = <T>(path: string): Promise<T> => request<T>("DELETE", path);
