export function formatCurrency(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return new Intl.NumberFormat("en-US").format(value);
}

export function formatPct(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
}

export const RISK_COLORS: Record<string, string> = {
  "Very Low Risk": "#22c55e",
  "Low Risk": "#84cc16",
  "Moderate Risk": "#f59e0b",
  "High Risk": "#ef4444",
  "No Cohort": "#9ca3af",
  "No Data": "#9ca3af",
};

export const CLASSIFICATION_COLORS: Record<string, string> = {
  "Pass Both": "#22c55e",
  "Fail Both": "#ef4444",
  "Pass Local Only": "#3b82f6",
  "Pass State Only": "#f59e0b",
};

export function riskBadgeClass(risk: string): string {
  const map: Record<string, string> = {
    "Very Low Risk": "bg-green-100 text-green-800",
    "Low Risk": "bg-lime-100 text-lime-800",
    "Moderate Risk": "bg-amber-100 text-amber-800",
    "High Risk": "bg-red-100 text-red-800",
    "Privacy Suppressed": "bg-purple-100 text-purple-800",
    "No Cohort": "bg-gray-100 text-gray-600",
    "No Data": "bg-gray-100 text-gray-600",
    "Est. Very Low Risk": "bg-teal-50 text-teal-700 border border-teal-300 border-dashed",
    "Est. Low Risk": "bg-teal-50 text-teal-600 border border-teal-300 border-dashed",
    "Est. Moderate Risk": "bg-teal-50 text-amber-600 border border-teal-300 border-dashed",
    "Est. High Risk": "bg-teal-50 text-red-600 border border-teal-300 border-dashed",
  };
  return map[risk] || "bg-gray-100 text-gray-600";
}

export const PROGRAM_RISK_COLORS: Record<string, string> = {
  ...RISK_COLORS,
  "Privacy Suppressed": "#a78bfa",
  "Est. Very Low Risk": "#5eead4",
  "Est. Low Risk": "#99f6e4",
  "Est. Moderate Risk": "#fcd34d",
  "Est. High Risk": "#fca5a5",
};

export function formatCipCode(cip: string): string {
  if (cip.includes(".")) return cip;
  const padded = cip.padStart(4, "0");
  return `${padded.slice(0, 2)}.${padded.slice(2)}`;
}

export function credentialLabel(level: number | null): string {
  if (level == null) return "Unknown";
  const map: Record<number, string> = {
    1: "Certificate",
    2: "Associate's",
    3: "Bachelor's",
    4: "Post-bacc Cert",
    5: "Master's",
    6: "Doctoral",
    7: "Professional",
    8: "Grad Cert",
  };
  return map[level] || `Level ${level}`;
}
