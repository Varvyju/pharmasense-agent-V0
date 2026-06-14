import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getPatients } from "../api/client";
import DisclaimerBanner from "../components/DisclaimerBanner";

export default function CohortPage() {
  const [patients, setPatients] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getPatients().then(setPatients).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <DisclaimerBanner />

      <p style={{ color: "var(--ink-soft)", fontSize: 14, marginBottom: 18 }}>
        Select a synthetic patient to view their treatment journey and run
        the PharmaSense reasoning agent.
      </p>

      {error && (
        <div className="empty-state">Could not load cohort: {error}</div>
      )}

      {!patients && !error && (
        <div className="loading-state">
          <div className="spinner" />
          Loading synthetic cohort...
        </div>
      )}

      {patients && (
        <div className="cohort-grid">
          {patients.map((p) => (
            <div
              key={p.patient_id}
              className="patient-card"
              onClick={() => navigate(`/patients/${p.patient_id}`)}
            >
              <div className="pid">{p.patient_id}</div>
              <h3>{p.diagnosis}</h3>
              <div className="meta">
                <span>Age band: {p.age_band}</span>
                <span>Lines of therapy: {p.num_lots}</span>
                <span>Current: {p.current_drug}</span>
              </div>
              <div className="flag-row">
                {p.rapid_switch_count > 0 && (
                  <span className="flag rapid">
                    {p.rapid_switch_count} rapid switch
                  </span>
                )}
                {p.gap_in_therapy_days > 30 && (
                  <span className="flag gap">
                    {p.gap_in_therapy_days}d gap
                  </span>
                )}
                {p.rapid_switch_count === 0 && p.gap_in_therapy_days <= 30 && (
                  <span className="flag clean">no flags</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
