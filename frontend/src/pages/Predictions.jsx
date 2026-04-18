import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { getApiErrorMessage } from "../services/api.js";
import { listPredictions } from "../services/aiService.js";
import { formatDateTime, formatNumber } from "../services/formatters.js";


export default function Predictions() {
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRows() {
      setLoading(true);
      try {
        const data = await listPredictions({ activeOnly: true, limit: 100 });
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
    return <LoadingSpinner label="Loading predictions..." />;
  }

  const visibleRows = rows.filter((row) => !filter || row.symbol?.includes(filter.toUpperCase()));

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>Predictions</h1>
          <p>Latest LinearRegression predictions produced by the backend AI pipeline.</p>
        </div>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError("")} />

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Prediction Feed</h2>
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
          <EmptyState title="No predictions found" description="Run the AI pipeline first." />
        ) : (
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Model</th>
                  <th>Predicted Price</th>
                  <th>Confidence</th>
                  <th>Predicted For</th>
                  <th>Actual Price</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {visibleRows.map((row) => (
                  <tr key={row.prediction_id}>
                    <td>{row.symbol}</td>
                    <td>{row.model_type}</td>
                    <td>{formatNumber(row.predicted_price)}</td>
                    <td>{formatNumber(row.confidence)}</td>
                    <td>{formatDateTime(row.predicted_for)}</td>
                    <td>{formatNumber(row.actual_price)}</td>
                    <td>{formatDateTime(row.created_at)}</td>
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
