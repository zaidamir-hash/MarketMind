import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
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

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>Regimes</h1>
          <p>Latest HMM-style market regime classifications by asset.</p>
        </div>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError("")} />

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Regime Feed</h2>
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
                    <td>{row.state_label}</td>
                    <td>{row.state_index}</td>
                    <td>{formatNumber(row.probability)}</td>
                    <td>{formatDateTime(row.detected_at)}</td>
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
