// Splits trailing citation tags like "[KB-001], [KB-013]" or "[data]" or
// "[SIG-RAPID-SWITCH]" off the end of a bullet string and renders them
// as styled chips.
function renderBulletWithCitations(text) {
  const match = text.match(/^(.*?)((\s*\[[A-Za-z0-9\-_, \[\]]+\])+)\s*$/);
  if (!match) return <>{text}</>;

  const body = match[1].trim();
  const citationBlock = match[2];
  const citations = citationBlock.match(/\[[A-Za-z0-9\-_]+\]/g) || [];

  return (
    <>
      {body}
      {citations.map((c, i) => (
        <span className="citation" key={i}>
          {c.replace(/[[\]]/g, "")}
        </span>
      ))}
    </>
  );
}

export default function BriefView({ brief }) {
  return (
    <div className="card brief-card">
      <h2>Decision support brief</h2>
      <p className="brief-summary">{renderBulletWithCitations(brief.summary)}</p>

      {brief.sections.map((section) => (
        <div className="brief-section" key={section.heading}>
          <h4>{section.heading}</h4>
          {section.bullets.map((b, i) => (
            <div className="brief-bullet" key={i}>
              {renderBulletWithCitations(b)}
            </div>
          ))}
        </div>
      ))}

      <div className="review-banner">
        ⚠ Requires human review — {brief.disclaimer}
      </div>
    </div>
  );
}
