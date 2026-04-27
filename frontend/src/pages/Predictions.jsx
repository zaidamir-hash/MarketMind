import { useEffect, useState } from "react";
import { BrainCircuit, CalendarClock, CheckCircle2 } from "lucide-react";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import SectionCard from "../components/SectionCard.jsx";
import StatCard from "../components/StatCard.jsx";
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
  const actualPriceCount = rows.filter((row) => row.actual_price !== null && row.actual_price !== undefined).length;
  const highConfidenceCount = rows.filter((row) => Number(row.confidence) >= 0.7).length;

  return (
    <section className="page-shell">
      <PageHeader
        eyebrow="AI outputs"
        title="Predictions"
        description="Latest LinearRegression predictions produced by the backend AI pipeline."
      />

      <ErrorBanner message={error} tone="error" onDismiss={() => setError("")} />

      <div className="stats-grid">
        <StatCard label="Visible Predictions" value={visibleRows.length} hint="Rows after local filtering" icon={BrainCircuit} />
        <StatCard label="Stored Predictions" value={rows.length} hint="Latest fetched feed size" icon={CalendarClock} />
        <StatCard label="Actual Price Filled" value={actualPriceCount} hint="Trigger-managed backfill rows" icon={CheckCircle2} tone="success" />
        <StatCard label="High Confidence" value={highConfidenceCount} hint="confidence >= 0.70" icon={BrainCircuit} tone="warning" />
      </div>

      <SectionCard
        title="Prediction Feed"
        description="Filter locally by symbol and review the latest backend prediction rows."
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
      </SectionCard>
    </section>
  );
}
