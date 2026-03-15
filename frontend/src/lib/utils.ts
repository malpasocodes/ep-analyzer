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
    "No Data": "bg-gray-100 text-gray-600",
  };
  return map[risk] || "bg-gray-100 text-gray-600";
}
