import { percent } from "../../utils/format.js";

// CPU bar with a marker at the "idle" threshold.
export default function UtilizationGauge({ metrics }) {
  const { avg_cpu_percent: avg, cpu_threshold_percent: thr, lookback_days: days, note } = metrics;
  if (avg === null || avg === undefined) {
    return <p className="muted">{note || "No utilization data available."}</p>;
  }
  const low = avg < thr;
  return (
    <div>
      <div className="gauge-label">
        <span>Average CPU over {days} days</span>
        <b className={low ? "warn-text" : "good-text"}>{percent(avg, 1)}</b>
      </div>
      <div className="gauge" role="img" aria-label={`Average CPU ${avg} percent`}>
        <div className={`gauge-fill ${low ? "low" : "ok"}`} style={{ width: `${Math.min(avg, 100)}%` }} />
        <div className="gauge-marker" style={{ left: `${thr}%` }} title={`Idle threshold ${thr}%`} />
      </div>
      <p className="muted small">
        Marker = idle threshold ({thr}%). {low ? "Usage is below the threshold, so this instance is underutilized." : "Usage is above the threshold."}
      </p>
    </div>
  );
}
