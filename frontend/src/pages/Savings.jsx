import { useMemo } from "react";
import { useScan } from "../context/ScanContext.jsx";
import { STATUSES } from "../config/statuses.js";
import PageHeader from "../components/common/PageHeader.jsx";
import StatCards from "../components/common/StatCards.jsx";
import CostByTypeChart from "../components/common/CostByTypeChart.jsx";
import FindingsTable from "../components/common/FindingsTable.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import { money, percent } from "../utils/format.js";

export default function Savings() {
  const { summary, findings, loading, hasScan } = useScan();

  const groups = useMemo(() => {
    const g = {};
    findings.forEach((f) => {
      g[f.status] ||= { count: 0, savings: 0 };
      g[f.status].count += 1;
      g[f.status].savings += f.potential_savings;
    });
    return Object.entries(g).sort((a, b) => b[1].savings - a[1].savings);
  }, [findings]);

  if (loading) return <p className="muted">Loading…</p>;
  if (!hasScan) return (<><PageHeader title="Savings" /><EmptyState /></>);

  const total = summary.potential_monthly_savings;
  const spend = summary.estimated_monthly_spend || 0;

  return (
    <>
      <PageHeader title="Savings" subtitle="What you could save, and which actions are worth the most." />
      <StatCards cards={[
        { label: "Potential monthly savings", value: money(total), tone: "ok" },
        { label: "Potential yearly savings", value: money(total * 12), tone: "ok" },
        { label: "Share of estimated spend", value: spend ? percent((total / spend) * 100, 1) : "-", hint: spend ? `of ${money(spend)} per month` : "" },
        { label: "Opportunities", value: summary.flagged_count },
      ]} />

      <section className="grid-2">
        <CostByTypeChart byType={summary.by_type} title="Savings by resource type" />
        <div className="card">
          <h2>Recommended actions</h2>
          {groups.length === 0 ? <p className="muted">No actions needed.</p> : (
            <ul className="action-list">
              {groups.map(([status, g]) => (
                <li key={status}>
                  <div className="action-row">
                    <span>{STATUSES[status]?.action || status}</span>
                    <b className="good-text">{money(g.savings)}/mo</b>
                  </div>
                  <div className="bar"><div style={{ width: `${total ? (g.savings / total) * 100 : 0}%` }} /></div>
                  <span className="muted small">{g.count} resource{g.count > 1 ? "s" : ""}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <FindingsTable findings={findings} title="Top savings opportunities" limit={10} />
      <p className="muted small">Savings are estimates based on fixed price assumptions. Underutilized instances assume a 50% saving from downsizing.</p>
    </>
  );
}
