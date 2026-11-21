import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { useScan } from "../context/ScanContext.jsx";
import { RESOURCE_TYPES, getType } from "../config/resourceTypes.js";
import { STATUSES } from "../config/statuses.js";
import PageHeader from "../components/common/PageHeader.jsx";
import EmptyState from "../components/common/EmptyState.jsx";
import ResourceCard from "../components/resources/ResourceCard.jsx";

// Filters live in the URL (?type=ebs&status=unused&q=text&sort=savings) so views can be shared / bookmarked.
export default function Resources() {
  const { inventory, loading, hasScan } = useScan();
  const [params, setParams] = useSearchParams();
  const type = params.get("type") || "all";
  const status = params.get("status") || "all";
  const q = params.get("q") || "";
  const sort = params.get("sort") || "savings";

  const set = (key, value, empty) => {
    const next = new URLSearchParams(params);
    if (!value || value === empty) next.delete(key); else next.set(key, value);
    setParams(next, { replace: true });
  };

  const counts = useMemo(() => {
    const c = {};
    inventory.forEach((i) => { c[i.resource_type] = (c[i.resource_type] || 0) + 1; });
    return c;
  }, [inventory]);

  const items = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const list = inventory.filter((i) => {
      if (type !== "all" && i.resource_type !== type) return false;
      if (status === "flagged" ? !i.flagged : status !== "all" && i.status !== status) return false;
      if (!needle) return true;
      return [i.resource_id, i.name, i.details.public_ip].some((v) => (v || "").toLowerCase().includes(needle));
    });
    const by = {
      savings: (a, b) => b.potential_savings - a.potential_savings,
      cost: (a, b) => b.monthly_cost - a.monthly_cost,
      name: (a, b) => (a.name || a.resource_id).localeCompare(b.name || b.resource_id),
    }[sort];
    return [...list].sort(by);
  }, [inventory, type, status, q, sort]);

  if (loading) return <p className="muted">Loading…</p>;
  if (!hasScan || inventory.length === 0) {
    return (
      <>
        <PageHeader title="Resources" subtitle="Every resource found in your cloud account." />
        <EmptyState text={hasScan ? "This scan has no resource inventory. Run a new scan to build it." : undefined} />
      </>
    );
  }

  const typeKeys = [...new Set([...Object.keys(RESOURCE_TYPES), ...Object.keys(counts)])].filter((t) => counts[t]);

  return (
    <>
      <PageHeader title="Resources" subtitle={`${inventory.length} resources found. Click one to see its details and check its savings.`} />

      <div className="chips" role="tablist" aria-label="Resource type">
        <button className={`chip ${type === "all" ? "active" : ""}`} onClick={() => set("type", "all", "all")}>All <span>{inventory.length}</span></button>
        {typeKeys.map((t) => (
          <button key={t} className={`chip ${type === t ? "active" : ""}`} onClick={() => set("type", t, "all")}>
            {getType(t).plural} <span>{counts[t]}</span>
          </button>
        ))}
      </div>

      <div className="toolbar">
        <input type="search" placeholder="Search by ID, name or IP…" value={q} onChange={(e) => set("q", e.target.value)} aria-label="Search resources" />
        <select value={status} onChange={(e) => set("status", e.target.value, "all")} aria-label="Filter by status">
          <option value="all">All statuses</option>
          <option value="flagged">Flagged only</option>
          {Object.entries(STATUSES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <select value={sort} onChange={(e) => set("sort", e.target.value, "savings")} aria-label="Sort">
          <option value="savings">Sort: highest savings</option>
          <option value="cost">Sort: highest cost</option>
          <option value="name">Sort: name</option>
        </select>
      </div>

      {items.length === 0 ? (
        <p className="muted">No resources match these filters.</p>
      ) : (
        <div className="resource-grid">
          {items.map((i) => <ResourceCard key={`${i.resource_type}-${i.resource_id}`} item={i} />)}
        </div>
      )}
    </>
  );
}
