import api from "./api.js";


export async function listRiskIndicators({ activeOnly = true, limit = 100 } = {}) {
  const response = await api.get("/risk-indicators", {
    params: {
      active_only: activeOnly,
      limit,
    },
  });
  return response.data;
}

export async function getRiskIndicatorBySymbol(symbol) {
  const response = await api.get(`/risk-indicators/symbol/${encodeURIComponent(symbol)}`);
  return response.data;
}

export async function computeRiskForSymbol(symbol) {
  const response = await api.post("/risk-indicators/compute", { symbol });
  return response.data;
}

export async function computeRiskForAllActive() {
  const response = await api.post("/risk-indicators/compute/all-active");
  return response.data;
}
