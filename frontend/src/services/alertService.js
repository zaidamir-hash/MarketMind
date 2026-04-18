import api from "./api.js";


export async function createAlert(payload) {
  const response = await api.post("/alerts", payload);
  return response.data;
}

export async function listAlerts(activeOnly = false) {
  const response = await api.get("/alerts", { params: { active_only: activeOnly } });
  return response.data;
}

export async function deactivateAlert(alertId) {
  const response = await api.patch(`/alerts/${alertId}/deactivate`);
  return response.data;
}

export async function listAlertLogs(limit = 50) {
  const response = await api.get("/alerts/logs", { params: { limit } });
  return response.data;
}
