// Resource type registry. To support a new resource (RDS, S3, Lambda...):
// add an entry here; cards, filters and detail pages pick it up automatically.
import { dateTime } from "../utils/format.js";

const list = (v) => (Array.isArray(v) ? (v.length ? v.join(", ") : "None") : v);
const yesNo = (v) => (v ? "Yes" : "No");

export const RESOURCE_TYPES = {
  ec2: {
    label: "EC2 Instance",
    plural: "EC2 Instances",
    short: "EC2",
    color: "#d9772b",
    cardFacts: (r) => [["Type", r.details.instance_type], ["State", r.details.state]],
    detailFields: [
      ["instance_type", "Instance type"],
      ["state", "State"],
      ["launch_time", "Launched", dateTime],
      ["availability_zone", "Availability zone"],
      ["public_ip", "Public IP"],
      ["private_ip", "Private IP"],
      ["volume_ids", "Attached volumes", list],
    ],
  },
  ebs: {
    label: "EBS Volume",
    plural: "EBS Volumes",
    short: "EBS",
    color: "#2f7fd3",
    cardFacts: (r) => [["Size", `${r.details.size_gb} GB`], ["Status", r.details.state === "available" ? "Not attached" : "Attached"]],
    detailFields: [
      ["size_gb", "Size (GB)"],
      ["volume_type", "Volume type"],
      ["state", "State"],
      ["attached_to", "Attached to", list],
      ["availability_zone", "Availability zone"],
      ["encrypted", "Encrypted", yesNo],
      ["iops", "IOPS"],
      ["create_time", "Created", dateTime],
    ],
  },
  eip: {
    label: "Elastic IP",
    plural: "Elastic IPs",
    short: "EIP",
    color: "#8a5cd6",
    cardFacts: (r) => [["IP", r.details.public_ip], ["Status", r.details.associated ? "Associated" : "Not associated"]],
    detailFields: [
      ["public_ip", "Public IP"],
      ["associated", "Associated", yesNo],
      ["instance_id", "Associated instance"],
      ["domain", "Domain"],
    ],
  },
};

const FALLBACK = {
  label: "Resource", plural: "Resources", short: "RES", color: "#667085",
  cardFacts: () => [], detailFields: [],
};

export const getType = (t) =>
  RESOURCE_TYPES[t] || { ...FALLBACK, label: t.toUpperCase(), plural: t.toUpperCase(), short: t.toUpperCase().slice(0, 4) };
