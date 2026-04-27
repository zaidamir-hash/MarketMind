import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { getApiErrorMessage } from "../services/api.js";


export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await register(form);
      navigate("/login", {
        replace: true,
        state: {
          message: "Registration completed. You can now log in.",
        },
      });
    } catch (submitError) {
      setError(getApiErrorMessage(submitError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-panel">
        <div className="auth-hero">
          <div>
            <span className="page-header-eyebrow">MarketMind</span>
            <h2>Create a user for the full MarketMind workflow.</h2>
            <p>
              Registration stays simple: one local JWT-backed account is enough to test protected ETL, portfolio,
              trade, alert, and optimizer flows against the real backend.
            </p>
          </div>

          <div className="pill-row">
            <span className="pill">Integrated platform</span>
            <span className="pill">Real JWT auth</span>
            <span className="pill">No mock portfolio actions</span>
          </div>

          <ul>
            <li>Use a memorable username for Swagger, PowerShell, and frontend testing.</li>
            <li>The backend stores password hashes only; the UI never exposes them.</li>
            <li>After registering, log in once and keep the session active for protected tools.</li>
          </ul>
        </div>

        <div className="auth-card">
          <div className="auth-header">
            <h1>Create Account</h1>
            <p>Register a MarketMind user to unlock ETL, portfolio, and alert tools.</p>
          </div>

          <ErrorBanner message={error} tone="error" onDismiss={() => setError("")} />

          <form className="form-grid" onSubmit={handleSubmit}>
            <label className="form-field">
              <span>Username</span>
              <input
                type="text"
                value={form.username}
                onChange={(event) => setForm((current) => ({ ...current, username: event.target.value }))}
                required
              />
            </label>

            <label className="form-field">
              <span>Email</span>
              <input
                type="email"
                value={form.email}
                onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                required
              />
            </label>

            <label className="form-field">
              <span>Password</span>
              <input
                type="password"
                minLength="8"
                value={form.password}
                onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
                required
              />
            </label>

            <label className="form-field">
              <span>Full Name</span>
              <input
                type="text"
                value={form.full_name}
                onChange={(event) => setForm((current) => ({ ...current, full_name: event.target.value }))}
              />
            </label>

            <button type="submit" className="primary-button" disabled={submitting}>
              {submitting ? "Creating account..." : "Register"}
            </button>
          </form>

          <p className="auth-footer">
            Already registered? <Link to="/login">Go to login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
