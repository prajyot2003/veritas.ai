import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

// Request interceptor: attach JWT
api.interceptors.request.use((config) => {
  const token = Cookies.get("veritas_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      Cookies.remove("veritas_token");
      Cookies.remove("veritas_user");
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

// ── API Methods ───────────────────────────────────────────────

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }).then((r) => r.data),
  me: () => api.get("/auth/me").then((r) => r.data),
};

// Documents
export const documentsApi = {
  upload: (files: File[]) => {
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    return api.post("/documents/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
  list: (status?: string) =>
    api.get("/documents/list", { params: { status_filter: status } }).then((r) => r.data),
  get: (id: string) => api.get(`/documents/${id}`).then((r) => r.data),
  delete: (id: string) => api.delete(`/documents/${id}`).then((r) => r.data),
};

// Anomaly
export const anomalyApi = {
  analyze: (docId: string) =>
    api.post(`/anomaly/analyze/${docId}`).then((r) => r.data),
  getResult: (docId: string) =>
    api.get(`/anomaly/results/${docId}`).then((r) => r.data),
  listResults: () =>
    api.get("/anomaly/results").then((r) => r.data),
};

// Compliance
export const complianceApi = {
  getMaps: (status?: string, priority?: string) =>
    api.get("/compliance/maps", { params: { status, priority } }).then((r) => r.data),
  getMap: (id: string) => api.get(`/compliance/maps/${id}`).then((r) => r.data),
  validate: (mapId: string, file?: File) => {
    const form = new FormData();
    if (file) form.append("proof_file", file);
    return api.post(`/compliance/validate/${mapId}`, form).then((r) => r.data);
  },
  getSummary: () => api.get("/compliance/summary").then((r) => r.data),
};

// Graph
export const graphApi = {
  getData: (entityType?: string) =>
    api.get("/graph/data", { params: { entity_type: entityType } }).then((r) => r.data),
  getAnalytics: () => api.get("/graph/analytics").then((r) => r.data),
};

// Risk
export const riskApi = {
  getDashboard: () => api.get("/risk/dashboard").then((r) => r.data),
  getUnderwriting: (docId: string) =>
    api.get(`/risk/underwriting/${docId}`).then((r) => r.data),
  getAlerts: () => api.get("/risk/alerts").then((r) => r.data),
};
