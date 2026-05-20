const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiClient<T>(path: string, init?: RequestInit & { token?: string | null }): Promise<T> {
  const headers = new Headers(init?.headers);
  const isFormData = typeof FormData !== "undefined" && init?.body instanceof FormData;
  if (!headers.has("Content-Type") && init?.body && !isFormData) {
    headers.set("Content-Type", "application/json");
  }
  if (init?.token) {
    headers.set("Authorization", `Bearer ${init.token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let message = `API request failed with status ${response.status}`;
    try {
      const errorBody = await response.json();
      message = errorBody?.message ?? message;
    } catch {
      // Keep default message when the backend returns an empty/non-JSON response.
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}
