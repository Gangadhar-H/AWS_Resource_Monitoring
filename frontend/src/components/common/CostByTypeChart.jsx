import { Bar } from "react-chartjs-2";
import { BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Tooltip } from "chart.js";
import { getType } from "../../config/resourceTypes.js";
import { money } from "../../utils/format.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function CostByTypeChart({ byType, title = "Cost by resource type" }) {
  const types = Object.keys(byType || {});
  if (types.length === 0) {
    return (
      <div className="card">
        <h2>{title}</h2>
        <p className="muted">Nothing wasteful found. Nice work.</p>
      </div>
    );
  }
  const data = {
    labels: types.map((t) => getType(t).label),
    datasets: [
      { label: "Monthly cost", data: types.map((t) => byType[t].monthly_cost), backgroundColor: "#6b7a99", borderRadius: 4 },
      { label: "Potential savings", data: types.map((t) => byType[t].potential_savings), backgroundColor: "#1f9d6b", borderRadius: 4 },
    ],
  };
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "bottom" },
      tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${money(c.parsed.y)}` } },
    },
    scales: {
      y: { beginAtZero: true, ticks: { callback: (v) => `$${v}` }, grid: { color: "rgba(128,128,128,.15)" } },
      x: { grid: { display: false } },
    },
  };
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="chart-box"><Bar data={data} options={options} /></div>
    </div>
  );
}
