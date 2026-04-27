import {
  Activity,
  BrainCircuit,
  Lock,
  LogIn,
  LogOut,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import { protectedLinks, publicLinks } from "./navigationConfig.js";

function SidebarLink({ to, label, icon: Icon, requiresAuth = false, isAuthenticated, onClick }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `sidebar-link ${isActive ? "is-active" : ""} ${requiresAuth ? "is-protected" : ""}`}
      onClick={onClick}
    >
      <div className="sidebar-link-content">
        <Icon size={18} />
        <span>{label}</span>
      </div>
      {requiresAuth && !isAuthenticated ? (
        <span className="sidebar-link-badge">
          <Lock size={12} />
          Login
        </span>
      ) : null}
    </NavLink>
  );
}


export default function Sidebar({ isOpen = false, onClose }) {
  const { currentUser, isAuthenticated, logout } = useAuth();

  return (
    <>
      <button
        type="button"
        className={`sidebar-backdrop ${isOpen ? "is-visible" : ""}`}
        aria-label="Close navigation menu"
        onClick={onClose}
      />
      <aside className={`sidebar ${isOpen ? "is-open" : ""}`}>
        <div className="sidebar-topbar">
          <div className="sidebar-brand">
            <div className="brand-mark">
              <BrainCircuit size={18} />
            </div>
            <div>
              <h1>MarketMind</h1>
              <p>Market intelligence platform</p>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-group">
            <span className="sidebar-group-title">Overview</span>
            {publicLinks.map((link) => (
              <SidebarLink
                key={link.to}
                {...link}
                isAuthenticated={isAuthenticated}
                onClick={onClose}
              />
            ))}
          </div>

          <div className="sidebar-group">
            <span className="sidebar-group-title">Workspace</span>
            {protectedLinks.map((link) => (
              <SidebarLink
                key={link.to}
                {...link}
                isAuthenticated={isAuthenticated}
                onClick={onClose}
              />
            ))}
          </div>
        </nav>

        <div className="sidebar-footer">
          {isAuthenticated ? (
            <>
              <div className="sidebar-user">
                <span className="sidebar-user-label">Authenticated workspace</span>
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
              <div className="sidebar-user sidebar-user-guest">
                <span className="sidebar-user-label">Guest mode</span>
                <strong>Public analytics available</strong>
                <span>Login to access ETL, portfolios, trades, and alerts.</span>
              </div>
              <NavLink className="ghost-button full-width" to="/login" onClick={onClose}>
                <LogIn size={16} />
                <span>Login</span>
              </NavLink>
              <NavLink className="primary-button full-width" to="/register" onClick={onClose}>
                <Activity size={16} />
                <span>Register</span>
              </NavLink>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
