function formatDate(dateStr) {
  if (!dateStr) return "ongoing";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { year: "numeric", month: "short" });
}

const SWITCH_REASON_LABELS = {
  inadequate_response: "inadequate response",
  tolerability_issue: "tolerability issue",
  adherence_decline: "adherence decline",
  guideline_update: "guideline update",
};

export default function LotTimeline({ lines }) {
  return (
    <div className="card lot-card">
      <h3>Lines of therapy</h3>
      <div className="lot-timeline">
        {lines.map((lot) => (
          <div className="lot-item" key={lot.lot}>
            <div className="lot-badge">LOT {lot.lot}</div>
            <div>
              <div className="lot-name">{lot.drug}</div>
              <div className="lot-meta">
                {formatDate(lot.start_date)} – {formatDate(lot.end_date)}
                {lot.switch_reason &&
                  ` · switched: ${SWITCH_REASON_LABELS[lot.switch_reason] || lot.switch_reason}`}
              </div>
            </div>
            <div className="lot-adherence">{lot.adherence_pct}% adherence</div>
          </div>
        ))}
      </div>
    </div>
  );
}
