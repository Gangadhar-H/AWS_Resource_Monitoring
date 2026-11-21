import { Outlet } from "react-router-dom";
import Navbar from "../components/layout/Navbar.jsx";
import { useScan } from "../context/ScanContext.jsx";

export default function Layout() {
  const { error } = useScan();
  return (
    <>
      <Navbar />
      <main className="page">
        {error && <div className="alert" role="alert">{error}</div>}
        <Outlet />
      </main>
    </>
  );
}
