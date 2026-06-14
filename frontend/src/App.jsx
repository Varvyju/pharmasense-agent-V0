import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import CohortPage from "./pages/CohortPage";
import PatientDetailPage from "./pages/PatientDetailPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <div className="topbar">
          <Link to="/" style={{ textDecoration: "none" }}>
            <span className="brand display">
              PharmaSense Agent
              <small>Reasoning Agents</small>
            </span>
          </Link>
          <nav>Microsoft Agents League · Foundry IQ + Fabric IQ mapping</nav>
        </div>

        <Routes>
          <Route path="/" element={<CohortPage />} />
          <Route path="/patients/:patientId" element={<PatientDetailPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
