// cards: [{ label, value, hint, tone: "ok" | "warn" }]
export default function StatCards({ cards }) {
  return (
    <section className="cards">
      {cards.map((c) => (
        <div key={c.label} className={`card stat ${c.tone || ""}`}>
          <span className="stat-label">{c.label}</span>
          <span className="stat-value">{c.value}</span>
          <span className="stat-hint">{c.hint || " "}</span>
        </div>
      ))}
    </section>
  );
}
