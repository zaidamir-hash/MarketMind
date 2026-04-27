import { useEffect, useState } from "react";
import { AlertTriangle, BellRing, Siren, Waves } from "lucide-react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import SectionCard from "../components/SectionCard.jsx";
import StatCard from "../components/StatCard.jsx";
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

  const activeCount = alerts.filter((alert) => alert.is_active).length;

  return (
    <section className="page-shell">
      <PageHeader
        eyebrow="Protected workspace"
        title="Alerts"
        description="Create price alerts, manage active rules, and inspect trigger-generated alert logs."
      />

      <ErrorBanner message={error} tone="error" onDismiss={() => setError("")} />
      <ErrorBanner message={message} tone="success" onDismiss={() => setMessage("")} />

      <div className="stats-grid">
        <StatCard label="Alerts" value={alerts.length} hint="Current user alert rows" icon={AlertTriangle} />
        <StatCard label="Active Alerts" value={activeCount} hint="Still eligible to trigger" icon={BellRing} tone="warning" />
        <StatCard label="Alert Logs" value={logs.length} hint="Trigger-created rows" icon={Siren} tone="success" />
        <StatCard label="View Filter" value={activeOnly ? "Active" : "All"} hint="Current rules filter" icon={Waves} />
      </div>

      <div className="content-grid two-column">
        <SectionCard
          title="Create Alert"
          description="The app inserts into alerts; the database trigger writes alert_logs later."
        >

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
        </SectionCard>

        <SectionCard
          title="Alert Rules"
          description="Filter the authenticated user's alerts."
          actions={(
            <label className="inline-toggle">
              <input
                type="checkbox"
                checked={activeOnly}
                onChange={(event) => setActiveOnly(event.target.checked)}
              />
              <span>Show active only</span>
            </label>
          )}
        >

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
                    <td><span className="badge badge-info">{alert.condition}</span></td>
                    <td>{formatNumber(alert.threshold)}</td>
                    <td>
                      <span className={`badge ${alert.is_active ? "badge-success" : "badge-neutral"}`}>
                        {alert.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
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
        </SectionCard>
      </div>

      <SectionCard
        title="Alert Logs"
        description="Rows created automatically by the database trigger after matching price inserts."
      >

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
      </SectionCard>
    </section>
  );
}
