export const money = (n) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: 2 }).format(n || 0);

export const dateTime = (iso) =>
  iso ? new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "-";

export const prettyKey = (k) => k.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

export const percent = (n, digits = 0) => `${(n || 0).toFixed(digits)}%`;
