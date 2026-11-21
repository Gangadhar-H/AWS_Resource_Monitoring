import { statusLabel } from "../../config/statuses.js";

export default function StatusBadge({ status }) {
  return <span className={`badge ${status}`}>{statusLabel(status)}</span>;
}
