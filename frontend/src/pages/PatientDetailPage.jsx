import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getPatient, analyzePatient } from "../api/client";
import DisclaimerBanner from "../components/DisclaimerBanner";
import LabTrendChart from "../components/LabTrendChart";
import LotTimeline from "../components/LotTimeline";
import ReasoningTrace from "../components/ReasoningTrace";
import BriefView from "../components/BriefView";

export default function PatientDetailPage() {
  const { patientId } = useParams();
  const [patient, setPatient] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setPatient(null);
    setAnalysis(null);
    getPatient(patientId).then(setPatient).catch((e) => setError(e.message));
  }, [patientId]);

  async function handleAnalyze() {
    setAnalyzing(true);
    setError(null);
    try {
      const result = await analyzePatient(patientId);
      setAnalysis(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div>
      <DisclaimerBanner />
      <Link to="/" className="back-link">&larr; Back to cohort</Link>

      {!patient && !error && (
        <div className="loading-state">
          <div className="spinner" />
          Loading patient journey...
        </div>
      )}

      {error && <div className="empty-state">{error}</div>}

      {patient && (
        <>
          <div className="detail-header">
            <div>
              <h1>{patient.patient_id}</h1>
              <div className="subtitle">
                {patient.diagnosis} · age band {patient.age_band} · sex {patient.sex} ·
                diagnosed {patient.diagnosis_date.slice(0, 7)}
              </div>
            </div>
            <button
              className="btn-analyze"
              onClick={handleAnalyze}
              disabled={analyzing}
            >
              {analyzing ? "Analyzing..." : "Run PharmaSense analysis"}
            </button>
          </div>

          <LabTrendChart labTrend={patient.lab_trend} />
          <LotTimeline lines={patient.lines_of_therapy} />

          {analyzing && (
            <div className="loading-state">
              <div className="spinner" />
              Running 5-step reasoning pipeline...
            </div>
          )}

          {analysis && (
            <>
              <h3 style={{ margin: "28px 0 14px", fontSize: 14, textTransform: "uppercase",
                            letterSpacing: "0.06em", color: "var(--ink-soft)", fontFamily: "Inter, sans-serif" }}>
                Agent reasoning trace
              </h3>
              <ReasoningTrace steps={analysis.steps} />
              <BriefView brief={analysis.brief} />
            </>
          )}
        </>
      )}
    </div>
  );
}
