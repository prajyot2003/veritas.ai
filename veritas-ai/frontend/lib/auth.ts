import Cookies from "js-cookie";
import { authApi } from "./api";

const TOKEN_KEY = "veritas_token";
const USER_KEY = "veritas_user";

export async function login(email: string, password: string) {
  const data = await authApi.login(email, password);
  return data;
}

export function setAuthToken(token: string, user: any) {
  Cookies.set(TOKEN_KEY, token, { expires: 1 });
  Cookies.set(USER_KEY, JSON.stringify(user), { expires: 1 });
}

export function getAuthToken(): string | null {
  return Cookies.get(TOKEN_KEY) || null;
}

export function getUser(): any | null {
  const raw = Cookies.get(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return !!getAuthToken();
}

export function logout() {
  Cookies.remove(TOKEN_KEY);
  Cookies.remove(USER_KEY);
  window.location.href = "/login";
}

export function requireAuth() {
  if (typeof window !== "undefined" && !isAuthenticated()) {
    window.location.href = "/login";
  }
}
