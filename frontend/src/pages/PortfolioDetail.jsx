import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import EmptyState from "../components/EmptyState.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import StatCard from "../components/StatCard.jsx";
import { getApiErrorMessage } from "../services/api.js";
import { getAssetCatalog } from "../services/assetsService.js";
import { formatCurrency, formatDateTime, formatPercent } from "../services/formatters.js";
import {
  getPortfolio,
  getPortfolioHoldings,
  getPortfolioPerformance,
  listOptimizations,
  runOptimization,
} from "../services/portfolioService.js";
import { createTrade, listTradesForPortfolio } from "../services/tradeService.js";


function getAvailableTradeCategories(assetCatalog, tradeType, holdings) {
  if (tradeType !== "SELL") {
    return assetCatalog;
  }

  const heldSymbols = new Set(holdings.map((holding) => holding.symbol));
  return assetCatalog
    .map((category) => ({
      ...category,
      options: category.options.filter((option) => heldSymbols.has(option.symbol)),
    }))
    .filter((category) => category.options.length > 0);
}


export default function PortfolioDetail() {
  const { portfolioId } = useParams();
  const [portfolio, setPortfolio] = useState(null);
  const [holdings, setHoldings] = useState([]);
  const [performance, setPerformance] = useState(null);
  const [optimizations, setOptimizations] = useState([]);
  const [trades, setTrades] = useState([]);
  const [assetCatalog, setAssetCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [tradeForm, setTradeForm] = useState({
    category_id: "",
    symbol: "",
    trade_type: "BUY",
    quantity: 1,
  });
  const [optimizationForm, setOptimizationForm] = useState({
    iterations: 250,
  });

  async function loadPortfolioData() {
    setLoading(true);
    setError("");
    try {
      const [
        portfolioData,
        holdingsData,
        performanceData,
        optimizationData,
        tradesData,
      ] = await Promise.all([
        getPortfolio(portfolioId),
        getPortfolioHoldings(portfolioId),
        getPortfolioPerformance(portfolioId),
        listOptimizations(portfolioId),
        listTradesForPortfolio(portfolioId),
      ]);

      setPortfolio(portfolioData);
      setHoldings(holdingsData);
      setPerformance(performanceData);
      setOptimizations(optimizationData);
      setTrades(tradesData);
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    }

    try {
      const catalogData = await getAssetCatalog();
      setAssetCatalog(catalogData.categories ?? []);
    } catch (catalogError) {
      setAssetCatalog([]);
      setError((current) => current || getApiErrorMessage(catalogError));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPortfolioData();
  }, [portfolioId]);

  useEffect(() => {
    const availableCategories = getAvailableTradeCategories(
      assetCatalog,
      tradeForm.trade_type,
      holdings,
    );

    if (availableCategories.length === 0) {
      if (tradeForm.category_id || tradeForm.symbol) {
        setTradeForm((current) => ({
          ...current,
          category_id: "",
          symbol: "",
        }));
      }
      return;
    }

    const nextCategoryId = availableCategories.some(
      (category) => category.category_id === tradeForm.category_id,
    )
      ? tradeForm.category_id
      : availableCategories[0].category_id;

    const nextOptions = availableCategories.find(
      (category) => category.category_id === nextCategoryId,
    )?.options ?? [];

    const nextSymbol = nextOptions.some((option) => option.symbol === tradeForm.symbol)
      ? tradeForm.symbol
      : (nextOptions[0]?.symbol ?? "");

    if (nextCategoryId !== tradeForm.category_id || nextSymbol !== tradeForm.symbol) {
      setTradeForm((current) => ({
        ...current,
        category_id: nextCategoryId,
        symbol: nextSymbol,
      }));
    }
  }, [assetCatalog, holdings, tradeForm.category_id, tradeForm.symbol, tradeForm.trade_type]);

  async function handleTrade(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await createTrade({
        portfolio_id: portfolioId,
        symbol: tradeForm.symbol,
        trade_type: tradeForm.trade_type,
        quantity: tradeForm.quantity,
      });
      setMessage(`${tradeForm.trade_type} trade submitted for ${tradeForm.symbol}.`);
      await loadPortfolioData();
    } catch (tradeError) {
      setError(getApiErrorMessage(tradeError));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleOptimize(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await runOptimization(portfolioId, optimizationForm);
      setMessage("Portfolio optimization completed.");
      await loadPortfolioData();
    } catch (optimizeError) {
      setError(getApiErrorMessage(optimizeError));
    } finally {
      setSubmitting(false);
    }
  }

  const availableTradeCategories = getAvailableTradeCategories(
    assetCatalog,
    tradeForm.trade_type,
    holdings,
  );
  const selectedCategory = availableTradeCategories.find(
    (category) => category.category_id === tradeForm.category_id,
  );
  const availableTradeOptions = selectedCategory?.options ?? [];
  const selectedTradeOption = availableTradeOptions.find(
    (option) => option.symbol === tradeForm.symbol,
  );

  if (loading) {
    return <LoadingSpinner label="Loading portfolio..." />;
  }

  if (!portfolio) {
    return (
      <section className="page-shell">
        <EmptyState title="Portfolio not found" description="Go back to your portfolio list and try again." />
      </section>
    );
  }

  return (
    <section className="page-shell">
      <div className="page-header">
        <div>
          <p className="page-meta"><Link to="/portfolios">Back to portfolios</Link></p>
          <h1>{portfolio.name}</h1>
          <p>Review holdings, trade with the latest stored prices, and run optimization.</p>
        </div>
      </div>

      <ErrorBanner message={error || message} onDismiss={() => { setError(""); setMessage(""); }} />

      {performance ? (
        <div className="stats-grid">
          <StatCard label="Current Cash" value={formatCurrency(performance.current_cash)} />
          <StatCard label="Holdings Value" value={formatCurrency(performance.holdings_value)} />
          <StatCard label="Total Value" value={formatCurrency(performance.total_portfolio_value)} />
          <StatCard label="Total PnL" value={formatCurrency(performance.total_pnl)} />
          <StatCard label="Return %" value={formatPercent(performance.return_pct)} />
          <StatCard label="Priced Holdings" value={performance.priced_holdings} />
        </div>
      ) : null}

      <div className="content-grid two-column">
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Create Trade</h2>
              <p>The backend inserts into `trades` only and lets DB triggers update holdings and cash.</p>
            </div>
          </div>
          {availableTradeCategories.length === 0 ? (
            <EmptyState
              title={tradeForm.trade_type === "SELL" ? "No sellable assets yet" : "Asset catalog unavailable"}
              description={tradeForm.trade_type === "SELL"
                ? "Create BUY trades first so this portfolio has holdings you can sell."
                : "Run the curated universe bootstrap so the trade catalog is ready."}
            />
          ) : (
            <form className="form-grid" onSubmit={handleTrade}>
              <label className="form-field">
                <span>Trade Type</span>
                <select
                  value={tradeForm.trade_type}
                  onChange={(event) => setTradeForm((current) => ({ ...current, trade_type: event.target.value }))}
                >
                  <option value="BUY">BUY</option>
                  <option value="SELL">SELL</option>
                </select>
              </label>
              <label className="form-field">
                <span>Category</span>
                <select
                  value={tradeForm.category_id}
                  onChange={(event) => {
                    const nextCategory = availableTradeCategories.find(
                      (category) => category.category_id === event.target.value,
                    );
                    setTradeForm((current) => ({
                      ...current,
                      category_id: event.target.value,
                      symbol: nextCategory?.options[0]?.symbol ?? "",
                    }));
                  }}
                  required
                >
                  {availableTradeCategories.map((category) => (
                    <option key={category.category_id} value={category.category_id}>
                      {category.category_label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                <span>Asset / Company</span>
                <select
                  value={tradeForm.symbol}
                  onChange={(event) => setTradeForm((current) => ({ ...current, symbol: event.target.value }))}
                  required
                >
                  {availableTradeOptions.map((option) => (
                    <option key={option.symbol} value={option.symbol}>
                      {option.display_name} ({option.symbol})
                    </option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                <span>Quantity</span>
                <input
                  type="number"
                  min="0.00000001"
                  step="0.00000001"
                  value={tradeForm.quantity}
                  onChange={(event) => setTradeForm((current) => ({ ...current, quantity: event.target.value }))}
                  required
                />
              </label>
              <p className="form-help">
                {selectedTradeOption
                  ? `Selected asset: ${selectedTradeOption.display_name} (${selectedTradeOption.symbol})`
                  : "Select a category and asset to trade."}
              </p>
              <button
                type="submit"
                className="primary-button"
                disabled={submitting || !tradeForm.symbol}
              >
                {submitting ? "Submitting..." : "Submit Trade"}
              </button>
            </form>
          )}
        </div>

        <div className="card">
          <div className="section-header">
            <div>
              <h2>Run Optimization</h2>
              <p>Simple random-search optimizer using stored price history for held assets.</p>
            </div>
          </div>
          <form className="form-grid" onSubmit={handleOptimize}>
            <label className="form-field">
              <span>Iterations</span>
              <input
                type="number"
                min="50"
                max="2000"
                value={optimizationForm.iterations}
                onChange={(event) => setOptimizationForm({ iterations: Number(event.target.value) })}
              />
            </label>
            <button type="submit" className="secondary-button" disabled={submitting}>
              {submitting ? "Optimizing..." : "Run Optimization"}
            </button>
          </form>
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <div>
            <h2>Holdings</h2>
            <p>Values shown here come from trigger-managed holdings plus latest stored prices.</p>
          </div>
        </div>
        {holdings.length === 0 ? (
          <EmptyState title="No holdings yet" description="Create BUY trades to populate this portfolio." />
        ) : (
          <div className="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>Quantity</th>
                  <th>Avg Buy</th>
                  <th>Latest Price</th>
                  <th>Market Value</th>
                  <th>Unrealized PnL</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => (
                  <tr key={holding.holding_id}>
                    <td>{holding.symbol}</td>
                    <td>{holding.name}</td>
                    <td>{holding.quantity}</td>
                    <td>{formatCurrency(holding.avg_buy_price)}</td>
                    <td>{formatCurrency(holding.latest_price)}</td>
                    <td>{formatCurrency(holding.market_value)}</td>
                    <td>{formatCurrency(holding.unrealized_pnl)}</td>
                    <td>{formatDateTime(holding.last_updated)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="content-grid two-column">
        <div className="card">
          <div className="section-header">
            <div>
              <h2>Recent Trades</h2>
              <p>Latest trade activity for this portfolio.</p>
            </div>
          </div>
          {trades.length === 0 ? (
            <EmptyState title="No trades yet" description="Use the trade form above to create one." />
          ) : (
            <div className="table-shell">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Type</th>
                    <th>Quantity</th>
                    <th>Executed Price</th>
                    <th>Total Value</th>
                    <th>Traded</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((trade) => (
                    <tr key={trade.trade_id}>
                      <td>{trade.symbol}</td>
                      <td>{trade.trade_type}</td>
                      <td>{trade.quantity}</td>
                      <td>{formatCurrency(trade.executed_price)}</td>
                      <td>{formatCurrency(trade.total_value)}</td>
                      <td>{formatDateTime(trade.traded_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="card">
          <div className="section-header">
            <div>
              <h2>Optimization History</h2>
              <p>Saved rows from `portfolio_optimisation`.</p>
            </div>
          </div>
          {optimizations.length === 0 ? (
            <EmptyState title="No optimization runs yet" description="Run optimization once holdings are ready." />
          ) : (
            <div className="table-shell">
              <table>
                <thead>
                  <tr>
                    <th>Sharpe</th>
                    <th>Expected Return</th>
                    <th>Expected Risk</th>
                    <th>Iterations</th>
                    <th>Weights</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {optimizations.map((row) => (
                    <tr key={row.opt_id}>
                      <td>{row.sharpe_ratio}</td>
                      <td>{row.expected_return ?? "-"}</td>
                      <td>{row.expected_risk ?? "-"}</td>
                      <td>{row.generations_run}</td>
                      <td className="weights-cell">
                        {Object.entries(row.weights).map(([symbol, weight]) => (
                          <span key={symbol}>{symbol}: {weight}</span>
                        ))}
                      </td>
                      <td>{formatDateTime(row.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
