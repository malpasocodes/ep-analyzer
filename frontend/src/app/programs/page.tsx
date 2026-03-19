"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  api,
  ProgramOverview,
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
  const [tab, setTab] = useState<"cips" | "search" | "suppression">("cips");
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

      <div className="flex items-start gap-4 mb-3 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded-full bg-teal-500" />
          <span><span className="text-teal-600 font-medium">~$XX,XXX</span> = Monte Carlo estimate (hover for 80% CI)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block w-2.5 h-2.5 rounded-full border border-dashed border-gray-400" />
          <span><span className="font-medium">Est. Risk</span> = simulated risk level from estimated earnings</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-2 px-2 font-medium text-gray-600">Institution</th>
              <th className="py-2 px-2 font-medium text-gray-600">CIP</th>
              <th className="py-2 px-2 font-medium text-gray-600">Credential</th>
              <th className="py-2 px-2 font-medium text-gray-600 text-right">Earnings</th>
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
                  {p.program_earnings != null ? formatCurrency(p.program_earnings) : (
                    p.estimated_earnings != null ? (
                      <span className="text-teal-600" title={`Monte Carlo est. ${formatCurrency(p.earnings_ci_low)}–${formatCurrency(p.earnings_ci_high)} (80% CI) | P(pass): ${p.prob_pass_state != null ? (p.prob_pass_state * 100).toFixed(0) + "%" : "N/A"}`}>
                        ~{formatCurrency(p.estimated_earnings)}
                      </span>
                    ) : (
                      <span className="text-purple-500 text-xs">suppressed</span>
                    )
                  )}
                </td>
                <td className="py-2 px-2 text-right">
                  {p.state_threshold != null ? formatCurrency(p.state_threshold) : "—"}
                </td>
                <td className="py-2 px-2">
                  {(() => {
                    const displayRisk = p.estimated_risk_level
                      ? `Est. ${p.estimated_risk_level}`
                      : p.risk_level;
                    return (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${riskBadgeClass(displayRisk)}`}>
                        {displayRisk}
                      </span>
                    );
                  })()}
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

