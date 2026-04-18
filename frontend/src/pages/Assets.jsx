import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import {
  createAsset,
  deactivateAsset,
  getAssetBySymbol,
  listAssets,
  updateAsset,
} from "../services/assetsService.js";
import { getApiErrorMessage } from "../services/api.js";
import { formatDateTime } from "../services/formatters.js";


const defaultAssetForm = {
  symbol: "",
  name: "",
  asset_type: "STOCK",
  exchange: "",
  currency: "USD",
  is_active: true,
};


export default function Assets() {
  const { isAuthenticated } = useAuth();
  const [assets, setAssets] = useState([]);
  const [activeOnly, setActiveOnly] = useState(false);
  const [lookupSymbol, setLookupSymbol] = useState("");
  const [lookupResult, setLookupResult] = useState(null);
  const [assetForm, setAssetForm] = useState(defaultAssetForm);
  const [editForm, setEditForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadAssetsView() {
    setLoading(true);
    try {
      const data = await listAssets(activeOnly);
      setAssets(data);
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAssetsView();
  }, [activeOnly]);

  async function handleLookup(event) {
    event.preventDefault();
    if (!lookupSymbol) {
      return;
    }

    setError("");
    setLookupResult(null);
    try {
      const result = await getAssetBySymbol(lookupSymbol);
      setLookupResult(result);
    } catch (lookupError) {
      setError(getApiErrorMessage(lookupError));
    }
  }

  async function handleCreate(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      await createAsset(assetForm);
      setMessage(`Created asset ${assetForm.symbol}.`);
      setAssetForm(defaultAssetForm);
      await loadAssetsView();
    } catch (createError) {
      setError(getApiErrorMessage(createError));
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdate(event) {
    event.preventDefault();
    if (!editForm) {
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");
    try {
      await updateAsset(editForm.asset_id, {
        name: editForm.name,
        asset_type: editForm.asset_type,
        exchange: editForm.exchange,
        currency: editForm.currency,
        is_active: editForm.is_active,
      });
      setMessage(`Updated asset ${editForm.symbol}.`);
      setEditForm(null);
      await loadAssetsView();
    } catch (updateError) {
      setError(getApiErrorMessage(updateError));
    } finally {
      setSaving(false);
    }
  }

  async function handleDeactivate(assetId) {
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const result = await deactivateAsset(assetId);
      setMessage(`Deactivated asset ${result.symbol}.`);
      await loadAssetsView();
    } catch (deactivateError) {
      setError(getApiErrorMessage(deactivateError));
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <LoadingSpinner label="Loading assets..." />;
  }

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>Assets</h1>
          <p>Browse current assets, look up symbols, and manage asset metadata when authenticated.</p>
        </div>
      </div>

      <ErrorBanner message={error || message} onDismiss={() => { setError(""); setMessage(""); }} />

      <div className="content-grid two-column">
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Browse Assets</h2>
              <p>Toggle active assets only or browse the full asset table.</p>
            </div>
          </div>
          <label className="inline-toggle">
            <input
              type="checkbox"
              checked={activeOnly}
              onChange={(event) => setActiveOnly(event.target.checked)}
            />
            <span>Show active assets only</span>
          </label>

          {assets.length === 0 ? (
            <EmptyState title="No assets found" description="Use the ETL tools or create an asset manually." />
          ) : (
            <div className="table-shell">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Exchange</th>
                    <th>Status</th>
                    <th>Added</th>
                    {isAuthenticated ? <th>Actions</th> : null}
                  </tr>
                </thead>
                <tbody>
                  {assets.map((asset) => (
                    <tr key={asset.asset_id}>
                      <td>{asset.symbol}</td>
                      <td>{asset.name}</td>
                      <td>{asset.asset_type}</td>
                      <td>{asset.exchange || "-"}</td>
                      <td>{asset.is_active ? "Active" : "Inactive"}</td>
                      <td>{formatDateTime(asset.added_at)}</td>
                      {isAuthenticated ? (
                        <td>
                          <div className="inline-actions">
                            <button
                              type="button"
                              className="link-button"
                              onClick={() => setEditForm(asset)}
                            >
                              Edit
                            </button>
                            <button
                              type="button"
                              className="link-button danger-text"
                              onClick={() => handleDeactivate(asset.asset_id)}
                            >
                              Deactivate
                            </button>
                          </div>
                        </td>
                      ) : null}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="stack-column">
          <div className="card">
            <div className="section-header">
              <div>
                <h2>Lookup by Symbol</h2>
                <p>Query a specific asset using the backend symbol lookup route.</p>
              </div>
            </div>
            <form className="form-grid compact-form" onSubmit={handleLookup}>
              <label className="form-field">
                <span>Symbol</span>
                <input
                  type="text"
                  value={lookupSymbol}
                  onChange={(event) => setLookupSymbol(event.target.value.toUpperCase())}
                  placeholder="AAPL"
                />
              </label>
              <button type="submit" className="secondary-button">Lookup</button>
            </form>

            {lookupResult ? (
              <div className="detail-list">
                <div><strong>{lookupResult.symbol}</strong> {lookupResult.name}</div>
                <div>Type: {lookupResult.asset_type}</div>
                <div>Currency: {lookupResult.currency}</div>
                <div>Exchange: {lookupResult.exchange || "-"}</div>
              </div>
            ) : null}
          </div>

          {isAuthenticated ? (
            <div className="card">
              <div className="section-header">
                <div>
                  <h2>Create Asset</h2>
                  <p>Manual asset creation for demo use when backend auth is available.</p>
                </div>
              </div>
              <form className="form-grid" onSubmit={handleCreate}>
                <label className="form-field">
                  <span>Symbol</span>
                  <input
                    type="text"
                    value={assetForm.symbol}
                    onChange={(event) => setAssetForm((current) => ({ ...current, symbol: event.target.value.toUpperCase() }))}
                    required
                  />
                </label>
                <label className="form-field">
                  <span>Name</span>
                  <input
                    type="text"
                    value={assetForm.name}
                    onChange={(event) => setAssetForm((current) => ({ ...current, name: event.target.value }))}
                    required
                  />
                </label>
                <label className="form-field">
                  <span>Asset Type</span>
                  <select
                    value={assetForm.asset_type}
                    onChange={(event) => setAssetForm((current) => ({ ...current, asset_type: event.target.value }))}
                  >
                    <option value="STOCK">STOCK</option>
                    <option value="CRYPTO">CRYPTO</option>
                  </select>
                </label>
                <label className="form-field">
                  <span>Exchange</span>
                  <input
                    type="text"
                    value={assetForm.exchange}
                    onChange={(event) => setAssetForm((current) => ({ ...current, exchange: event.target.value }))}
                  />
                </label>
                <button type="submit" className="primary-button" disabled={saving}>
                  {saving ? "Saving..." : "Create Asset"}
                </button>
              </form>
            </div>
          ) : null}

          {isAuthenticated && editForm ? (
            <div className="card">
              <div className="section-header">
                <div>
                  <h2>Edit Asset</h2>
                  <p>Update selected asset metadata.</p>
                </div>
              </div>
              <form className="form-grid" onSubmit={handleUpdate}>
                <label className="form-field">
                  <span>Symbol</span>
                  <input type="text" value={editForm.symbol} disabled />
                </label>
                <label className="form-field">
                  <span>Name</span>
                  <input
                    type="text"
                    value={editForm.name}
                    onChange={(event) => setEditForm((current) => ({ ...current, name: event.target.value }))}
                    required
                  />
                </label>
                <label className="form-field">
                  <span>Asset Type</span>
                  <select
                    value={editForm.asset_type}
                    onChange={(event) => setEditForm((current) => ({ ...current, asset_type: event.target.value }))}
                  >
                    <option value="STOCK">STOCK</option>
                    <option value="CRYPTO">CRYPTO</option>
                  </select>
                </label>
                <label className="form-field">
                  <span>Exchange</span>
                  <input
                    type="text"
                    value={editForm.exchange || ""}
                    onChange={(event) => setEditForm((current) => ({ ...current, exchange: event.target.value }))}
                  />
                </label>
                <div className="inline-actions">
                  <button type="submit" className="primary-button" disabled={saving}>
                    {saving ? "Updating..." : "Save Changes"}
                  </button>
                  <button type="button" className="ghost-button" onClick={() => setEditForm(null)}>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
