import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { errorMessage, getInventory, getResources, getSummary, runScan } from "../services/api.js";

const ScanContext = createContext(null);

// Holds the latest scan for every page. Add new shared data here (e.g. history, settings).
export function ScanProvider({ children }) {
  const [summaryData, setSummaryData] = useState(null);
  const [findings, setFindings] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    try {
      const [s, r, i] = await Promise.all([getSummary(), getResources(), getInventory()]);
      setSummaryData(s);
      setFindings(r.findings);
      setInventory(i.items);
      setError("");
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const scan = useCallback(async () => {
    setScanning(true);
    setError("");
    try {
      await runScan();
      await reload();
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setScanning(false);
    }
  }, [reload]);

  const value = useMemo(
    () => ({ summaryData, summary: summaryData?.summary, hasScan: Boolean(summaryData?.scan_id),
             findings, inventory, loading, scanning, error, scan, reload }),
    [summaryData, findings, inventory, loading, scanning, error, scan, reload]
  );
  return <ScanContext.Provider value={value}>{children}</ScanContext.Provider>;
}

export const useScan = () => useContext(ScanContext);
