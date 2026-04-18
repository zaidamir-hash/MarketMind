import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
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

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>Signals</h1>
          <p>Latest BUY, HOLD, and SELL outputs from the rule-based signal generator.</p>
        </div>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError("")} />

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Signal Feed</h2>
            <p>Filter locally by symbol.</p>
          </div>
          <input
            className="search-input"
            type="text"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            placeholder="Filter symbol"
          />
        </div>

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
                    <td>{row.signal_type}</td>
                    <td>{row.model_source}</td>
                    <td>{formatNumber(row.strength)}</td>
                    <td>{row.regime || "-"}</td>
                    <td>{formatDateTime(row.generated_at)}</td>
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
