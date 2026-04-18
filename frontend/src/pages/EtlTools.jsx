import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { fetchPricesForAllActive, fetchPricesForSymbol, listEtlLogs, onboardAsset } from "../services/etlService.js";
import { getApiErrorMessage } from "../services/api.js";
import { formatDateTime } from "../services/formatters.js";


export default function EtlTools() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [onboardSymbol, setOnboardSymbol] = useState("AAPL");
  const [priceForm, setPriceForm] = useState({
    symbol: "AAPL",
    period: "5d",
    interval: "5m",
  });
  const [batchForm, setBatchForm] = useState({
    period: "5d",
    interval: "5m",
  });

  async function loadLogs() {
    setLoading(true);
    try {
      const data = await listEtlLogs(20);
      setLogs(data);
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLogs();
  }, []);

  async function runAction(action, successMessage) {
    setSubmitting(true);
    setError("");
    setMessage("");
    try {
      await action();
      setMessage(successMessage);
      await loadLogs();
    } catch (actionError) {
      setError(getApiErrorMessage(actionError));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <LoadingSpinner label="Loading ETL tools..." />;
  }

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>ETL Tools</h1>
          <p>Manually run yfinance onboarding and price-fetch jobs through the protected backend routes.</p>
        </div>
      </div>

      <ErrorBanner message={error || message} onDismiss={() => { setError(""); setMessage(""); }} />

      <div className="content-grid three-column">
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Onboard Asset</h2>
              <p>Create or update an asset from yfinance metadata.</p>
            </div>
          </div>
          <form
            className="form-grid compact-form"
            onSubmit={(event) => {
              event.preventDefault();
              runAction(() => onboardAsset(onboardSymbol), `Onboarded ${onboardSymbol}.`);
            }}
          >
            <label className="form-field">
              <span>Symbol</span>
              <input
                type="text"
                value={onboardSymbol}
                onChange={(event) => setOnboardSymbol(event.target.value.toUpperCase())}
                required
              />
            </label>
            <button type="submit" className="primary-button" disabled={submitting}>
              {submitting ? "Running..." : "Onboard"}
            </button>
          </form>
        </div>

        <div className="card">
          <div className="section-header">
            <div>
              <h2>Fetch Prices</h2>
              <p>Pull one symbol's OHLCV rows into `price_history`.</p>
            </div>
          </div>
          <form
            className="form-grid compact-form"
            onSubmit={(event) => {
              event.preventDefault();
              runAction(
                () => fetchPricesForSymbol(priceForm),
                `Fetched prices for ${priceForm.symbol}.`,
              );
            }}
          >
            <label className="form-field">
              <span>Symbol</span>
              <input
                type="text"
                value={priceForm.symbol}
                onChange={(event) => setPriceForm((current) => ({ ...current, symbol: event.target.value.toUpperCase() }))}
                required
              />
            </label>
            <label className="form-field">
              <span>Period</span>
              <input
                type="text"
                value={priceForm.period}
                onChange={(event) => setPriceForm((current) => ({ ...current, period: event.target.value }))}
              />
            </label>
            <label className="form-field">
              <span>Interval</span>
              <input
                type="text"
                value={priceForm.interval}
                onChange={(event) => setPriceForm((current) => ({ ...current, interval: event.target.value }))}
              />
            </label>
            <button type="submit" className="secondary-button" disabled={submitting}>
              Fetch Symbol Prices
            </button>
          </form>
        </div>

        <div className="card">
          <div className="section-header">
            <div>
              <h2>Fetch All Active</h2>
              <p>Run the batch fetch for every active asset.</p>
            </div>
          </div>
          <form
            className="form-grid compact-form"
            onSubmit={(event) => {
              event.preventDefault();
              runAction(
                () => fetchPricesForAllActive(batchForm),
                "Fetched prices for all active assets.",
              );
            }}
          >
            <label className="form-field">
              <span>Period</span>
              <input
                type="text"
                value={batchForm.period}
                onChange={(event) => setBatchForm((current) => ({ ...current, period: event.target.value }))}
              />
            </label>
            <label className="form-field">
              <span>Interval</span>
              <input
                type="text"
                value={batchForm.interval}
                onChange={(event) => setBatchForm((current) => ({ ...current, interval: event.target.value }))}
              />
            </label>
            <button type="submit" className="secondary-button" disabled={submitting}>
              Fetch All Active
            </button>
          </form>
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Recent ETL Logs</h2>
            <p>Latest rows from `scraper_logs`.</p>
          </div>
        </div>

        {logs.length === 0 ? (
          <EmptyState title="No ETL logs yet" description="Run onboarding or price jobs to populate logs." />
        ) : (
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Job Name</th>
                  <th>Status</th>
                  <th>Rows Inserted</th>
                  <th>Started</th>
                  <th>Finished</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.log_id}>
                    <td>{log.job_name}</td>
                    <td>{log.status}</td>
                    <td>{log.rows_inserted ?? "-"}</td>
                    <td>{formatDateTime(log.started_at)}</td>
                    <td>{formatDateTime(log.finished_at)}</td>
                    <td>{log.error_message || "-"}</td>
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
