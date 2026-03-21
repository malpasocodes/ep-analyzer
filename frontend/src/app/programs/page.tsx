"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  api,
  ProgramOverview,
  ProgramSuppressionSummary,
  CipSuppressionRisk,
  CipSummary,
  ProgramBrief,
} from "@/lib/api";
import StatCard from "@/components/StatCard";
import RiskBar from "@/components/charts/RiskBar";
import {
  formatCurrency,
  formatNumber,
  riskBadgeClass,
  PROGRAM_RISK_COLORS,
} from "@/lib/utils";

export default function ProgramsPage() {
  const [tab, setTab] = useState<"cips" | "search" | "suppression" | "impact">("cips");
  const [overview, setOverview] = useState<ProgramOverview | null>(null);

  useEffect(() => {
    api.getProgramOverview().then(setOverview).catch(() => {});
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Program-Level Analysis</h1>
      <p className="text-gray-600 mb-6">
        The EP test applies at the program level. Explore 213K+ programs across
        424 CIP codes. ~52% are privacy-suppressed (&lt;30 cohort) and ~20% have no cohort tracked.
      </p>

      {/* Overview cards */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard
            label="Total Programs"
            value={formatNumber(overview.total_programs)}
          />
          <StatCard
            label="With Earnings"
            value={formatNumber(overview.with_earnings)}
            sub={`${(100 - overview.suppression_rate).toFixed(0)}%`}
          />
          <StatCard
            label="Privacy Suppressed"
            value={formatNumber(overview.earnings_suppressed)}
            sub={`${overview.suppression_rate}% — cohort <30`}
            className="text-purple-600"
          />
          <StatCard
            label="No Cohort"
            value={formatNumber(overview.no_cohort)}
            sub="no earnings cohort tracked"
            className="text-gray-500"
          />
        </div>
      )}

      {/* Risk distribution bar */}
      {overview && (
        <div className="bg-white rounded-xl p-4 shadow-sm border mb-8">
          <RiskBar
            distribution={overview.risk_distribution}
            riskOnly
            title="Program Risk Distribution"
          />
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {[
          { id: "cips" as const, label: "CIP Explorer" },
          { id: "search" as const, label: "Program Search" },
          { id: "suppression" as const, label: "Most At-Risk" },
          { id: "impact" as const, label: "Suppression Impact" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t.id
                ? "bg-indigo-600 text-white"
                : "bg-white border text-gray-600 hover:bg-gray-50"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "cips" && <CipExplorer />}
      {tab === "search" && <ProgramSearch />}
      {tab === "suppression" && <TopRiskCips overview={overview} />}
      {tab === "impact" && <SuppressionImpact />}
    </div>
  );
}

function CipExplorer() {
  const [cips, setCips] = useState<CipSummary[]>([]);
  const [sortBy, setSortBy] = useState("total_programs");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api
      .getCipList({ sort_by: sortBy, limit: "100" } as Record<string, string>)
      .then(setCips)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [sortBy]);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">CIP Codes</h2>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="total_programs">Most Programs</option>
          <option value="pct_high_risk">Highest Risk</option>
        </select>
      </div>

      {loading && <p className="text-gray-400">Loading...</p>}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-2 px-2 font-medium text-gray-600">CIP</th>
              <th className="py-2 px-2 font-medium text-gray-600">Field</th>
              <th className="py-2 px-2 font-medium text-gray-600 text-right">Programs</th>
              <th className="py-2 px-2 font-medium text-gray-600 text-right">% High Risk</th>
              <th className="py-2 px-2 font-medium text-gray-600 text-right">% Passing</th>
              <th className="py-2 px-2 font-medium text-gray-600" style={{ width: "180px" }}>
                Risk
              </th>
            </tr>
          </thead>
          <tbody>
            {cips.map((c) => {
              const riskLevels = ["Very Low Risk", "Low Risk", "Moderate Risk", "High Risk"];
              const riskEntries = Object.entries(c.risk_distribution).filter(([l]) => riskLevels.includes(l));
              const total = riskEntries.reduce((sum, [, v]) => sum + v, 0);
              return (
                <tr key={c.cipcode} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-2 px-2 font-mono text-xs">
                    <Link
                      href={`/programs/${c.cipcode}`}
                      className="text-indigo-600 hover:underline"
                    >
                      {c.cipcode}
                    </Link>
                  </td>
                  <td className="py-2 px-2">
                    <Link
                      href={`/programs/${c.cipcode}`}
                      className="text-indigo-600 hover:underline"
                    >
                      {c.cip_desc.replace(/\.$/, "")}
                    </Link>
                  </td>
                  <td className="py-2 px-2 text-right">{formatNumber(c.total_programs)}</td>
                  <td className="py-2 px-2 text-right">
                    {c.pct_high_risk != null ? (
                      <span className={c.pct_high_risk > 50 ? "text-red-600 font-medium" : ""}>
                        {c.pct_high_risk.toFixed(0)}%
                      </span>
                    ) : "—"}
                  </td>
                  <td className="py-2 px-2 text-right">
                    {c.pct_passing != null ? `${c.pct_passing.toFixed(0)}%` : "—"}
                  </td>
                  <td className="py-2 px-2">
                    <div className="flex h-3 rounded-full overflow-hidden bg-gray-100">
                      {riskEntries.map(([level, count]) => (
                          <div
                            key={level}
                            style={{
                              width: `${(count / total) * 100}%`,
                              backgroundColor: PROGRAM_RISK_COLORS[level] || "#9ca3af",
                            }}
                            title={`${level}: ${count}`}
                          />
                        ))}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ProgramSearch() {
  const [query, setQuery] = useState("");
  const [state, setState] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [results, setResults] = useState<ProgramBrief[]>([]);
  const [loading, setLoading] = useState(false);

  const search = () => {
    setLoading(true);
    const params: Record<string, string> = { limit: "100" };
    if (query) params.search = query;
    if (state) params.state = state.toUpperCase();
    if (riskFilter) params.risk = riskFilter;
    api
      .searchPrograms(params)
      .then(setResults)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const timeout = setTimeout(search, 300);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, state, riskFilter]);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          placeholder="Search institution or field..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm flex-1 min-w-[200px]"
        />
        <input
          type="text"
          placeholder="State (e.g., CA)"
          value={state}
          onChange={(e) => setState(e.target.value.toUpperCase().slice(0, 2))}
          className="border rounded-lg px-3 py-2 text-sm w-20"
        />
        <select
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="">All Risk Levels</option>
          <option value="High Risk">High Risk</option>
          <option value="Moderate Risk">Moderate Risk</option>
          <option value="Low Risk">Low Risk</option>
          <option value="Very Low Risk">Very Low Risk</option>
          <option value="Privacy Suppressed">Privacy Suppressed</option>
          <option value="No Cohort">No Cohort</option>
        </select>
      </div>

      {loading && <p className="text-gray-400 text-sm">Searching...</p>}


      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-2 px-2 font-medium text-gray-600">Institution</th>
              <th className="py-2 px-2 font-medium text-gray-600">CIP</th>
              <th className="py-2 px-2 font-medium text-gray-600">Credential</th>
              <th className="py-2 px-2 font-medium text-gray-600 text-right">Earnings</th>
              <th className="py-2 px-2 font-medium text-gray-600 text-right">
                <span title="Earnings at 1yr / 2yr / 4yr / 5yr after completion">Trajectory</span>
              </th>
              <th className="py-2 px-2 font-medium text-gray-600 text-right">Threshold</th>
              <th className="py-2 px-2 font-medium text-gray-600">Risk</th>
            </tr>
          </thead>
          <tbody>
            {results.map((p, i) => (
              <tr key={`${p.unit_id}-${p.cipcode}-${p.credential_level}-${i}`} className="border-b last:border-0 hover:bg-gray-50">
                <td className="py-2 px-2">
                  <Link
                    href={`/institutions/${p.unit_id}`}
                    className="text-indigo-600 hover:underline"
                  >
                    {p.institution}
                  </Link>
                </td>
                <td className="py-2 px-2">
                  <Link
                    href={`/programs/${p.cipcode}`}
                    className="text-indigo-600 hover:underline"
                  >
                    {p.cip_desc.replace(/\.$/, "").slice(0, 35)}
                  </Link>
                </td>
                <td className="py-2 px-2 text-gray-600">{p.credential_desc || "—"}</td>
                <td className="py-2 px-2 text-right">
                  {p.program_earnings != null ? (
                    <span>
                      {formatCurrency(p.program_earnings)}
                      {p.earnings_timeframe && (
                        <span className="text-xs text-gray-400 ml-1">({p.earnings_timeframe})</span>
                      )}
                    </span>
                  ) : (
                    <span className="text-purple-500 text-xs">suppressed</span>
                  )}
                </td>
                <td className="py-2 px-2 text-right text-xs text-gray-500 font-mono whitespace-nowrap">
                  {[p.earn_mdn_1yr, p.earn_mdn_2yr, p.earn_mdn_4yr, p.earn_mdn_5yr].some(v => v != null) ? (
                    <span title={`1yr: ${p.earn_mdn_1yr != null ? formatCurrency(p.earn_mdn_1yr) : "—"} | 2yr: ${p.earn_mdn_2yr != null ? formatCurrency(p.earn_mdn_2yr) : "—"} | 4yr: ${p.earn_mdn_4yr != null ? formatCurrency(p.earn_mdn_4yr) : "—"} | 5yr: ${p.earn_mdn_5yr != null ? formatCurrency(p.earn_mdn_5yr) : "—"}`}>
                      {[
                        p.earn_mdn_1yr != null ? `${Math.round(p.earn_mdn_1yr / 1000)}k` : "—",
                        p.earn_mdn_2yr != null ? `${Math.round(p.earn_mdn_2yr / 1000)}k` : "—",
                        p.earn_mdn_4yr != null ? `${Math.round(p.earn_mdn_4yr / 1000)}k` : "—",
                        p.earn_mdn_5yr != null ? `${Math.round(p.earn_mdn_5yr / 1000)}k` : "—",
                      ].join(" / ")}
                    </span>
                  ) : "—"}
                </td>
                <td className="py-2 px-2 text-right">
                  {p.state_threshold != null ? formatCurrency(p.state_threshold) : "—"}
                </td>
                <td className="py-2 px-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${riskBadgeClass(p.risk_level)}`}>
                    {p.risk_level}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {results.length === 0 && !loading && (
          <p className="text-gray-400 text-sm py-4 text-center">
            No results. Try a different search.
          </p>
        )}
      </div>
    </div>
  );
}

function TopRiskCips({ overview }: { overview: ProgramOverview | null }) {
  if (!overview) return <p className="text-gray-400">Loading...</p>;

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <h2 className="text-lg font-semibold mb-2">Most Vulnerable CIP Codes</h2>
      <p className="text-sm text-gray-600 mb-4">
        Fields with the highest percentage of programs failing the EP test
        (minimum 5 programs with earnings data).
      </p>
      <div className="space-y-3">
        {overview.top_risk_cips.map((c) => (
          <div key={c.cipcode} className="flex items-center gap-3">
            <Link
              href={`/programs/${c.cipcode}`}
              className="text-indigo-600 hover:underline font-mono text-sm w-12"
            >
              {c.cipcode}
            </Link>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <Link
                  href={`/programs/${c.cipcode}`}
                  className="text-sm font-medium text-indigo-600 hover:underline"
                >
                  {c.cip_desc.replace(/\.$/, "")}
                </Link>
                <span className="text-sm text-red-600 font-medium">
                  {c.pct_high_risk}% fail
                </span>
              </div>
              <div className="flex h-2 rounded-full overflow-hidden bg-gray-100">
                <div
                  className="bg-red-400"
                  style={{ width: `${c.pct_high_risk}%` }}
                />
                <div
                  className="bg-green-400"
                  style={{ width: `${100 - c.pct_high_risk}%` }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-0.5">{formatNumber(c.total_programs)} programs</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SuppressionImpact() {
  const [data, setData] = useState<ProgramSuppressionSummary | null>(null);
  const [cipData, setCipData] = useState<CipSuppressionRisk[] | null>(null);
  const [cipSort, setCipSort] = useState<"high_risk" | "total" | "cipcode">("high_risk");

  useEffect(() => {
    api.getSuppressionSummary().then(setData).catch(() => {});
    api.getSuppressionByCip().then(setCipData).catch(() => {});
  }, []);

  if (!data) return <p className="text-gray-400">Loading...</p>;

  const riskDist = data.estimated_risk_distribution;
  const totalEstimated = Object.values(riskDist).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <h2 className="text-lg font-semibold mb-2">Suppression Impact Analysis</h2>
        <p className="text-sm text-gray-600 mb-6">
          Over half of all programs have earnings suppressed by the College Scorecard (cohort &lt; 30 students).
          Using Monte Carlo simulation with national field-of-study priors, institution effects, and local labor
          market adjustments, we estimated risk levels for suppressed programs without exposing individual program estimates.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard
            label="Total Suppressed"
            value={formatNumber(data.total_suppressed)}
            className="text-purple-600"
          />
          <StatCard
            label="Estimable"
            value={formatNumber(data.estimable)}
            sub={`${((data.estimable / data.total_suppressed) * 100).toFixed(0)}% of suppressed`}
          />
          <StatCard
            label="Inestimable"
            value={formatNumber(data.inestimable)}
            sub="insufficient prior data"
          />
          <StatCard
            label="Median Est. Earnings"
            value={data.median_estimated_earnings != null ? formatCurrency(data.median_estimated_earnings) : "—"}
          />
        </div>

        {totalEstimated > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Estimated Risk Distribution</h3>
            <RiskBar distribution={riskDist} riskOnly title="" />
          </div>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <p className="text-2xl font-bold text-red-600">{formatNumber(riskDist["High Risk"] || 0)}</p>
            <p className="text-xs text-gray-600">Est. High Risk</p>
          </div>
          <div className="text-center p-3 bg-amber-50 rounded-lg">
            <p className="text-2xl font-bold text-amber-600">{formatNumber(riskDist["Moderate Risk"] || 0)}</p>
            <p className="text-xs text-gray-600">Est. Moderate Risk</p>
          </div>
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">{formatNumber(riskDist["Low Risk"] || 0)}</p>
            <p className="text-xs text-gray-600">Est. Low Risk</p>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">{formatNumber(riskDist["Very Low Risk"] || 0)}</p>
            <p className="text-xs text-gray-600">Est. Very Low Risk</p>
          </div>
        </div>

        {data.prob_pass_state_mean != null && (
          <p className="text-sm text-gray-600">
            Average probability of passing the EP test across estimable suppressed programs:{" "}
            <span className="font-semibold">{(data.prob_pass_state_mean * 100).toFixed(0)}%</span>
          </p>
        )}
      </div>

      {cipData && cipData.length > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-2">Estimated Risk by Field of Study</h2>
          <p className="text-sm text-gray-600 mb-4">
            Monte Carlo risk estimates for suppressed programs, aggregated by CIP code.
            No individual programs are identified.
          </p>

          <div className="flex gap-2 mb-4">
            {([["high_risk", "Most At-Risk"], ["total", "Most Programs"], ["cipcode", "CIP Code"]] as const).map(([val, label]) => (
              <button
                key={val}
                onClick={() => setCipSort(val)}
                className={`px-3 py-1.5 rounded text-xs font-medium ${
                  cipSort === val ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-white">
                <tr className="border-b text-left">
                  <th className="py-2 px-2 font-medium text-gray-600">CIP</th>
                  <th className="py-2 px-2 font-medium text-gray-600">Field</th>
                  <th className="py-2 px-2 font-medium text-gray-600 text-right">Total</th>
                  <th className="py-2 px-2 font-medium text-red-600 text-right">High</th>
                  <th className="py-2 px-2 font-medium text-amber-600 text-right">Moderate</th>
                  <th className="py-2 px-2 font-medium text-blue-600 text-right">Low</th>
                  <th className="py-2 px-2 font-medium text-green-600 text-right">Very Low</th>
                </tr>
              </thead>
              <tbody>
                {[...cipData]
                  .sort((a, b) =>
                    cipSort === "cipcode" ? a.cipcode.localeCompare(b.cipcode)
                    : cipSort === "total" ? b.total - a.total
                    : b.high_risk - a.high_risk
                  )
                  .map((c) => (
                  <tr key={c.cipcode} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-1.5 px-2 font-mono text-xs">
                      <Link href={`/programs/${c.cipcode}`} className="text-indigo-600 hover:underline">
                        {c.cipcode}
                      </Link>
                    </td>
                    <td className="py-1.5 px-2 text-xs">{c.cip_desc.replace(/\.$/, "").slice(0, 50)}</td>
                    <td className="py-1.5 px-2 text-right text-xs font-medium">{formatNumber(c.total)}</td>
                    <td className="py-1.5 px-2 text-right text-xs text-red-600 font-medium">{c.high_risk > 0 ? formatNumber(c.high_risk) : "—"}</td>
                    <td className="py-1.5 px-2 text-right text-xs text-amber-600">{c.moderate_risk > 0 ? formatNumber(c.moderate_risk) : "—"}</td>
                    <td className="py-1.5 px-2 text-right text-xs text-blue-600">{c.low_risk > 0 ? formatNumber(c.low_risk) : "—"}</td>
                    <td className="py-1.5 px-2 text-right text-xs text-green-600">{c.very_low_risk > 0 ? formatNumber(c.very_low_risk) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="bg-gray-50 rounded-xl p-6 border">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Methodology</h3>
        <p className="text-sm text-gray-600 leading-relaxed">
          For each suppressed program, we draw from a hierarchical prior: national median earnings for the
          program&apos;s field of study and credential level, adjusted by an institution-level performance
          effect (how the institution&apos;s graduates perform relative to the national average) and a
          geographic factor (local vs. statewide labor market conditions). We run 1,000 Monte Carlo draws
          per program to produce estimated earnings distributions and pass probabilities. Individual program
          estimates are not published to protect the privacy of small cohorts.
        </p>
      </div>
    </div>
  );
}
