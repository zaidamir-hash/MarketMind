import { useEffect, useState } from "react";
import { Gauge, Minus, TrendingDown, TrendingUp } from "lucide-react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import SectionCard from "../components/SectionCard.jsx";
import StatCard from "../components/StatCard.jsx";
import { getApiErrorMessage } from "../services/api.js";
import { formatDateTime, formatNumber } from "../services/formatters.js";
import { listRegimes } from "../services/aiService.js";


export default function Regimes() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRows() {
      setLoading(true);
      try {
        const data = await listRegimes({ activeOnly: true, limit: 100 });
        setRows(data);
      } catch (loadError) {
        setError(getApiErrorMessage(loadError));
      } finally {
        setLoading(false);
      }
    }

    loadRows();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Loading regimes..." />;
  }

  const visibleRows = rows.filter((row) => !filter || row.symbol?.includes(filter.toUpperCase()));
  const bullCount = rows.filter((row) => row.state_label === "BULL").length;
  const bearCount = rows.filter((row) => row.state_label === "BEAR").length;
  const sidewaysCount = rows.filter((row) => row.state_label === "SIDEWAYS").length;

  return (
    <section className="page-shell">
      <PageHeader
        eyebrow="AI outputs"
        title="Regimes"
        description="Latest HMM-style market regime classifications by asset."
      />

      <ErrorBanner message={error} tone="error" onDismiss={() => setError("")} />

      <div className="stats-grid">
        <StatCard label="Visible Regimes" value={visibleRows.length} hint="Rows after local filtering" icon={Gauge} />
        <StatCard label="BULL" value={bullCount} hint="Positive detected regime" icon={TrendingUp} tone="success" />
        <StatCard label="BEAR" value={bearCount} hint="Negative detected regime" icon={TrendingDown} tone="danger" />
        <StatCard label="SIDEWAYS" value={sidewaysCount} hint="Neutral detected regime" icon={Minus} />
      </div>

      <SectionCard
        title="Regime Feed"
        description="Filter locally by symbol and inspect the latest state classification and probability."
        actions={(
          <input
            className="search-input"
            type="text"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            placeholder="Filter symbol"
          />
        )}
      >

        {visibleRows.length === 0 ? (
          <EmptyState title="No regimes found" description="Run the AI pipeline first." />
        ) : (
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>State</th>
                  <th>Index</th>
                  <th>Probability</th>
                  <th>Detected</th>
                </tr>
              </thead>
              <tbody>
                {visibleRows.map((row) => (
                  <tr key={row.hmm_state_id}>
                    <td>{row.symbol}</td>
                    <td>
                      <span className={`badge ${row.state_label === "BULL" ? "badge-success" : row.state_label === "BEAR" ? "badge-danger" : "badge-neutral"}`}>
                        {row.state_label}
                      </span>
                    </td>
                    <td>{row.state_index}</td>
                    <td>{formatNumber(row.probability)}</td>
                    <td>{formatDateTime(row.detected_at)}</td>
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
