import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from "react";
import { createElement } from "react";
import api from "../api/client";

export interface UserInfo {
  id: string;
  email: string;
  nome: string;
  role: "admin" | "manager" | "consulta";
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserInfo | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => !!localStorage.getItem("token")
  );
  const [user, setUser] = useState<UserInfo | null>(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  const fetchMe = useCallback(async () => {
    try {
      const resp = await api.get("/auth/me");
      const u = resp.data as UserInfo;
      setUser(u);
      localStorage.setItem("user", JSON.stringify(u));
    } catch {
      // Token invalid
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setIsAuthenticated(false);
      setUser(null);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchMe();
    }
  }, [isAuthenticated, user, fetchMe]);

  const login = useCallback(async (email: string, password: string) => {
    const resp = await api.post("/auth/login", { email, password });
    localStorage.setItem("token", resp.data.access_token);
    setIsAuthenticated(true);
    // Fetch user info
    const meResp = await api.get("/auth/me");
    const u = meResp.data as UserInfo;
    setUser(u);
    localStorage.setItem("user", JSON.stringify(u));
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
    setUser(null);
  }, []);

  return createElement(
    AuthContext.Provider,
    { value: { isAuthenticated, user, login, logout } },
    children
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
