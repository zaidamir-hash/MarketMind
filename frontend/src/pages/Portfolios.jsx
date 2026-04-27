import { useEffect, useState } from "react";
import { Landmark, PiggyBank, Star, WalletCards } from "lucide-react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import PageHeader from "../components/PageHeader.jsx";
import SectionCard from "../components/SectionCard.jsx";
import StatCard from "../components/StatCard.jsx";
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

  const totalCash = rows.reduce((sum, portfolio) => sum + Number(portfolio.current_cash ?? 0), 0);
  const defaultCount = rows.filter((portfolio) => portfolio.is_default).length;

  return (
    <section className="page-shell">
      <PageHeader
        eyebrow="Protected workspace"
        title="Portfolios"
        description="Create and manage your authenticated user portfolios."
      />

      <ErrorBanner message={error} tone="error" onDismiss={() => setError("")} />
      <ErrorBanner message={message} tone="success" onDismiss={() => setMessage("")} />

      <div className="stats-grid">
        <StatCard label="Portfolios" value={rows.length} hint="Authenticated user rows" icon={WalletCards} />
        <StatCard label="Default Portfolios" value={defaultCount} hint="Marked as default" icon={Star} />
        <StatCard label="Current Cash" value={formatCurrency(totalCash)} hint="Sum of current_cash across rows" icon={PiggyBank} tone="success" />
        <StatCard label="Base Capital" value={formatCurrency(rows.reduce((sum, portfolio) => sum + Number(portfolio.initial_capital ?? 0), 0))} hint="Initial capital across portfolios" icon={Landmark} />
      </div>

      <div className="content-grid two-column">
        <SectionCard
          title="Create Portfolio"
          description="The backend will set current_cash equal to the initial capital."
        >

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
        </SectionCard>

        <SectionCard
          title="Your Portfolios"
          description="Open a portfolio to trade, review holdings, and run optimization."
        >

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
                    <small>{portfolio.is_default ? "Default portfolio" : "Standard portfolio"}</small>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </SectionCard>
      </div>
    </section>
  );
}
