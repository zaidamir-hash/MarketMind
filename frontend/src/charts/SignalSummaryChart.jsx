import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";


export default function SignalSummaryChart({ signals = [] }) {
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
            <Bar dataKey="count" fill="#2563eb" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
