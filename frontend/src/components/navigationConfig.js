import {
  AlertTriangle,
  BarChart3,
  Database,
  Gauge,
  LayoutDashboard,
  LineChart,
  PackageSearch,
  ShieldCheck,
  WalletCards,
} from "lucide-react";


export const publicLinks = [
  {
    to: "/",
    label: "Dashboard",
    icon: LayoutDashboard,
    description: "System overview and recent activity.",
  },
  {
    to: "/assets",
    label: "Assets",
    icon: PackageSearch,
    description: "Browse the tracked asset universe.",
  },
  {
    to: "/risk-indicators",
    label: "Risk Indicators",
    icon: ShieldCheck,
    description: "Latest deterministic and Bayesian-style risk outputs.",
  },
  {
    to: "/predictions",
    label: "Predictions",
    icon: LineChart,
    description: "Latest linear-model price predictions.",
  },
  {
    to: "/signals",
    label: "Signals",
    icon: BarChart3,
    description: "Rule-based BUY, HOLD, and SELL outputs.",
  },
  {
    to: "/regimes",
    label: "Regimes",
    icon: Gauge,
    description: "Recent market regime classifications.",
  },
];

export const protectedLinks = [
  {
    to: "/etl-tools",
    label: "ETL Tools",
    icon: Database,
    description: "Manual yfinance onboarding and price jobs.",
    requiresAuth: true,
  },
  {
    to: "/portfolios",
    label: "Portfolios",
    icon: WalletCards,
    description: "Create portfolios, trade, and optimize allocations.",
    requiresAuth: true,
  },
  {
    to: "/alerts",
    label: "Alerts",
    icon: AlertTriangle,
    description: "Manage user alerts and trigger logs.",
    requiresAuth: true,
  },
];

export const allNavigationLinks = [...publicLinks, ...protectedLinks];


export function getRouteMeta(pathname) {
  if (!pathname || pathname === "/" || pathname === "/dashboard") {
    return {
      label: "Dashboard",
      section: "System overview",
      description: "High-level snapshot of the backend state and recent activity.",
    };
  }

  if (pathname.startsWith("/portfolios/")) {
    return {
      label: "Portfolio Detail",
      section: "Portfolio workspace",
      description: "Trade, inspect holdings, and review optimization history.",
    };
  }

  const matched = allNavigationLinks.find((link) => link.to === pathname);
  if (matched) {
    return {
      label: matched.label,
      section: matched.requiresAuth ? "Protected workspace" : "Public analytics",
      description: matched.description,
    };
  }

  return {
    label: "MarketMind",
    section: "Application",
    description: "Stock and crypto intelligence dashboard.",
  };
}
