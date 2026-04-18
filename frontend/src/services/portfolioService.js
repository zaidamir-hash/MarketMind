import api from "./api.js";


export async function createPortfolio(payload) {
  const response = await api.post("/portfolios", payload);
  return response.data;
}

export async function listPortfolios() {
  const response = await api.get("/portfolios");
  return response.data;
}

export async function getPortfolio(portfolioId) {
  const response = await api.get(`/portfolios/${portfolioId}`);
  return response.data;
}

export async function updatePortfolio(portfolioId, payload) {
  const response = await api.patch(`/portfolios/${portfolioId}`, payload);
  return response.data;
}

export async function getPortfolioHoldings(portfolioId) {
  const response = await api.get(`/portfolios/${portfolioId}/holdings`);
  return response.data;
}

export async function getPortfolioPerformance(portfolioId) {
  const response = await api.get(`/portfolios/${portfolioId}/performance`);
  return response.data;
}

export async function runOptimization(portfolioId, payload = { iterations: 250 }) {
  const response = await api.post(`/portfolios/${portfolioId}/optimize`, payload);
  return response.data;
}

export async function listOptimizations(portfolioId) {
  const response = await api.get(`/portfolios/${portfolioId}/optimisations`);
  return response.data;
}
