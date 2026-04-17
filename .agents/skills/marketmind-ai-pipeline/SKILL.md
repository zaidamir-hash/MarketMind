---
name: marketmind-ai-pipeline
description: Use when implementing MarketMind AI modules: regression price prediction, classification signals, HMM regimes, Bayesian risk inference, and Genetic Algorithm optimization.
---

Implement AI modules in small independent services.
Keep implementations simple, demo-friendly, and easy to explain.
Do not overengineer the AI stack.

Models:

- Regression/classification: scikit-learn
- HMM: hmmlearn
- Bayesian Network: pgmpy
- Genetic Algorithm: DEAP

Database outputs:

- AI_PREDICTIONS
- MARKET_SIGNALS
- HMM_STATES
- RISK_INDICATORS.risk_score and risk_label
- PORTFOLIO_OPTIMISATION

Do not make AI code depend on frontend.
Do not overwrite historical outputs unless explicitly instructed.
Prefer append-only output records for model tracking.
Do not add any news, sentiment, AI summaries, or Claude-related tables.
