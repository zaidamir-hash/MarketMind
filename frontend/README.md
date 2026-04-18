# Frontend

This folder contains the React + Vite JavaScript frontend for MarketMind.

## Install

1. `cd frontend`
2. `npm.cmd install`

## Run

1. Make sure the FastAPI backend is already running on `http://127.0.0.1:8000` or set `VITE_API_BASE_URL` in `.env`
2. `cd frontend`
3. `npm.cmd run dev -- --host 127.0.0.1 --port 5173`

Optional local environment file:

- copy `.env.example` to `.env`
- set `VITE_API_BASE_URL=http://127.0.0.1:8000`

PowerShell note:

- If `npm` is blocked by execution policy on your machine, use `npm.cmd` instead.

## Authentication

- login uses the backend `POST /auth/login`
- the access token is stored in `localStorage`
- authenticated actions such as ETL, portfolios, trades, alerts, and optimization require the backend token

## Notes

- JavaScript only
- no TypeScript
- API access is organized under `src/services/`
- the backend must be running first for the dashboard and data pages to work
