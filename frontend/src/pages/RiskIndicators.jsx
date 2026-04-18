import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { getApiErrorMessage } from "../services/api.js";
import { formatDateTime, formatNumber } from "../services/formatters.js";
import {
  computeRiskForAllActive,
  computeRiskForSymbol,
  getRiskIndicatorBySymbol,
  listRiskIndicators,
} from "../services/riskService.js";


export default function RiskIndicators() {
  const { isAuthenticated } = useAuth();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [searchSymbol, setSearchSymbol] = useState("");
  const [lookupRow, setLookupRow] = useState(null);
  const [computeSymbol, setComputeSymbol] = useState("AAPL");

  async function loadRows() {
    setLoading(true);
    try {
      const data = await listRiskIndicators({ activeOnly: true, limit: 100 });
      setRows(data);
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRows();
  }, []);

  async function handleLookup(event) {
    event.preventDefault();
    if (!searchSymbol) {
      return;
    }

    setError("");
    try {
      const row = await getRiskIndicatorBySymbol(searchSymbol);
      setLookupRow(row);
    } catch (lookupError) {
      setError(getApiErrorMessage(lookupError));
    }
  }

  async function handleComputeOne() {
    setSubmitting(true);
    setError("");
    setMessage("");
    try {
      await computeRiskForSymbol(computeSymbol);
      setMessage(`Computed risk indicators for ${computeSymbol}.`);
      await loadRows();
    } catch (computeError) {
      setError(getApiErrorMessage(computeError));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleComputeAll() {
    setSubmitting(true);
    setError("");
    setMessage("");
    try {
      await computeRiskForAllActive();
      setMessage("Computed risk indicators for all active assets.");
      await loadRows();
    } catch (computeError) {
      setError(getApiErrorMessage(computeError));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <LoadingSpinner label="Loading risk indicators..." />;
  }

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>Risk Indicators</h1>
          <p>Latest deterministic and Bayesian-style risk outputs from the backend.</p>
        </div>
      </div>

      <ErrorBanner message={error || message} onDismiss={() => { setError(""); setMessage(""); }} />

      <div className="content-grid two-column">
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Lookup By Symbol</h2>
              <p>Fetch the latest row for one asset.</p>
            </div>
          </div>
          <form className="form-grid compact-form" onSubmit={handleLookup}>
            <label className="form-field">
              <span>Symbol</span>
              <input
                type="text"
                value={searchSymbol}
                onChange={(event) => setSearchSymbol(event.target.value.toUpperCase())}
                placeholder="AAPL"
              />
            </label>
            <button type="submit" className="secondary-button">Lookup</button>
          </form>

          {lookupRow ? (
            <div className="detail-list">
              <div><strong>{lookupRow.symbol}</strong> | Risk label: {lookupRow.risk_label || "-"}</div>
              <div>Volatility: {formatNumber(lookupRow.volatility_30d)}</div>
              <div>RSI 14: {formatNumber(lookupRow.rsi_14)}</div>
              <div>Computed: {formatDateTime(lookupRow.computed_at)}</div>
            </div>
          ) : null}
        </div>

        {isAuthenticated ? (
          <div className="card">
            <div className="section-header">
              <div>
                <h2>Compute</h2>
                <p>Trigger the protected risk compute endpoints.</p>
              </div>
            </div>
            <div className="form-grid compact-form">
              <label className="form-field">
                <span>Symbol</span>
                <input
                  type="text"
                  value={computeSymbol}
                  onChange={(event) => setComputeSymbol(event.target.value.toUpperCase())}
                />
              </label>
              <button type="button" className="primary-button" onClick={handleComputeOne} disabled={submitting}>
                Compute One
              </button>
              <button type="button" className="secondary-button" onClick={handleComputeAll} disabled={submitting}>
                Compute All Active
              </button>
            </div>
          </div>
        ) : null}
      </div>

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Latest Risk Rows</h2>
            <p>Public read view of the latest risk indicator per asset.</p>
          </div>
        </div>

        {rows.length === 0 ? (
          <EmptyState title="No risk indicators found" description="Run ETL and the risk pipeline first." />
        ) : (
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Volatility</th>
                  <th>RSI</th>
                  <th>Volume Ratio</th>
                  <th>52W High Gap</th>
                  <th>SMA50 Gap</th>
                  <th>Vol Label</th>
                  <th>Momentum</th>
                  <th>Volume</th>
                  <th>Risk Score</th>
                  <th>Risk Label</th>
                  <th>Computed</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.risk_id}>
                    <td>{row.symbol}</td>
                    <td>{formatNumber(row.volatility_30d)}</td>
                    <td>{formatNumber(row.rsi_14)}</td>
                    <td>{formatNumber(row.volume_ratio)}</td>
                    <td>{formatNumber(row.price_vs_52w_high)}</td>
                    <td>{formatNumber(row.price_vs_sma50)}</td>
                    <td>{row.volatility_label}</td>
                    <td>{row.momentum_label}</td>
                    <td>{row.volume_label}</td>
                    <td>{formatNumber(row.risk_score)}</td>
                    <td>{row.risk_label || "-"}</td>
                    <td>{formatDateTime(row.computed_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
