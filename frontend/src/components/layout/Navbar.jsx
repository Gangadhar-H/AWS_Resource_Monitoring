import { NavLink } from "react-router-dom";
import { NAV_ITEMS } from "../../config/navigation.js";
import { useScan } from "../../context/ScanContext.jsx";
import { dateTime } from "../../utils/format.js";
import ScanButton from "../common/ScanButton.jsx";

export default function Navbar() {
  const { summaryData, hasScan, scan, scanning } = useScan();
  return (
    <header className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="brand">
          <span className="brand-mark" aria-hidden="true">$</span>
          <span>Cloud Cost Monitor</span>
        </NavLink>

        <nav className="nav-links" aria-label="Main">
          {NAV_ITEMS.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="nav-right">
          {hasScan && (
            <span className="muted small nav-meta">
              {summaryData.provider?.toUpperCase()} · {summaryData.region} · {dateTime(summaryData.scanned_at)}
            </span>
          )}
          <ScanButton onClick={scan} scanning={scanning} />
        </div>
      </div>
    </header>
  );
}
