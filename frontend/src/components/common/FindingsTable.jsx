import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getType } from "../../config/resourceTypes.js";
import { money } from "../../utils/format.js";
import StatusBadge from "./StatusBadge.jsx";

// Table of flagged resources. Each row links to the resource's detail page.
export default function FindingsTable({ findings, title = "Flagged resources", limit }) {
  const [type, setType] = useState("all");
  const [sortDesc, setSortDesc] = useState(true);

  const rows = useMemo(() => {
    const filtered = type === "all" ? findings : findings.filter((f) => f.resource_type === type);
    const sorted = [...filtered].sort((a, b) => (sortDesc ? b.potential_savings - a.potential_savings : a.potential_savings - b.potential_savings));
    return limit ? sorted.slice(0, limit) : sorted;
  }, [findings, type, sortDesc, limit]);

  const typesPresent = [...new Set(findings.map((f) => f.resource_type))];

  return (
    <section className="card">
      <div className="table-head">
        <h2>{title}</h2>
        <select value={type} onChange={(e) => setType(e.target.value)} aria-label="Filter by type">
          <option value="all">All types</option>
          {typesPresent.map((t) => <option key={t} value={t}>{getType(t).plural}</option>)}
        </select>
      </div>
      {rows.length === 0 ? (
        <p className="muted">No flagged resources.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Type</th><th>Resource</th><th>Status</th><th>Reason</th>
                <th className="num">Monthly cost</th>
                <th className="num sortable" onClick={() => setSortDesc((s) => !s)}>Savings {sortDesc ? "▼" : "▲"}</th>
                <th>Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((f) => (
                <tr key={`${f.resource_type}-${f.resource_id}`}>
                  <td>{getType(f.resource_type).label}</td>
                  <td>
                    <Link className="mono link" to={`/resources/${f.resource_type}/${f.resource_id}`}>{f.resource_id}</Link>
                    {f.name && <div className="muted small">{f.name}</div>}
                  </td>
                  <td><StatusBadge status={f.status} /></td>
                  <td>{f.reason}</td>
                  <td className="num">{money(f.monthly_cost)}</td>
                  <td className="num strong">{money(f.potential_savings)}</td>
                  <td className="small">{f.recommendation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
