import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Alerts from "./pages/Alerts.jsx";
import Assets from "./pages/Assets.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import EtlTools from "./pages/EtlTools.jsx";
import Login from "./pages/Login.jsx";
import NotFound from "./pages/NotFound.jsx";
import PortfolioDetail from "./pages/PortfolioDetail.jsx";
import Portfolios from "./pages/Portfolios.jsx";
import Predictions from "./pages/Predictions.jsx";
import Regimes from "./pages/Regimes.jsx";
import Register from "./pages/Register.jsx";
import RiskIndicators from "./pages/RiskIndicators.jsx";
import Signals from "./pages/Signals.jsx";


export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/risk-indicators" element={<RiskIndicators />} />
        <Route path="/predictions" element={<Predictions />} />
        <Route path="/signals" element={<Signals />} />
        <Route path="/regimes" element={<Regimes />} />

        <Route
          path="/etl-tools"
          element={(
            <ProtectedRoute>
              <EtlTools />
            </ProtectedRoute>
          )}
        />
        <Route
          path="/portfolios"
          element={(
            <ProtectedRoute>
              <Portfolios />
            </ProtectedRoute>
          )}
        />
        <Route
          path="/portfolios/:portfolioId"
          element={(
            <ProtectedRoute>
              <PortfolioDetail />
            </ProtectedRoute>
          )}
        />
        <Route
          path="/alerts"
          element={(
            <ProtectedRoute>
              <Alerts />
            </ProtectedRoute>
          )}
        />

        <Route path="/dashboard" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
