import {
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import EmptyState from "../components/EmptyState.jsx";


const signalColors = {
  BUY: "#16a34a",
  HOLD: "#2563eb",
  SELL: "#dc2626",
};


export default function SignalSummaryChart({ signals = [] }) {
  if (!signals.length) {
    return (
      <div className="chart-card">
        <div className="section-header">
          <div>
            <h3>Latest Signal Mix</h3>
            <p>No stored signals are available yet.</p>
          </div>
        </div>

        <div className="chart-wrapper chart-empty">
          <EmptyState
            title="No signal data"
            description="Run the AI pipeline to populate BUY, HOLD, and SELL signal rows."
          />
        </div>
      </div>
    );
  }

  const summary = ["BUY", "HOLD", "SELL"].map((signalType) => ({
    signalType,
    count: signals.filter((signal) => signal.signal_type === signalType).length,
  }));

  return (
    <div className="chart-card">
      <div className="section-header">
        <div>
          <h3>Latest Signal Mix</h3>
          <p>Counts from the latest backend signal records.</p>
        </div>
      </div>

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={summary}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="signalType" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" radius={[8, 8, 0, 0]}>
              {summary.map((entry) => (
                <Cell key={entry.signalType} fill={signalColors[entry.signalType]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
