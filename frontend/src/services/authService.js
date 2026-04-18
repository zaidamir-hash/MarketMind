import api, { TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from "./api.js";


export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function getStoredUser() {
  const raw = window.localStorage.getItem(USER_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function storeAuthPayload(payload) {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, payload.access_token);
  window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(payload.user));
}

export async function register(payload) {
  const response = await api.post("/auth/register", payload);
  return response.data;
}

export async function login(payload) {
  const response = await api.post("/auth/login", payload);
  storeAuthPayload(response.data);
  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get("/auth/me");
  window.localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(response.data));
  return response.data;
}

export function logout() {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  window.localStorage.removeItem(USER_STORAGE_KEY);
  window.dispatchEvent(new Event("marketmind:logout"));
}
