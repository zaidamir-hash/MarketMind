import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import StatCard from "../components/StatCard.jsx";
import SignalSummaryChart from "../charts/SignalSummaryChart.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { listPredictions, listSignals } from "../services/aiService.js";
import { listActiveAssets, listAssets } from "../services/assetsService.js";
import { listEtlLogs } from "../services/etlService.js";
import { getApiErrorMessage } from "../services/api.js";
import { formatDateTime } from "../services/formatters.js";
import { listPortfolios } from "../services/portfolioService.js";
import { listRiskIndicators } from "../services/riskService.js";


const quickLinks = [
  { to: "/assets", label: "Assets" },
  { to: "/etl-tools", label: "ETL Tools" },
  { to: "/risk-indicators", label: "Risk Indicators" },
  { to: "/predictions", label: "Predictions" },
  { to: "/portfolios", label: "Portfolios" },
  { to: "/alerts", label: "Alerts" },
];


export default function Dashboard() {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState({
    totalAssets: 0,
    activeAssets: 0,
    predictions: [],
    signals: [],
    riskIndicators: [],
    portfolios: [],
    etlLogs: [],
  });

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError("");

      const requests = await Promise.allSettled([
        listAssets(),
        listActiveAssets(),
        listPredictions({ limit: 50 }),
        listSignals({ limit: 50 }),
        listRiskIndicators({ limit: 50 }),
        isAuthenticated ? listPortfolios() : Promise.resolve([]),
        isAuthenticated ? listEtlLogs(5) : Promise.resolve([]),
      ]);

      const [allAssets, activeAssets, predictions, signals, risks, portfolios, etlLogs] = requests;
      const failures = requests
        .filter((result) => result.status === "rejected")
        .map((result) => getApiErrorMessage(result.reason));

      setSummary({
        totalAssets: allAssets.status === "fulfilled" ? allAssets.value.length : 0,
        activeAssets: activeAssets.status === "fulfilled" ? activeAssets.value.length : 0,
        predictions: predictions.status === "fulfilled" ? predictions.value : [],
        signals: signals.status === "fulfilled" ? signals.value : [],
        riskIndicators: risks.status === "fulfilled" ? risks.value : [],
        portfolios: portfolios.status === "fulfilled" ? portfolios.value : [],
        etlLogs: etlLogs.status === "fulfilled" ? etlLogs.value : [],
      });

      if (failures.length > 0) {
        setError(failures[0]);
      }

      setLoading(false);
    }

    loadDashboard();
  }, [isAuthenticated]);

  if (loading) {
    return <LoadingSpinner label="Loading dashboard..." />;
  }

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>High-level overview of the current MarketMind backend state.</p>
        </div>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError("")} />

      <div className="stats-grid">
        <StatCard label="Total Assets" value={summary.totalAssets} />
        <StatCard label="Active Assets" value={summary.activeAssets} />
        <StatCard label="Latest Predictions" value={summary.predictions.length} />
        <StatCard label="Latest Signals" value={summary.signals.length} />
        <StatCard
          label="Portfolios"
          value={isAuthenticated ? summary.portfolios.length : "Login Required"}
        />
        <StatCard label="Risk Rows" value={summary.riskIndicators.length} />
      </div>

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Quick Actions</h2>
            <p>Jump directly into the main demo sections.</p>
          </div>
        </div>
        <div className="quick-links">
          {quickLinks.map((link) => (
            <Link key={link.to} to={link.to} className="secondary-button">
              {link.label}
            </Link>
          ))}
        </div>
      </div>

      <div className="content-grid two-column">
        <SignalSummaryChart signals={summary.signals} />

        <div className="card">
          <div className="section-header">
            <div>
              <h2>Recent ETL Logs</h2>
              <p>Shown only when you are authenticated.</p>
            </div>
          </div>
          {!isAuthenticated ? (
            <EmptyState title="Login required" description="Authenticate to read ETL logs." />
          ) : summary.etlLogs.length === 0 ? (
            <EmptyState title="No ETL logs yet" description="Run onboarding or price ETL jobs first." />
          ) : (
            <div className="list-stack">
              {summary.etlLogs.map((log) => (
                <div key={log.log_id} className="list-row">
                  <div>
                    <strong>{log.job_name}</strong>
                    <p>{formatDateTime(log.started_at)}</p>
                  </div>
                  <span className={`badge ${log.status === "SUCCESS" ? "badge-success" : "badge-danger"}`}>
                    {log.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
