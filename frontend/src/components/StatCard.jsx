export default function StatCard({ label, value, hint, icon: Icon, tone = "default" }) {
  return (
    <article className={`stat-card stat-card-${tone}`}>
      <div className="stat-card-top">
        <span className="stat-label">{label}</span>
        {Icon ? (
          <span className="stat-icon">
            <Icon size={16} />
          </span>
        ) : null}
      </div>
      <strong className="stat-value">{value}</strong>
      {hint ? <span className="stat-hint">{hint}</span> : null}
    </article>
  );
}
