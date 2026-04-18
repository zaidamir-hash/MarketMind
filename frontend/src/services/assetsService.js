import api from "./api.js";


export async function listAssets(activeOnly = false) {
  const response = await api.get("/assets", { params: { active_only: activeOnly } });
  return response.data;
}

export async function listActiveAssets() {
  const response = await api.get("/assets/active");
  return response.data;
}

export async function getAssetCatalog() {
  const response = await api.get("/assets/catalog");
  return response.data;
}

export async function getAssetBySymbol(symbol) {
  const response = await api.get(`/assets/symbol/${encodeURIComponent(symbol)}`);
  return response.data;
}

export async function createAsset(payload) {
  const response = await api.post("/assets", payload);
  return response.data;
}

export async function updateAsset(assetId, payload) {
  const response = await api.patch(`/assets/${assetId}`, payload);
  return response.data;
}

export async function deactivateAsset(assetId) {
  const response = await api.delete(`/assets/${assetId}`);
  return response.data;
}
