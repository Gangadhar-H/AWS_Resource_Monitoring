import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { errorMessage, getResource, scanResource } from "../services/api.js";
import { useScan } from "../context/ScanContext.jsx";
import { getType } from "../config/resourceTypes.js";
import { prettyKey, dateTime, money } from "../utils/format.js";
import PageHeader from "../components/common/PageHeader.jsx";
import StatusBadge from "../components/common/StatusBadge.jsx";
import StatCards from "../components/common/StatCards.jsx";
import ScanButton from "../components/common/ScanButton.jsx";
import UtilizationGauge from "../components/resources/UtilizationGauge.jsx";

const show = (v) => (v === null || v === undefined || v === "" ? "-" : String(v));

export default function ResourceDetail() {
  const { type, id } = useParams();
  const { reload } = useScan();
  const [item, setItem] = useState(null);
  const [scannedAt, setScannedAt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true); setNotFound(false); setResult(null); setError("");
    getResource(type, id)
      .then((r) => { if (!cancelled) { setItem(r.item); setScannedAt(r.scanned_at); } })
      .catch((e) => { if (!cancelled) (e.response?.status === 404 ? setNotFound(true) : setError(errorMessage(e))); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [type, id]);

  const rescan = useCallback(async () => {
    setScanning(true); setError(""); setResult(null);
    const before = item?.potential_savings ?? 0;
    try {
      const r = await scanResource(type, id);
      setItem(r.item); setScannedAt(r.scanned_at);
      setResult({ before, after: r.item.potential_savings, flagged: r.item.flagged });
      reload(); // refresh Home / Resources / Savings pages too
    } catch (e) {
      if (e.response?.status === 404) setNotFound(true); else setError(errorMessage(e));
    } finally {
      setScanning(false);
    }
  }, [type, id, item, reload]);

  const back = <Link className="link" to="/resources">← Back to resources</Link>;
  if (loading) return <p className="muted">Loading…</p>;
  if (notFound) {
    return (
      <div className="card empty">
        <h2>Resource not found</h2>
        <p className="muted">It is not in the latest scan, or it no longer exists in your account.</p>
        {back}
      </div>
    );
  }
  if (!item) return <>{error && <div className="alert">{error}</div>}{back}</>;

  const t = getType(item.resource_type);
  const known = new Set(t.detailFields.map(([k]) => k));
  const extras = Object.entries(item.details).filter(([k]) => !known.has(k));

  return (
    <>
      <p>{back}</p>
      <PageHeader
        title={item.name || item.resource_id}
        subtitle={`${t.label} · ${item.region}${item.name ? " · " + item.resource_id : ""}`}
        actions={<ScanButton onClick={rescan} scanning={scanning} label="Scan this resource" busyLabel="Scanning…" />}
      />
      {error && <div className="alert" role="alert">{error}</div>}
      {result && (
        <div className={`banner ${result.flagged ? "warn" : "ok"}`}>
          Scan complete. {result.flagged
            ? `This resource can save ${money(result.after)} per month.`
            : "No savings opportunity found for this resource."}
          {result.flagged && result.before !== result.after && ` (was ${money(result.before)})`}
        </div>
      )}

      <StatCards cards={[
        { label: "Status", value: <StatusBadge status={item.status} />, hint: item.flagged ? "Needs attention" : "All good" },
        { label: "Monthly cost", value: money(item.monthly_cost) },
        { label: "Potential monthly savings", value: money(item.potential_savings), tone: item.potential_savings > 0 ? "ok" : "" },
        { label: "Potential yearly savings", value: money(item.potential_savings * 12), tone: item.potential_savings > 0 ? "ok" : "" },
      ]} />

      <section className="grid-2">
        <div className="card">
          <h2>Finding</h2>
          <p><b>{item.reason}</b></p>
          <h3>Recommendation</h3>
          <p>{item.recommendation}</p>
          <h3>How this was calculated</h3>
          <p className="muted small">Cost: {item.cost_basis}</p>
          {item.savings_basis && <p className="muted small">Savings: {item.savings_basis}</p>}
        </div>
        <div className="card">
          <h2>Utilization</h2>
          {item.metrics ? <UtilizationGauge metrics={item.metrics} /> : <p className="muted">Utilization metrics are not collected for this resource type.</p>}
        </div>
      </section>

      <section className="card">
        <h2>Details</h2>
        <dl className="detail-list">
          <div><dt>Resource ID</dt><dd className="mono">{item.resource_id}</dd></div>
          <div><dt>Region</dt><dd>{show(item.region)}</dd></div>
          {t.detailFields.map(([key, label, fmt]) => (
            <div key={key}><dt>{label}</dt><dd>{show(fmt ? fmt(item.details[key]) : item.details[key])}</dd></div>
          ))}
          {extras.map(([k, v]) => (
            <div key={k}><dt>{prettyKey(k)}</dt><dd>{show(Array.isArray(v) ? v.join(", ") : typeof v === "object" ? JSON.stringify(v) : v)}</dd></div>
          ))}
          <div><dt>Last scanned</dt><dd>{dateTime(scannedAt)}</dd></div>
        </dl>
      </section>
    </>
  );
}
