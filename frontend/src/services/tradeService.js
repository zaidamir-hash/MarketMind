import api from "./api.js";


export async function createTrade(payload) {
  const response = await api.post("/trades", payload);
  return response.data;
}

export async function getTrade(tradeId) {
  const response = await api.get(`/trades/${tradeId}`);
  return response.data;
}

export async function listTradesForPortfolio(portfolioId) {
  const response = await api.get(`/trades/portfolio/${portfolioId}`);
  return response.data;
}
