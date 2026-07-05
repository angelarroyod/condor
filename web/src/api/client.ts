import { API_URL } from "../config";

interface ApiErrorBody {
  error?: { message?: string };
}

/** Typed GET that surfaces the API's `{error:{message}}` schema as an Error. */
export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = (await res.json()) as ApiErrorBody;
      message = body.error?.message ?? message;
    } catch {
      // non-JSON error body — keep statusText
    }
    throw new Error(message);
  }
  return (await res.json()) as T;
}
