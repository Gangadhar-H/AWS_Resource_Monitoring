import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  timeout: 120000, // a scan can take a while on big accounts
});

const data = (r) => r.data;
const enc = encodeURIComponent;

export const runScan = () => api.post("/scan").then(data);
export const getSummary = () => api.get("/summary").then(data);
export const getResources = (params = {}) => api.get("/resources", { params }).then(data); // flagged only

// Inventory = every resource (flagged or healthy)
export const getInventory = (params = {}) => api.get("/inventory", { params }).then(data);
export const getResource = (type, id) => api.get(`/inventory/${enc(type)}/${enc(id)}`).then(data);
export const scanResource = (type, id) => api.post(`/inventory/${enc(type)}/${enc(id)}/scan`).then(data);

export function errorMessage(err) {
  if (err.response?.data?.detail) return err.response.data.detail;
  if (err.code === "ERR_NETWORK") return "Cannot reach the backend. Is it running on port 8000?";
  return err.message || "Something went wrong.";
}
