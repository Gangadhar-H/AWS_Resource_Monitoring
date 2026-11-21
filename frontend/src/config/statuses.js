// Every status a resource can have. `action` is the savings action shown on the Savings page.
export const STATUSES = {
  healthy:       { label: "Healthy",       action: null },
  unused:        { label: "Unused",        action: "Delete or release unused resources" },
  stopped:       { label: "Stopped",       action: "Clean up volumes of stopped instances" },
  underutilized: { label: "Underutilized", action: "Downsize underutilized instances" },
};

export const statusLabel = (s) => STATUSES[s]?.label || s;
