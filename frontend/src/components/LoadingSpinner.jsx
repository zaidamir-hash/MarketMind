export default function LoadingSpinner({ label = "Loading...", inline = false }) {
  return (
    <div className={`loading-state ${inline ? "is-inline" : ""}`}>
      <div className="spinner" />
      <span>{label}</span>
    </div>
  );
}
