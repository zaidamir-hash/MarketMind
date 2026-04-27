import { createContext, useContext, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  getCurrentUser,
  getStoredToken,
  login as loginRequest,
  logout as logoutRequest,
  register as registerRequest,
} from "../services/authService.js";
import { getApiErrorMessage } from "../services/api.js";


const AuthContext = createContext(null);


export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [token, setToken] = useState(getStoredToken());
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getStoredToken()));

  useEffect(() => {
    async function bootstrap() {
      if (!getStoredToken()) {
        setLoading(false);
        return;
      }

      try {
        const user = await getCurrentUser();
        setCurrentUser(user);
        setToken(getStoredToken());
      } catch (error) {
        const status = error?.response?.status;
        if (status === 401 || status === 403) {
          logoutRequest();
        }
        setCurrentUser(null);
        setToken(status === 401 || status === 403 ? null : getStoredToken());
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, []);

  useEffect(() => {
    function handleUnauthorized() {
      setCurrentUser(null);
      setToken(null);
      if (!["/login", "/register"].includes(window.location.pathname)) {
        navigate("/login", {
          replace: true,
          state: {
            from: location.pathname,
            message: "Your session expired. Please log in again.",
          },
        });
      }
    }

    function handleLogout() {
      setCurrentUser(null);
      setToken(null);
    }

    window.addEventListener("marketmind:unauthorized", handleUnauthorized);
    window.addEventListener("marketmind:logout", handleLogout);

    return () => {
      window.removeEventListener("marketmind:unauthorized", handleUnauthorized);
      window.removeEventListener("marketmind:logout", handleLogout);
    };
  }, [location.pathname, navigate]);

  async function login(credentials) {
    const payload = await loginRequest(credentials);
    setToken(payload.access_token);
    setCurrentUser(payload.user);
    return payload;
  }

  async function register(data) {
    return registerRequest(data);
  }

  async function refreshUser() {
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
      return user;
    } catch (error) {
      throw new Error(getApiErrorMessage(error));
    }
  }

  function logout() {
    logoutRequest();
    setCurrentUser(null);
    setToken(null);
    navigate("/login", { replace: true });
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        currentUser,
        isAuthenticated: Boolean(token && currentUser),
        loading,
        login,
        register,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return context;
}
