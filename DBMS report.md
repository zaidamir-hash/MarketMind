# MarketMind

## Project Report

Database-Centered Stock and Crypto Intelligence Platform

### Group Members

1. Ali Zeeshan   24K-07492. Hasan Dad   24K-05253. Agha Zaid Amir   24K-0813

Course: Database Systems / Database Management Systems

## 1. Executive Summary

MarketMind is a stock and crypto intelligence platform developed with the database as its core foundation. The system uses PostgreSQL to store market data, user records, portfolios, trades, risk indicators, AI outputs, alerts, and operational logs. The backend and frontend are built around this database layer so that every major feature depends on structured, consistent, and queryable data.

The project demonstrates practical Database Systems concepts including relational modelling, primary and foreign keys, normalisation, constraints, indexes, trigger-driven updates, materialized views, and integration between a database and application services. Market data is fetched from Yahoo Finance, written into PostgreSQL through ETL services, processed into risk and AI outputs, and displayed through a React dashboard.

Key achievements include a 14-table normalised schema, trigger-managed portfolio accounting, automatic alert logging, structured ETL logging, SQLAlchemy integration, and read surfaces that support Buy / Sell / Hold decision-making without compromising database consistency.

## 2. Introduction

Financial market applications require reliable storage of high-volume and time-sensitive data. Prices, volumes, predictions, trades, and alerts must remain consistent across multiple workflows. MarketMind was built to demonstrate how a properly designed relational database can support a complete full-stack product.

The system still includes AI, backend, and frontend layers, but for the Database Systems course the main focus is the PostgreSQL design and its integration with the rest of the application. The database is responsible for storing raw market data, maintaining user-specific records, supporting analysis, and enforcing important business rules.

### Project Objectives:

- Design a normalized PostgreSQL schema for a stock and crypto intelligence platform.

- Store Yahoo Finance asset metadata and OHLCV price history in structured relational tables.

- Use primary keys, foreign keys, constraints, indexes, triggers, and materialized views appropriately.

- Integrate the database with a FastAPI backend through SQLAlchemy.

- Support risk indicators, AI predictions, Buy / Sell / Hold signals, portfolios, trades, alerts, and optimisation results.

- Demonstrate reliable data flow from external source to database, backend APIs, and frontend dashboard.

## 3. Project Description

### Scope:

- User authentication and user-owned portfolios.

- Curated asset universe and asset metadata management.

- Yahoo Finance ETL for price-history ingestion.

- Risk indicator storage and retrieval.

- AI output storage for predictions, regimes, and market signals.

- Paper-trading through trade records and trigger-updated holdings.

- Price-threshold alerts and automatic alert logs.

- Portfolio optimisation result storage using JSONB asset weights.

### Technical Overview:

- Database: PostgreSQL with 14 base tables, 4 materialized views, 6 triggers, constraints, and indexes.

- Backend: FastAPI with SQLAlchemy 2.0 ORM models mapped to the existing SQL schema.

- Frontend: React + Vite using backend APIs to display database-backed information.

- Data Source: Yahoo Finance through yfinance for asset metadata and OHLCV history.

- Data Processing: Python services for ETL, risk indicators, prediction, signal generation, and portfolio optimisation.

- Deployment Model: Local full-stack demonstration environment.

MarketMind supports a complete database-backed workflow: data enters through ETL, is stored in normalized tables, is processed into derived outputs, and is retrieved through APIs for user-facing decision support.

## 4. Methodology

### Approach:

A database-first methodology was followed. The PostgreSQL schema was designed before the backend and frontend so that application logic could be built on a stable data model. The design process started with entity identification, relationship mapping, key selection, normalization, and constraint definition. After the schema was verified, backend models, API routes, ETL services, and frontend pages were implemented around it.

The build sequence was intentionally controlled: database verification came first, followed by FastAPI foundation, SQLAlchemy models, JWT authentication, asset APIs, yfinance ETL, risk indicators, AI outputs, portfolio/trade/alert APIs, React frontend, and final demo polish. This reduced integration risk because each layer was tested before the next one was introduced.

### Roles and Responsibilities:

- Ali Zeeshan: Database design, schema validation, backend coordination, and final report/presentation consolidation.

- Hasan Dad: Frontend integration, user-facing workflows, dashboard testing, and usability support.

- Agha Zaid Amir: AI pipeline integration, analytical logic, and data-processing support.

- All members contributed to debugging, verification, and final demo preparation.

## 5. Project Implementation

### Design and Structure:

The implementation follows a layered architecture. PostgreSQL stores all persistent data, FastAPI exposes the data through REST APIs, and React provides the user interface. The ETL and AI services are implemented as backend modules that read from and write to the database. This structure keeps the database as the central source of truth.

### Database Design:

The schema contains 14 base tables: USERS, ASSETS, PRICE_HISTORY, PORTFOLIOS, PORTFOLIO_HOLDINGS, TRADES, RISK_INDICATORS, AI_PREDICTIONS, MARKET_SIGNALS, HMM_STATES, PORTFOLIO_OPTIMISATION, ALERTS, ALERT_LOGS, and SCRAPER_LOGS. These tables separate user data, market data, transaction data, analytical outputs, and operational logs into clear relational structures.

ASSETS acts as the central reference table for all stocks and cryptocurrencies.

PRICE_HISTORY stores timestamped OHLCV market snapshots for each asset.

RISK_INDICATORS stores derived numeric features and interpretable labels.

AI_PREDICTIONS, MARKET_SIGNALS, and HMM_STATES store analytical outputs.

PORTFOLIOS, PORTFOLIO_HOLDINGS, and TRADES support paper-trading and performance tracking.

ALERTS and ALERT_LOGS separate alert rules from firing events.

SCRAPER_LOGS records ETL and pipeline execution status.

### Database Rules and Automation:

- Foreign keys enforce relationships such as user-to-portfolio, asset-to-price-history, portfolio-to-trade, and alert-to-alert-log.

- Triggers update portfolio holdings and cash after trades, preventing duplicate application-side accounting logic.

- A trigger validates SELL quantity before inserting invalid trades.

- A price-insert trigger checks active alert rules and inserts alert-log rows automatically.

- A prediction trigger/reconciliation flow supports filling actual prices when market data becomes available.

- Materialized views provide efficient latest-price, portfolio-performance, risk-summary, and signal-leaderboard read surfaces.

### Application Integration:

The backend uses SQLAlchemy models that mirror the executable SQL schema. API services do not generate tables and do not bypass database rules. For example, the trade service inserts into TRADES only, while the database handles holdings and cash updates. ETL services insert market data into ASSETS and PRICE_HISTORY, while risk and AI modules write their outputs into their respective tables. The frontend retrieves this data through backend routes and displays it in dashboards, tables, forms, and portfolio views.

### Challenges Faced:

- Keeping the executable SQL schema, ORM models, and backend services aligned.

- Avoiding duplicate business logic when database triggers already handled accounting and alerts.

- Managing timestamp consistency between Yahoo Finance data, PostgreSQL TIMESTAMPTZ fields, and prediction outputs.

- Preventing duplicate price-history rows during repeated scraping.

- Balancing database normalization with practical read performance and AI model access.

## 6. Results

MarketMind successfully demonstrates a working database-backed market intelligence workflow. The system can store assets, ingest price history, compute risk indicators, generate AI outputs, support paper-trading, update holdings through triggers, create alerts, and display all major data through a web dashboard.

### Testing and Validation:

- Database verification confirmed the expected 14 base tables, 4 materialized views, and 6 triggers.

- Foreign key relationships and table names were validated through SQL queries and ORM validation scripts.

- Backend health and database-connection checks confirmed PostgreSQL integration.

- ETL tests confirmed asset onboarding, price insertion, duplicate handling, and scraper logging.

- Risk and AI tests confirmed that analytical outputs are stored in the correct database tables.

- Trade tests confirmed that holdings and cash are updated by database triggers after inserting trades.

- Alert tests confirmed rule creation and trigger-based alert-log behavior.

- Frontend tests confirmed that database-backed data is visible through the user interface.

### Screenshots and Illustrations:

- Database schema and entity relationship view showing tables and relationships.

- Dashboard overview showing database-backed counts and workflow status.

- Assets and ETL pages showing asset onboarding and Yahoo Finance data ingestion.

- Risk Indicators page showing computed features stored in RISK_INDICATORS.

- Predictions, Signals, and Regimes pages showing AI outputs stored in database tables.

- Portfolio and Holdings views showing trigger-managed trading results.

- Alerts page showing alert rules and alert-log history.

## 7. Conclusion

MarketMind demonstrates the importance of database design in a full-stack analytical application. While the project includes AI and frontend components, its reliability depends on the PostgreSQL schema, relationships, constraints, triggers, and query structure. The database does more than store records: it enforces consistency, supports automated updates, and provides the foundation for analytics and user actions.

### Final Remarks:

- The project strengthened understanding of normalization, relationships, constraints, triggers, materialized views, and database-application integration.

- The database-first build process made the backend and frontend easier to structure and test.

Future enhancements may include scheduled database jobs, stronger indexing strategies, hosted deployment, and more advanced analytics while keeping the database as the central source of truth.

### Observed Outcome:

During demonstration, the user can select an asset, fetch market data, compute indicators, view Buy / Sell / Hold outputs, create a portfolio, place paper trades, and observe database-managed holdings and cash updates. This makes the final system a practical example of Database Systems concepts applied to a real-world inspired market intelligence platform.
