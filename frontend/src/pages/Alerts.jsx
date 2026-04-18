import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { createAlert, deactivateAlert, listAlertLogs, listAlerts } from "../services/alertService.js";
import { getApiErrorMessage } from "../services/api.js";
import { formatDateTime, formatNumber } from "../services/formatters.js";


const defaultAlertForm = {
  symbol: "AAPL",
  condition: "ABOVE",
  threshold: 100,
};


export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState(defaultAlertForm);
  const [activeOnly, setActiveOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadAlertData() {
    setLoading(true);
    try {
      const [alertsData, logsData] = await Promise.all([
        listAlerts(activeOnly),
        listAlertLogs(50),
      ]);
      setAlerts(alertsData);
      setLogs(logsData);
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAlertData();
  }, [activeOnly]);

  async function handleCreate(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await createAlert(form);
      setMessage(`Created alert for ${form.symbol}.`);
      setForm(defaultAlertForm);
      await loadAlertData();
    } catch (createError) {
      setError(getApiErrorMessage(createError));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDeactivate(alertId) {
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await deactivateAlert(alertId);
      setMessage("Alert deactivated.");
      await loadAlertData();
    } catch (deactivateError) {
      setError(getApiErrorMessage(deactivateError));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <LoadingSpinner label="Loading alerts..." />;
  }

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>Alerts</h1>
          <p>Create price alerts, manage active rules, and inspect trigger-generated alert logs.</p>
        </div>
      </div>

      <ErrorBanner message={error || message} onDismiss={() => { setError(""); setMessage(""); }} />

      <div className="content-grid two-column">
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Create Alert</h2>
              <p>The app inserts into `alerts`; the database trigger writes `alert_logs` later.</p>
            </div>
          </div>

          <form className="form-grid" onSubmit={handleCreate}>
            <label className="form-field">
              <span>Symbol</span>
              <input
                type="text"
                value={form.symbol}
                onChange={(event) => setForm((current) => ({ ...current, symbol: event.target.value.toUpperCase() }))}
                required
              />
            </label>
            <label className="form-field">
              <span>Condition</span>
              <select
                value={form.condition}
                onChange={(event) => setForm((current) => ({ ...current, condition: event.target.value }))}
              >
                <option value="ABOVE">ABOVE</option>
                <option value="BELOW">BELOW</option>
              </select>
            </label>
            <label className="form-field">
              <span>Threshold</span>
              <input
                type="number"
                min="0"
                step="0.000001"
                value={form.threshold}
                onChange={(event) => setForm((current) => ({ ...current, threshold: event.target.value }))}
                required
              />
            </label>
            <button type="submit" className="primary-button" disabled={submitting}>
              {submitting ? "Creating..." : "Create Alert"}
            </button>
          </form>
        </div>

        <div className="card">
          <div className="section-header">
            <div>
              <h2>Alert Rules</h2>
              <p>Filter the authenticated user's alerts.</p>
            </div>
          </div>
          <label className="inline-toggle">
            <input
              type="checkbox"
              checked={activeOnly}
              onChange={(event) => setActiveOnly(event.target.checked)}
            />
            <span>Show active alerts only</span>
          </label>

          {alerts.length === 0 ? (
            <EmptyState title="No alerts yet" description="Create an alert to watch a stored asset price." />
          ) : (
            <div className="table-shell">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Condition</th>
                    <th>Threshold</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert) => (
                    <tr key={alert.alert_id}>
                      <td>{alert.symbol}</td>
                      <td>{alert.condition}</td>
                      <td>{formatNumber(alert.threshold)}</td>
                      <td>{alert.is_active ? "Active" : "Inactive"}</td>
                      <td>{formatDateTime(alert.created_at)}</td>
                      <td>
                        {alert.is_active ? (
                          <button
                            type="button"
                            className="link-button danger-text"
                            onClick={() => handleDeactivate(alert.alert_id)}
                          >
                            Deactivate
                          </button>
                        ) : (
                          "-"
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Alert Logs</h2>
            <p>Rows created automatically by the database trigger after price inserts.</p>
          </div>
        </div>

        {logs.length === 0 ? (
          <EmptyState title="No alert logs yet" description="Matching price inserts have not fired any alerts yet." />
        ) : (
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Triggered Price</th>
                  <th>Fired At</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.log_id}>
                    <td>{log.symbol}</td>
                    <td>{formatNumber(log.triggered_price)}</td>
                    <td>{formatDateTime(log.fired_at)}</td>
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
