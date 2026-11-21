import { Link } from "react-router-dom";
import { getType } from "../../config/resourceTypes.js";
import { money } from "../../utils/format.js";
import StatusBadge from "../common/StatusBadge.jsx";

export default function ResourceCard({ item }) {
  const t = getType(item.resource_type);
  return (
    <Link to={`/resources/${item.resource_type}/${item.resource_id}`} className="card resource-card">
      <div className="rc-top">
        <span className="type-chip" style={{ background: t.color }}>{t.short}</span>
        <StatusBadge status={item.status} />
      </div>
      <div className="rc-title">{item.name || item.resource_id}</div>
      {item.name && <div className="mono muted small rc-id">{item.resource_id}</div>}
      <dl className="rc-facts">
        {t.cardFacts(item).map(([k, v]) => (
          <div key={k}><dt>{k}</dt><dd>{v ?? "-"}</dd></div>
        ))}
      </dl>
      <div className="rc-bottom">
        <div><span className="muted small">Monthly cost</span><div className="rc-money">{money(item.monthly_cost)}</div></div>
        {item.potential_savings > 0 && (
          <div className="right"><span className="muted small">Can save</span><div className="rc-money good">{money(item.potential_savings)}</div></div>
        )}
      </div>
    </Link>
  );
}
