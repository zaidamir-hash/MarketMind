---
name: marketmind-demo-documentation
description: Use this skill when creating demo scripts, README files, setup instructions, feature explanations, onboarding guides, architecture summaries, and project presentation material.
---

# MarketMind Demo Documentation

## Purpose

This skill helps Codex generate clear, professional, and beginner-friendly documentation for the MarketMind project.

## Use This Skill For

- Writing README files
- Creating installation/setup instructions
- Explaining project architecture
- Writing feature descriptions
- Creating demo walkthroughs
- Preparing project presentation notes
- Writing API usage examples
- Creating database documentation
- Writing frontend usage instructions
- Creating deployment notes
- Writing troubleshooting guides
- Summarizing technical decisions

## Documentation Style Rules

- Use simple, clear language
- Assume the reader may be a beginner
- Use step-by-step instructions when possible
- Use markdown headings and bullet points
- Include code blocks for commands
- Keep sections short and readable
- Explain why something is done, not only how
- Avoid unnecessary jargon
- Prefer examples over abstract explanations
- Keep formatting consistent across files

## README Structure

When generating a README, prefer this order:

1. Project name
2. Short description
3. Features
4. Tech stack
5. Project structure
6. Installation
7. Environment variables
8. Running backend/frontend
9. Database setup
10. Example usage
11. Future improvements
12. License

## Demo Walkthrough Rules

When creating a demo script or presentation:

- Start with the project problem being solved
- Explain the target users
- Show the main workflow first
- Demonstrate the backend and frontend connection
- Highlight AI/analytics features
- Mention stock and crypto support
- Mention database usage
- End with future improvements and scalability

## Project-Specific Context

MarketMind is an AI-powered stock and crypto intelligence platform.

The project uses:

- FastAPI backend
- PostgreSQL database
- SQLAlchemy 2.0 ORM
- APScheduler background jobs
- yfinance data ingestion
- pandas/numpy for analytics
- scikit-learn for machine learning
- hmmlearn for market regime modeling
- pgmpy for Bayesian inference
- DEAP for portfolio optimization
- React + Vite frontend
- Recharts for visualizations

Project constraints to reflect in docs:

- frontend is JavaScript only, not TypeScript
- authentication is real JWT login
- local development only for now
- database uses the executable PostgreSQL SQL schema file
- do not document Alembic unless the user explicitly asks later
- do not document SENTIMENT_SCORES, news tables, sentiment tables, AI summaries tables, or Claude chat tables
- describe AI as simple and demo-friendly, not overengineered

## Important Documentation Rules

- Keep all setup instructions Windows-friendly unless otherwise specified
- Use the current project root or a generic placeholder path such as:
  `C:\path\to\MarketMind`
- Prefer PowerShell commands when giving terminal examples
- Keep instructions compatible with beginners
- Avoid assuming Docker unless explicitly requested
