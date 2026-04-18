import { Link } from "react-router-dom";


export default function NotFound() {
  return (
    <section className="page-shell">
      <div className="card">
        <h1>Page Not Found</h1>
        <p>The route you requested does not exist in the current MarketMind frontend.</p>
        <Link className="primary-button" to="/">Back to Dashboard</Link>
      </div>
    </section>
  );
}
