import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { getApiErrorMessage } from "../services/api.js";


export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, loading } = useAuth();
  const [form, setForm] = useState({
    username_or_email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const from = location.state?.from || "/";

  useEffect(() => {
    if (!loading && isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [from, isAuthenticated, loading, navigate]);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await login(form);
      navigate(from, { replace: true });
    } catch (submitError) {
      setError(getApiErrorMessage(submitError));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <LoadingSpinner label="Loading your session..." />;
  }

  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <div className="auth-hero">
          <div>
            <span className="page-header-eyebrow">MarketMind</span>
            <h2>Operate the full platform from one clean workspace.</h2>
            <p>
              Sign in to unlock ETL controls, user portfolios, trades, alerts, and optimization tools while keeping
              the existing backend behavior unchanged.
            </p>
          </div>

          <div className="pill-row">
            <span className="pill">JWT-authenticated routes</span>
            <span className="pill">FastAPI + PostgreSQL</span>
            <span className="pill">React dashboard</span>
          </div>

          <ul>
            <li>Run ETL jobs and inspect system activity.</li>
            <li>Create portfolios, submit trades, and review trigger-managed holdings.</li>
            <li>Create alerts and monitor trigger-generated alert logs.</li>
          </ul>
        </div>

        <div className="auth-card">
          <div className="auth-header">
            <h1>Login</h1>
            <p>Use your MarketMind account to access protected tools and portfolio actions.</p>
          </div>

          <ErrorBanner message={error} tone="error" onDismiss={() => setError("")} />
          <ErrorBanner message={location.state?.message} tone="success" />

          <form className="form-grid" onSubmit={handleSubmit}>
            <label className="form-field">
              <span>Username or Email</span>
              <input
                type="text"
                value={form.username_or_email}
                onChange={(event) => setForm((current) => ({ ...current, username_or_email: event.target.value }))}
                required
              />
            </label>

            <label className="form-field">
              <span>Password</span>
              <input
                type="password"
                value={form.password}
                onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
                required
              />
            </label>

            <button type="submit" className="primary-button" disabled={submitting}>
              {submitting ? "Signing in..." : "Login"}
            </button>
          </form>

          <p className="auth-footer">
            Need an account? <Link to="/register">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
