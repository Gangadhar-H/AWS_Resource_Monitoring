import PageHeader from "../components/common/PageHeader.jsx";

const RULES = [
  ["EC2 instance", "Running for 14+ days with average CPU below 5%", "Underutilized"],
  ["EC2 instance", "Stopped but its EBS volumes are still attached", "Stopped"],
  ["EBS volume", "Not attached to any instance", "Unused"],
  ["Elastic IP", "Not associated with any resource", "Unused"],
];

const ROADMAP = [
  "More resource types (RDS, S3, Lambda, load balancers)",
  "Azure and Google Cloud providers",
  "Scheduled scans and email alerts",
  "Cost history and trend charts",
  "Live pricing from the cloud provider's price API",
  "Multi-account support and user login",
];

export default function About() {
  return (
    <>
      <PageHeader title="About" subtitle="How the tool decides what is wasteful, and what comes next." />
      <section className="card">
        <h2>Detection rules</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Resource</th><th>Condition</th><th>Result</th></tr></thead>
            <tbody>{RULES.map((r) => <tr key={r[1]}><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
      <section className="grid-2">
        <div className="card note">
          <h2>Assumptions</h2>
          <ul>
            <li>Prices are fixed approximations (on-demand, Linux, us-east-1), not live prices.</li>
            <li>Instances younger than the 14-day window are not judged.</li>
            <li>CPU comes from CloudWatch. Memory is not available without an agent.</li>
            <li>Underutilized instances assume a 50% saving from downsizing.</li>
            <li>The tool is read-only and never modifies your account.</li>
          </ul>
        </div>
        <div className="card note">
          <h2>Roadmap</h2>
          <ul>{ROADMAP.map((r) => <li key={r}>{r}</li>)}</ul>
        </div>
      </section>
    </>
  );
}
