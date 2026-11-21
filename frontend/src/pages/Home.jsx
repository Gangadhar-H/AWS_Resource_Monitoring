import { Link } from "react-router-dom";
import { useScan } from "../context/ScanContext.jsx";
import PageHeader from "../components/common/PageHeader.jsx";
import StatCards from "../components/common/StatCards.jsx";
import CostByTypeChart from "../components/common/CostByTypeChart.jsx";
import FindingsTable from "../components/common/FindingsTable.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import { money } from "../utils/format.js";

export default function Home() {
  const { summary, findings, loading, hasScan } = useScan();
  if (loading) return <p className="muted">Loading…</p>;

  return (
    <>
      <PageHeader title="Overview" subtitle="Find idle cloud resources and see what they cost you." />
      {!hasScan ? (
        <EmptyState />
      ) : (
        <>
          <StatCards
            cards={[
              { label: "Resources scanned", value: summary.total_resources_scanned,
                hint: Object.entries(summary.scanned_by_type).map(([k, v]) => `${v} ${k.toUpperCase()}`).join(" · ") },
              { label: "Flagged as wasteful", value: summary.flagged_count, tone: summary.flagged_count ? "warn" : "ok",
                hint: Object.entries(summary.by_status).map(([k, v]) => `${v} ${k}`).join(" · ") },
              { label: "Estimated monthly waste", value: money(summary.estimated_monthly_waste),
                hint: `of ${money(summary.estimated_monthly_spend ?? 0)} total spend` },
              { label: "Potential monthly savings", value: money(summary.potential_monthly_savings), tone: "ok",
                hint: `${money(summary.potential_monthly_savings * 12)} per year` },
            ]}
          />
          <section className="grid-2">
            <CostByTypeChart byType={summary.by_type} />
            <div className="card note">
              <h2>Explore</h2>
              <ul>
                <li><Link className="link" to="/resources">Resources</Link>: every resource in the account, with a detail page for each.</li>
                <li><Link className="link" to="/savings">Savings</Link>: ranked opportunities grouped by action.</li>
                <li><Link className="link" to="/about">About</Link>: detection rules and pricing assumptions.</li>
              </ul>
              <p className="muted small">This tool only recommends. It never changes your account.</p>
            </div>
          </section>
          <FindingsTable findings={findings} title="Top flagged resources" limit={5} />
          <p className="right"><Link className="link" to="/resources?status=flagged">View all resources →</Link></p>
        </>
      )}
    </>
  );
}
