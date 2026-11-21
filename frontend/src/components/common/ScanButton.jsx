export default function ScanButton({ onClick, scanning, label = "Scan Now", busyLabel = "Scanning…", variant = "" }) {
  return (
    <button className={`btn ${variant}`} onClick={onClick} disabled={scanning}>
      {scanning ? (<><span className="spinner" aria-hidden="true" /> {busyLabel}</>) : label}
    </button>
  );
}
