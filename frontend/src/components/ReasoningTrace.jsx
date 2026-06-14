import { useState } from "react";

function StepBody({ step }) {
  const { step: num, output } = step;

  // Step 1: Ingest & Normalize
  if (num === 1) {
    const c = output.ontology_concepts;
    return (
      <div className="mono" style={{ fontSize: 12.5, lineHeight: 1.8 }}>
        <div>diagnosis: {c.diagnosis}</div>
        <div>age_band: {c.age_band}</div>
        <div>total_lots: {c.total_lots}</div>
        <div>current_drug_class: "{c.current_drug_class}"</div>
        <div>biomarker_trend_direction: <strong>{c.biomarker_trend_direction}</strong></div>
        <div>biomarker_latest_value: {c.biomarker_latest_value} umol/L</div>
        <div>biomarker_min_value: {c.biomarker_min_value} umol/L</div>
        <div>gap_in_therapy_days: {c.gap_in_therapy_days}</div>
        <div>rapid_switch_count: {c.rapid_switch_count}</div>
      </div>
    );
  }

  // Step 2: Pattern Detection
  if (num === 2) {
    if (output.signals_detected === 0) {
      return <div className="audit-clean">No risk signals detected by current rule set.</div>;
    }
    return (
      <div>
        {output.signals.map((s) => (
          <div className="signal-row" key={s.signal_id}>
            <span className={`severity-tag severity-${s.severity}`}>{s.severity}</span>
            <div>
              <div style={{ fontWeight: 500 }}>{s.name}</div>
              <div style={{ color: "var(--ink-soft)", marginTop: 2 }}>{s.description}</div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Step 3: Evidence Retrieval
  if (num === 3) {
    if (!output.evidence || output.evidence.length === 0) {
      return <div className="audit-clean">No signals to retrieve evidence for.</div>;
    }
    return (
      <div>
        {output.evidence.map((e) => (
          <div key={e.signal_id} style={{ marginBottom: 10 }}>
            <div style={{ fontWeight: 500, marginBottom: 4 }}>
              {e.signal_id}
            </div>
            {e.kb_matches.length === 0 && (
              <div className="audit-clean" style={{ paddingLeft: 8 }}>no KB match found</div>
            )}
            {e.kb_matches.map((m) => (
              <div className="kb-match-row" key={m.kb_id}>
                <span>
                  <span className="kb-id-chip">{m.kb_id}</span> {m.title}
                </span>
                <span className="mono" style={{ color: "var(--ink-soft)" }}>
                  relevance {m.relevance_score}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  }

  // Step 4: Synthesis
  if (num === 4) {
    const brief = output.brief_preview;
    return (
      <div style={{ fontSize: 13, color: "var(--ink-soft)" }}>
        Draft brief generated with {brief.sections.length} sections —
        every statement is tagged with a citation (a knowledge-base ID,
        signal ID, or "[data]") for traceability. Passed to Step 5 for
        the safety pass before being shown below.
      </div>
    );
  }

  // Step 5: Safety Check
  if (num === 5) {
    return (
      <div className="mono" style={{ fontSize: 12.5, lineHeight: 1.8 }}>
        <div>sections_checked: {output.checked_sections}</div>
        <div>
          violations_found: {output.violations_found}{" "}
          {output.violations_found === 0 && (
            <span className="audit-clean">— clean</span>
          )}
        </div>
        <div>requires_human_review: <strong>{String(output.requires_human_review)}</strong></div>
        <div>disclaimer_present: {String(output.disclaimer_present)}</div>
        {output.audit_log.length > 0 && (
          <div style={{ marginTop: 8 }}>
            {output.audit_log.map((a, i) => (
              <div key={i} style={{ color: "var(--red)" }}>
                [{a.section}] stripped — pattern "{a.violation_pattern}"
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return null;
}

export default function ReasoningTrace({ steps }) {
  const [openSteps, setOpenSteps] = useState(() => new Set(steps.map((s) => s.step)));

  function toggle(num) {
    setOpenSteps((prev) => {
      const next = new Set(prev);
      if (next.has(num)) next.delete(num);
      else next.add(num);
      return next;
    });
  }

  return (
    <div>
      {steps.map((step, i) => {
        const isOpen = openSteps.has(step.step);
        return (
          <div
            className="trace-step"
            key={step.step}
            style={{ animationDelay: `${i * 0.12}s` }}
          >
            <div className="trace-step-header" onClick={() => toggle(step.step)}>
              <div className="trace-step-num">{step.step}</div>
              <div className="trace-step-title">
                <div className="name">{step.name}</div>
                <div className="desc">{step.description}</div>
              </div>
              <div className="trace-step-toggle">{isOpen ? "hide" : "show"}</div>
            </div>
            {isOpen && (
              <div className="trace-step-body">
                <StepBody step={step} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
