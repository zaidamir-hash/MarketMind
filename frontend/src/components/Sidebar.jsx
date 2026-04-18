import {
  Activity,
  AlertTriangle,
  BarChart3,
  BrainCircuit,
  Database,
  Gauge,
  LayoutDashboard,
  LineChart,
  LogIn,
  LogOut,
  PackageSearch,
  ShieldCheck,
  WalletCards,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";


const publicLinks = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/assets", label: "Assets", icon: PackageSearch },
  { to: "/risk-indicators", label: "Risk Indicators", icon: ShieldCheck },
  { to: "/predictions", label: "Predictions", icon: LineChart },
  { to: "/signals", label: "Signals", icon: BarChart3 },
  { to: "/regimes", label: "Regimes", icon: Gauge },
];

const protectedLinks = [
  { to: "/etl-tools", label: "ETL Tools", icon: Database },
  { to: "/portfolios", label: "Portfolios", icon: WalletCards },
  { to: "/alerts", label: "Alerts", icon: AlertTriangle },
];


function SidebarLink({ to, label, icon: Icon }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `sidebar-link ${isActive ? "is-active" : ""}`}
    >
      <Icon size={18} />
      <span>{label}</span>
    </NavLink>
  );
}


export default function Sidebar() {
  const { currentUser, isAuthenticated, logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">
          <BrainCircuit size={18} />
        </div>
        <div>
          <h1>MarketMind</h1>
          <p>Local demo dashboard</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-group">
          <span className="sidebar-group-title">Overview</span>
          {publicLinks.map((link) => (
            <SidebarLink key={link.to} {...link} />
          ))}
        </div>

        <div className="sidebar-group">
          <span className="sidebar-group-title">Workspace</span>
          {protectedLinks.map((link) => (
            <SidebarLink key={link.to} {...link} />
          ))}
        </div>
      </nav>

      <div className="sidebar-footer">
        {isAuthenticated ? (
          <>
            <div className="sidebar-user">
              <strong>{currentUser?.full_name || currentUser?.username}</strong>
              <span>{currentUser?.email}</span>
            </div>
            <button type="button" className="ghost-button full-width" onClick={logout}>
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </>
        ) : (
          <div className="sidebar-auth-links">
            <NavLink className="ghost-button full-width" to="/login">
              <LogIn size={16} />
              <span>Login</span>
            </NavLink>
            <NavLink className="primary-button full-width" to="/register">
              <Activity size={16} />
              <span>Register</span>
            </NavLink>
          </div>
        )}
      </div>
    </aside>
  );
}
