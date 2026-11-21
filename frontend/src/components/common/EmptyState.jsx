import { useScan } from "../../context/ScanContext.jsx";
import ScanButton from "./ScanButton.jsx";

export default function EmptyState({ title = "No scan yet", text }) {
  const { scan, scanning } = useScan();
  return (
    <div className="card empty">
      <h2>{title}</h2>
      <p className="muted">
        {text || "Run your first read-only scan to look for unattached volumes, unused IP addresses and underutilized instances."}
      </p>
      <ScanButton onClick={scan} scanning={scanning} />
    </div>
  );
}
