import { useEffect, useState } from "react";
import { ArrowDownRight, ArrowRightLeft, ArrowUpRight, BarChart3 } from "lucide-react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import SectionCard from "../components/SectionCard.jsx";
import StatCard from "../components/StatCard.jsx";
import { getApiErrorMessage } from "../services/api.js";
import { formatDateTime, formatNumber } from "../services/formatters.js";
import { listSignals } from "../services/aiService.js";


export default function Signals() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRows() {
      setLoading(true);
      try {
        const data = await listSignals({ activeOnly: true, limit: 100 });
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
    return <LoadingSpinner label="Loading signals..." />;
  }

  const visibleRows = rows.filter((row) => !filter || row.symbol?.includes(filter.toUpperCase()));
  const buyCount = rows.filter((row) => row.signal_type === "BUY").length;
  const holdCount = rows.filter((row) => row.signal_type === "HOLD").length;
  const sellCount = rows.filter((row) => row.signal_type === "SELL").length;

  return (
    <section className="page-shell">
      <PageHeader
        eyebrow="AI outputs"
        title="Signals"
        description="Latest BUY, HOLD, and SELL outputs from the rule-based signal generator."
      />

      <ErrorBanner message={error} tone="error" onDismiss={() => setError("")} />

      <div className="stats-grid">
        <StatCard label="Visible Signals" value={visibleRows.length} hint="Rows after local filtering" icon={BarChart3} />
        <StatCard label="BUY" value={buyCount} hint="Positive rule-based signals" icon={ArrowUpRight} tone="success" />
        <StatCard label="HOLD" value={holdCount} hint="Neutral holding guidance" icon={ArrowRightLeft} />
        <StatCard label="SELL" value={sellCount} hint="Protective or downside calls" icon={ArrowDownRight} tone="danger" />
      </div>

      <SectionCard
        title="Signal Feed"
        description="Filter locally by symbol and compare strength, source, and detected regime."
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
          <EmptyState title="No signals found" description="Run the AI pipeline first." />
        ) : (
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Signal</th>
                  <th>Model Source</th>
                  <th>Strength</th>
                  <th>Regime</th>
                  <th>Generated</th>
                </tr>
              </thead>
              <tbody>
                {visibleRows.map((row) => (
                  <tr key={row.signal_id}>
                    <td>{row.symbol}</td>
                    <td>
                      <span className={`badge ${row.signal_type === "BUY" ? "badge-success" : row.signal_type === "SELL" ? "badge-danger" : "badge-neutral"}`}>
                        {row.signal_type}
                      </span>
                    </td>
                    <td>{row.model_source}</td>
                    <td>{formatNumber(row.strength)}</td>
                    <td>{row.regime ? <span className="badge badge-info">{row.regime}</span> : "-"}</td>
                    <td>{formatDateTime(row.generated_at)}</td>
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
