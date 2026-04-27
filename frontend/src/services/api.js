import axios from "axios";


export const TOKEN_STORAGE_KEY = "marketmind_access_token";
export const USER_STORAGE_KEY = "marketmind_user";
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const requestUrl = error.config?.url ?? "";
    const detail = error.response?.data?.detail;
    const isInactiveUser = status === 403 && detail === "Inactive user.";

    if (
      (status === 401 || isInactiveUser)
      && !requestUrl.includes("/auth/login")
      && !requestUrl.includes("/auth/token")
      && !requestUrl.includes("/auth/register")
    ) {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
      window.localStorage.removeItem(USER_STORAGE_KEY);
      window.dispatchEvent(new Event("marketmind:unauthorized"));
    }

    return Promise.reject(error);
  },
);

export function getApiErrorMessage(error) {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail)) {
    const validationMessages = detail
      .map((item) => item?.msg)
      .filter(Boolean)
      .join(" ");
    if (validationMessages) {
      return validationMessages;
    }
  }

  if (typeof detail === "string" && detail.trim()) {
    if (status === 403 && detail === "Inactive user.") {
      return "Your account is inactive. Contact the project owner or register a different local user.";
    }

    return detail;
  }

  if (status === 401) {
    return "Authentication required. Please log in again.";
  }

  if (status === 403) {
    return "You do not have permission to perform that action.";
  }

  if (status === 404) {
    return "This screen requested a backend route that was not found.";
  }

  if (status && status >= 500) {
    return "The backend returned a server error. Check the FastAPI terminal logs for details.";
  }

  if (error?.request && !error?.response) {
    return `Unable to reach the backend at ${API_BASE_URL}. Make sure FastAPI is running and CORS allows the frontend origin.`;
  }

  if (error?.message) {
    return error.message;
  }

  return "Something went wrong while contacting the backend.";
}

export default api;
