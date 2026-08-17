import { API_PREFIX } from "../utils/constants";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export async function apiGet(path, timeoutMs = 8000) {
  return apiRequest(path, { method: "GET", timeoutMs });
}

export async function apiPost(path, body, timeoutMs = 20000) {
  return apiRequest(path, { method: "POST", body, timeoutMs });
}

export async function apiRequest(path, { method = "GET", body = null, timeoutMs = 8000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${BASE_URL}${API_PREFIX}${path}`, {
      method,
      headers: body instanceof FormData ? {} : { "Content-Type": "application/json" },
      body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const payload = await response.json();
        detail = payload.detail || payload.message || detail;
      } catch {
        /* keep default */
      }
      throw new Error(detail);
    }
    return await response.json();
  } finally {
    clearTimeout(timer);
  }
}

export function getApiBaseUrl() {
  return BASE_URL;
}

export function isDemoMode() {
  return import.meta.env.VITE_USE_DEMO === "true";
}
