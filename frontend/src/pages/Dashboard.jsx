import { useEffect, useState } from "react";
import {
  ArrowRight,
  BrainCircuit,
  Database,
  ShieldCheck,
  Sparkles,
  WalletCards,
} from "lucide-react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import SectionCard from "../components/SectionCard.jsx";
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
  const [failures, setFailures] = useState([]);
  const [summary, setSummary] = useState({
    totalAssets: null,
    activeAssets: null,
    predictions: null,
    signals: null,
    riskIndicators: null,
    portfolios: null,
    etlLogs: null,
  });

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setFailures([]);

      const requestLabels = [
        "assets",
        "active assets",
        "predictions",
        "signals",
        "risk indicators",
        "portfolios",
        "job activity",
      ];

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
      const nextFailures = requests.reduce((items, result, index) => {
        if (result.status === "rejected") {
          items.push({
            section: requestLabels[index],
            message: getApiErrorMessage(result.reason),
          });
        }
        return items;
      }, []);

      setSummary({
        totalAssets: allAssets.status === "fulfilled" ? allAssets.value.length : null,
        activeAssets: activeAssets.status === "fulfilled" ? activeAssets.value.length : null,
        predictions: predictions.status === "fulfilled" ? predictions.value : null,
        signals: signals.status === "fulfilled" ? signals.value : null,
        riskIndicators: risks.status === "fulfilled" ? risks.value : null,
        portfolios: portfolios.status === "fulfilled" ? portfolios.value : null,
        etlLogs: etlLogs.status === "fulfilled" ? etlLogs.value : null,
      });

      setFailures(nextFailures);

      setLoading(false);
    }

    loadDashboard();
  }, [isAuthenticated]);

  if (loading) {
    return <LoadingSpinner label="Loading dashboard..." />;
  }

  const failureMessage = failures.length > 0
    ? `Some sections are unavailable right now: ${failures.map((item) => item.section).join(", ")}.`
    : "";
  const latestSignals = summary.signals ?? [];
  const latestPredictions = summary.predictions ?? [];
  const latestRisks = summary.riskIndicators ?? [];
  const latestPortfolios = summary.portfolios ?? [];
  const latestLogs = summary.etlLogs ?? [];

  return (
    <section className="page-shell">
      <PageHeader
        eyebrow="System overview"
        title="Dashboard"
        description="High-level overview of the current MarketMind backend state and workflow readiness."
      />

      <ErrorBanner
        title="Partial dashboard outage"
        message={failureMessage}
        tone="warning"
        onDismiss={() => setFailures([])}
      />

      <div className="stats-grid">
        <StatCard
          label="Tracked Assets"
          value={summary.totalAssets ?? "--"}
          hint="Public asset registry"
          icon={Database}
        />
        <StatCard
          label="Active Assets"
          value={summary.activeAssets ?? "--"}
          hint="Currently marked active"
          icon={Sparkles}
          tone="success"
        />
        <StatCard
          label="Latest Predictions"
          value={summary.predictions ? latestPredictions.length : "--"}
          hint="Most recent prediction feed"
          icon={BrainCircuit}
        />
        <StatCard
          label="Latest Signals"
          value={summary.signals ? latestSignals.length : "--"}
          hint="Latest stored signal rows"
          icon={ArrowRight}
          tone="warning"
        />
        <StatCard
          label="Portfolios"
          value={isAuthenticated ? (summary.portfolios ? latestPortfolios.length : "--") : "Login"}
          hint={isAuthenticated ? "Authenticated workspace" : "Protected route"}
          icon={WalletCards}
        />
        <StatCard
          label="Risk Rows"
          value={summary.riskIndicators ? latestRisks.length : "--"}
          hint="Latest risk indicator rows"
          icon={ShieldCheck}
        />
      </div>

      <SectionCard
        title="Quick Actions"
        description="Jump directly into the main sections."
      >
        <div className="quick-links">
          {quickLinks.map((link) => (
            <Link key={link.to} to={link.to} className="secondary-button">
              {link.label}
            </Link>
          ))}
        </div>
      </SectionCard>

      <div className="content-grid two-column">
        <SignalSummaryChart signals={latestSignals} />

        <SectionCard
          title="Recent Job Activity"
          description="Most recent scraper and pipeline jobs from the backend operational log."
        >
          {!isAuthenticated ? (
            <EmptyState
              title="Login required"
              description="Authenticate to inspect protected ETL, risk, and AI job logs."
              action={<Link to="/login" className="secondary-button">Go to login</Link>}
            />
          ) : summary.etlLogs === null ? (
            <EmptyState
              title="Job activity unavailable"
              description="The dashboard could not load scraper logs from the backend right now."
            />
          ) : latestLogs.length === 0 ? (
            <EmptyState
              title="No job activity yet"
              description="Run onboarding, pricing, risk, or AI jobs to populate the activity feed."
            />
          ) : (
            <div className="list-stack">
              {latestLogs.map((log) => (
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
        </SectionCard>
      </div>

      <SectionCard
        title="Pipeline Snapshot"
        description="A concise view of whether downstream analytics are already populated."
      >
        <div className="metric-strip">
          <div className="metric-tile">
            <span>Risk coverage</span>
            <strong>{summary.riskIndicators ? latestRisks.length : "--"}</strong>
            <span>Latest rows currently visible in the public risk feed.</span>
          </div>
          <div className="metric-tile">
            <span>Prediction coverage</span>
            <strong>{summary.predictions ? latestPredictions.length : "--"}</strong>
            <span>Latest stored prediction rows exposed by the AI routes.</span>
          </div>
          <div className="metric-tile">
            <span>Signal coverage</span>
            <strong>{summary.signals ? latestSignals.length : "--"}</strong>
            <span>Latest rule-based signal rows ready for the frontend pages.</span>
          </div>
        </div>
      </SectionCard>
    </section>
  );
}
