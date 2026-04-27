import { Menu } from "lucide-react";
import { useMemo, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import { getRouteMeta } from "./navigationConfig.js";
import Sidebar from "./Sidebar.jsx";


export default function AppLayout() {
  const location = useLocation();
  const { currentUser, isAuthenticated } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const routeMeta = useMemo(() => getRouteMeta(location.pathname), [location.pathname]);

  return (
    <div className="app-shell">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="app-content">
        <div className="app-topbar">
          <div className="app-topbar-main">
            <button
              type="button"
              className="ghost-button app-menu-button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation menu"
            >
              <Menu size={18} />
            </button>
            <div className="app-topbar-copy">
              <span className="app-topbar-kicker">{routeMeta.section}</span>
              <strong>{routeMeta.label}</strong>
              <p>{routeMeta.description}</p>
            </div>
          </div>

          <div className="app-topbar-meta">
            <div className="topbar-user">
              <span className="topbar-user-label">
                {isAuthenticated ? "Signed in as" : "Public browsing"}
              </span>
              <strong>{isAuthenticated ? (currentUser?.full_name || currentUser?.username) : "Guest"}</strong>
            </div>
          </div>
        </div>

        <div className="app-content-inner">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
