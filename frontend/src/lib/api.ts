const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" &&
  window.location.hostname !== "localhost"
    ? "https://ep-analyzer-api.onrender.com"
    : "http://localhost:8000");

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
  metric: string;
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

// Program-level types
export interface ProgramBrief {
  unit_id: number;
  institution: string;
  state: string;
  cipcode: string;
  cip_desc: string;
  credential_level: number | null;
  credential_desc: string | null;
  completions: number | null;
  program_earnings: number | null;
  earnings_timeframe: string | null;
  earn_mdn_1yr: number | null;
  earn_mdn_2yr: number | null;
  earn_mdn_4yr: number | null;
  earn_mdn_5yr: number | null;
  earnings_suppressed: boolean;
  state_threshold: number | null;
  earnings_margin_pct: number | null;
  risk_level: string;
  estimated_earnings: number | null;
  earnings_ci_low: number | null;
  earnings_ci_high: number | null;
  prob_pass_state: number | null;
  estimated_risk_level: string | null;
  estimation_method: string | null;
}

export interface ProgramOverview {
  total_programs: number;
  with_earnings: number;
  earnings_suppressed: number;
  no_cohort: number;
  suppression_rate: number;
  risk_distribution: Record<string, number>;
  cip_count: number;
  institution_count: number;
  top_risk_cips: {
    cipcode: string;
    cip_desc: string;
    total_programs: number;
    pct_high_risk: number;
  }[];
}

export interface CipSummary {
  cipcode: string;
  cip_desc: string;
  total_programs: number;
  total_completions: number;
  with_earnings: number;
  median_earnings: number | null;
  pct_passing: number | null;
  pct_high_risk: number | null;
  risk_distribution: Record<string, number>;
}

export interface InstitutionProgramsResponse {
  unit_id: number;
  institution: string;
  state: string;
  total_programs: number;
  with_earnings: number;
  suppressed: number;
  programs: ProgramBrief[];
}

export interface ProgramReclassificationProgram extends ReclassificationProgram {
  cipcode: string;
  cip_desc: string;
  credential_desc: string | null;
  completions: number | null;
  institution: string;
}

export interface ProgramReclassificationResult {
  state: string;
  threshold: number;
  inequality: number;
  total_programs: number;
  with_earnings: number;
  suppressed: number;
  pass_both: number;
  fail_both: number;
  pass_local_only: number;
  pass_state_only: number;
  real_benchmark_count: number;
  synthetic_benchmark_count: number;
  programs: ProgramReclassificationProgram[];
}

export interface ProgramSuppressionSummary {
  total_suppressed: number;
  estimable: number;
  inestimable: number;
  estimated_risk_distribution: Record<string, number>;
  prob_pass_state_mean: number | null;
  median_estimated_earnings: number | null;
}

export interface CipSuppressionRisk {
  cipcode: string;
  cip_desc: string;
  total: number;
  high_risk: number;
  moderate_risk: number;
  low_risk: number;
  very_low_risk: number;
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
  getReclassification: (state: string, inequality: number, metric: string = "P10") =>
    fetchAPI<ReclassificationResult>(
      `/api/analysis/reclassification?state=${state}&inequality=${inequality}&metric=${metric}`
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

  // Program-level endpoints
  getProgramOverview: () => fetchAPI<ProgramOverview>("/api/programs/overview"),
  searchPrograms: (params: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return fetchAPI<ProgramBrief[]>(`/api/programs/search?${qs}`);
  },
  getInstitutionPrograms: (unitId: number) =>
    fetchAPI<InstitutionProgramsResponse>(
      `/api/programs/by-institution/${unitId}`
    ),
  getCipSummary: (cipcode: string) =>
    fetchAPI<CipSummary>(`/api/programs/by-cip/${cipcode}`),
  getCipList: (params?: { sort_by?: string; limit?: number }) => {
    const qs = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params || {}).filter(([, v]) => v != null)
      ) as Record<string, string>
    ).toString();
    return fetchAPI<CipSummary[]>(`/api/programs/cip-list?${qs}`);
  },
  getProgramReclassification: (state: string, inequality: number) =>
    fetchAPI<ProgramReclassificationResult>(
      `/api/programs/reclassification?state=${state}&inequality=${inequality}`
    ),
  getSuppressionSummary: () =>
    fetchAPI<ProgramSuppressionSummary>("/api/programs/suppression-summary"),
  getSuppressionByCip: () =>
    fetchAPI<CipSuppressionRisk[]>("/api/programs/suppression-by-cip?limit=500"),
};
