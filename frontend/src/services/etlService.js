import api from "./api.js";


export async function onboardAsset(symbol) {
  const response = await api.post("/etl/onboard-asset", { symbol });
  return response.data;
}

export async function fetchPricesForSymbol(payload) {
  const response = await api.post("/etl/fetch-prices", payload);
  return response.data;
}

export async function fetchPricesForAllActive(payload = { period: "5d", interval: "5m" }) {
  const response = await api.post("/etl/fetch-prices/all-active", payload);
  return response.data;
}

export async function listEtlLogs(limit = 20) {
  const response = await api.get("/etl/logs", { params: { limit } });
  return response.data;
}
