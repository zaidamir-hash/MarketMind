import { useEffect, useState } from "react";
import { Database, RefreshCcw, Workflow } from "lucide-react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import SectionCard from "../components/SectionCard.jsx";
import StatCard from "../components/StatCard.jsx";
import { fetchPricesForAllActive, fetchPricesForSymbol, listEtlLogs, onboardAsset } from "../services/etlService.js";
import { getApiErrorMessage } from "../services/api.js";
import { formatDateTime } from "../services/formatters.js";

const periodOptions = ["1d", "5d", "1mo", "3mo", "6mo", "1y"];
const intervalOptions = ["5m", "15m", "30m", "1h", "1d"];


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

  const successCount = logs.filter((log) => log.status === "SUCCESS").length;
  const failureCount = logs.filter((log) => log.status === "FAIL").length;

  return (
    <section className="page-shell">
      <PageHeader
        eyebrow="Protected workspace"
        title="ETL Tools"
        description="Manually run yfinance onboarding and price-fetch jobs through the protected backend routes."
      />

      <ErrorBanner message={error} tone="error" onDismiss={() => setError("")} />
      <ErrorBanner message={message} tone="success" onDismiss={() => setMessage("")} />

      <div className="stats-grid">
        <StatCard label="Visible Job Logs" value={logs.length} hint="Latest rows fetched into the page" icon={Database} />
        <StatCard label="Successful Jobs" value={successCount} hint="SUCCESS rows in current view" icon={Workflow} tone="success" />
        <StatCard label="Failed Jobs" value={failureCount} hint="FAIL rows in current view" icon={RefreshCcw} tone="warning" />
      </div>

      <div className="content-grid three-column">
        <SectionCard
          title="Onboard Asset"
          description="Create or update an asset from yfinance metadata."
        >
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
        </SectionCard>

        <SectionCard
          title="Fetch Prices"
          description="Pull one symbol's OHLCV rows into price_history using preset period and interval options."
        >
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
              <select
                value={priceForm.period}
                onChange={(event) => setPriceForm((current) => ({ ...current, period: event.target.value }))}
              >
                {periodOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <label className="form-field">
              <span>Interval</span>
              <select
                value={priceForm.interval}
                onChange={(event) => setPriceForm((current) => ({ ...current, interval: event.target.value }))}
              >
                {intervalOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <p className="form-help">Use shorter intervals for intraday candles and 1d for longer windows.</p>
            <button type="submit" className="secondary-button" disabled={submitting}>
              Fetch Symbol Prices
            </button>
          </form>
        </SectionCard>

        <SectionCard
          title="Fetch All Active"
          description="Run the batch fetch for every active asset with the same yfinance window."
        >
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
              <select
                value={batchForm.period}
                onChange={(event) => setBatchForm((current) => ({ ...current, period: event.target.value }))}
              >
                {periodOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <label className="form-field">
              <span>Interval</span>
              <select
                value={batchForm.interval}
                onChange={(event) => setBatchForm((current) => ({ ...current, interval: event.target.value }))}
              >
                {intervalOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </label>
            <p className="form-help">Batch mode is useful after onboarding or when refreshing the curated asset universe.</p>
            <button type="submit" className="secondary-button" disabled={submitting}>
              Fetch All Active
            </button>
          </form>
        </SectionCard>
      </div>

      <SectionCard
        title="Recent Scraper Logs"
        description="Latest rows from scraper_logs, including ETL and downstream pipeline jobs."
      >

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
                    <td>
                      <span className={`badge ${log.status === "SUCCESS" ? "badge-success" : "badge-danger"}`}>
                        {log.status}
                      </span>
                    </td>
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
      </SectionCard>
    </section>
  );
}
