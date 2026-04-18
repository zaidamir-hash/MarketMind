import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import { getApiErrorMessage } from "../services/api.js";
import { formatCurrency, formatDateTime } from "../services/formatters.js";
import { createPortfolio, listPortfolios } from "../services/portfolioService.js";


const defaultPortfolioForm = {
  name: "",
  initial_capital: 10000,
  is_default: false,
};


export default function Portfolios() {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState(defaultPortfolioForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function loadRows() {
    setLoading(true);
    try {
      const data = await listPortfolios();
      setRows(data);
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRows();
  }, []);

  async function handleCreate(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      const result = await createPortfolio(form);
      setMessage(`Created portfolio ${result.name}.`);
      setForm(defaultPortfolioForm);
      await loadRows();
    } catch (createError) {
      setError(getApiErrorMessage(createError));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <LoadingSpinner label="Loading portfolios..." />;
  }

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <h1>Portfolios</h1>
          <p>Create and manage your authenticated user portfolios.</p>
        </div>
      </div>

      <ErrorBanner message={error || message} onDismiss={() => { setError(""); setMessage(""); }} />

      <div className="content-grid two-column">
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Create Portfolio</h2>
              <p>The backend will set `current_cash` equal to the initial capital.</p>
            </div>
          </div>

          <form className="form-grid" onSubmit={handleCreate}>
            <label className="form-field">
              <span>Name</span>
              <input
                type="text"
                value={form.name}
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                required
              />
            </label>

            <label className="form-field">
              <span>Initial Capital</span>
              <input
                type="number"
                min="0"
                step="0.01"
                value={form.initial_capital}
                onChange={(event) => setForm((current) => ({ ...current, initial_capital: event.target.value }))}
              />
            </label>

            <label className="inline-toggle">
              <input
                type="checkbox"
                checked={form.is_default}
                onChange={(event) => setForm((current) => ({ ...current, is_default: event.target.checked }))}
              />
              <span>Set as default portfolio</span>
            </label>

            <button type="submit" className="primary-button" disabled={submitting}>
              {submitting ? "Creating..." : "Create Portfolio"}
            </button>
          </form>
        </div>

        <div className="card">
          <div className="section-header">
            <div>
              <h2>Your Portfolios</h2>
              <p>Open a portfolio to trade, review holdings, and run optimization.</p>
            </div>
          </div>

          {rows.length === 0 ? (
            <EmptyState title="No portfolios yet" description="Create your first portfolio to get started." />
          ) : (
            <div className="list-stack">
              {rows.map((portfolio) => (
                <Link key={portfolio.portfolio_id} to={`/portfolios/${portfolio.portfolio_id}`} className="list-row link-row">
                  <div>
                    <strong>{portfolio.name}</strong>
                    <p>{formatDateTime(portfolio.created_at)}</p>
                  </div>
                  <div className="aligned-right">
                    <span>{formatCurrency(portfolio.current_cash)}</span>
                    <small>{portfolio.is_default ? "Default" : "Standard"}</small>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
