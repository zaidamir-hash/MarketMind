import api from "./api.js";


export async function runAiForSymbol(symbol) {
  const response = await api.post(`/ai/run/${encodeURIComponent(symbol)}`);
  return response.data;
}

export async function runAiForAll() {
  const response = await api.post("/ai/run-all");
  return response.data;
}

export async function listPredictions({ activeOnly = true, limit = 100 } = {}) {
  const response = await api.get("/ai/predictions", {
    params: {
      active_only: activeOnly,
      limit,
    },
  });
  return response.data;
}

export async function getPredictionsBySymbol(symbol) {
  const response = await api.get(`/ai/predictions/symbol/${encodeURIComponent(symbol)}`);
  return response.data;
}

export async function listSignals({ activeOnly = true, limit = 100 } = {}) {
  const response = await api.get("/ai/signals", {
    params: {
      active_only: activeOnly,
      limit,
    },
  });
  return response.data;
}

export async function getSignalsBySymbol(symbol) {
  const response = await api.get(`/ai/signals/symbol/${encodeURIComponent(symbol)}`);
  return response.data;
}

export async function listRegimes({ activeOnly = true, limit = 100 } = {}) {
  const response = await api.get("/ai/regimes", {
    params: {
      active_only: activeOnly,
      limit,
    },
  });
  return response.data;
}

export async function getRegimesBySymbol(symbol) {
  const response = await api.get(`/ai/regimes/symbol/${encodeURIComponent(symbol)}`);
  return response.data;
}
