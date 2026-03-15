const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export interface Overview {
  total_institutions: number;
  with_earnings: number;
  states_covered: number;
  risk_distribution: Record<string, number>;
  sector_distribution: Record<string, number>;
  total_programs: number;
  assessable_programs: number;
}

export interface StateSummary {
  state: string;
  state_name: string;
  threshold: number;
  institution_count: number;
  risk_distribution: Record<string, number>;
}

export interface StateDetail extends StateSummary {
  institutions: InstitutionBrief[];
  margin_histogram: number[];
}

export interface InstitutionBrief {
  unit_id: number;
  name: string;
  state: string;
  sector: string | null;
  enrollment: number | null;
  median_earnings: number | null;
  threshold: number | null;
  earnings_margin_pct: number | null;
  risk_level: string;
  total_programs: number | null;
}

export interface InstitutionDetail {
  unit_id: number;
  name: string;
  state: string;
  sector: string | null;
  enrollment: number | null;
  graduation_rate: number | null;
  cost: number | null;
  earnings_p6: number | null;
  earnings_p10: number | null;
  median_earnings: number | null;
  threshold: number | null;
  earnings_margin: number | null;
  earnings_margin_pct: number | null;
  risk_level: string;
  total_programs: number | null;
  assessable_programs: number | null;
  total_completions: number | null;
}

export interface PeerInstitution {
  unit_id: number;
  name: string;
  median_earnings: number | null;
  earnings_margin_pct: number | null;
  risk_level: string;
  enrollment: number | null;
}

export interface ReclassificationResult {
  state: string;
  threshold: number;
  inequality: number;
  total_programs: number;
  pass_both: number;
  fail_both: number;
  pass_local_only: number;
  pass_state_only: number;
  real_benchmark_count: number;
  synthetic_benchmark_count: number;
  programs: ReclassificationProgram[];
}

export interface ReclassificationProgram {
  unit_id: number;
  name: string;
  sector: string | null;
  county: string | null;
  earnings: number;
  state_benchmark: number;
  local_benchmark: number;
  distance_state: number;
  distance_local: number;
  pass_state: boolean;
  pass_local: boolean;
  classification: string;
  benchmark_source: "real" | "synthetic";
}

export interface SensitivityResult {
  unit_id: number;
  name: string;
  current_earnings: number | null;
  threshold: number | null;
  current_margin_pct: number | null;
  scenarios: {
    change_pct: number;
    adjusted_earnings: number;
    margin_pct: number;
    passes: boolean;
  }[];
}

export interface MarginDistribution {
  state: string | null;
  sector: string | null;
  margins: number[];
  risk_counts: Record<string, number>;
  near_threshold_count: number;
  total_count: number;
}

export interface EarlyVsLate {
  state: string | null;
  institutions: {
    unit_id: number;
    name: string;
    state: string;
    sector: string | null;
    earnings_p6: number;
    earnings_p10: number;
    threshold: number | null;
    pass_p6: boolean | null;
    pass_p10: boolean | null;
    changed: boolean | null;
  }[];
}

export const api = {
  getOverview: () => fetchAPI<Overview>("/api/overview"),
  getStates: () => fetchAPI<StateSummary[]>("/api/states"),
  getState: (state: string) => fetchAPI<StateDetail>(`/api/states/${state}`),
  searchInstitutions: (params: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return fetchAPI<InstitutionBrief[]>(`/api/institutions?${qs}`);
  },
  getInstitution: (id: number) =>
    fetchAPI<InstitutionDetail>(`/api/institutions/${id}`),
  getPeers: (id: number) =>
    fetchAPI<PeerInstitution[]>(`/api/institutions/${id}/peers`),
  getReclassification: (state: string, inequality: number) =>
    fetchAPI<ReclassificationResult>(
      `/api/analysis/reclassification?state=${state}&inequality=${inequality}`
    ),
  getSensitivity: (unitId: number) =>
    fetchAPI<SensitivityResult>(`/api/analysis/sensitivity?unit_id=${unitId}`),
  getMargins: (params?: { state?: string; sector?: string }) => {
    const qs = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params || {}).filter(([, v]) => v != null)
      ) as Record<string, string>
    ).toString();
    return fetchAPI<MarginDistribution>(`/api/analysis/margins?${qs}`);
  },
  getEarlyVsLate: (state?: string) => {
    const qs = state ? `?state=${state}` : "";
    return fetchAPI<EarlyVsLate>(`/api/analysis/early-vs-late${qs}`);
  },
};
