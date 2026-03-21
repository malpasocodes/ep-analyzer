"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, RiskAnalytics } from "@/lib/api";
import StatCard from "@/components/StatCard";
import { formatNumber, formatCurrency } from "@/lib/utils";

const RISK_LEVELS = ["High Risk", "Moderate Risk", "Low Risk", "Very Low Risk"] as const;

const RISK_COLORS: Record<string, { bg: string; text: string; bar: string }> = {
  "High Risk": { bg: "bg-red-50", text: "text-red-600", bar: "bg-red-400" },
  "Moderate Risk": { bg: "bg-amber-50", text: "text-amber-600", bar: "bg-amber-400" },
  "Low Risk": { bg: "bg-blue-50", text: "text-blue-600", bar: "bg-blue-400" },
  "Very Low Risk": { bg: "bg-green-50", text: "text-green-600", bar: "bg-green-400" },
};

export default function RiskAnalyticsPage() {
  const [data, setData] = useState<RiskAnalytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getRiskAnalytics().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="text-red-600 p-8">{error}</div>;
  if (!data) return <div className="p-8 text-gray-500">Loading...</div>;

  const totalReported = Object.values(data.reported_risk).reduce((a, b) => a + b, 0);
  const totalEstimated = Object.values(data.estimated_risk).reduce((a, b) => a + b, 0);
  const totalCombined = RISK_LEVELS.reduce((a, r) => a + (data.combined_risk[r] || 0), 0);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Risk Analytics</h1>
      <p className="text-gray-600 mb-8">
        How many programs fall into each risk category, broken down by data source:
        reported earnings from the College Scorecard vs. Monte Carlo estimates for privacy-suppressed programs.
      </p>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Programs" value={formatNumber(data.total_programs)} />
        <StatCard
          label="With Reported Earnings"
          value={formatNumber(data.with_earnings)}
          sub={`${((data.with_earnings / data.total_programs) * 100).toFixed(0)}%`}
        />
        <StatCard
          label="Privacy Suppressed"
          value={formatNumber(data.earnings_suppressed)}
          sub={`${((data.earnings_suppressed / data.total_programs) * 100).toFixed(0)}%`}
          className="text-purple-600"
        />
        <StatCard
          label="No Cohort"
          value={formatNumber(data.no_cohort)}
          sub="not assessable"
        />
      </div>

      {/* Combined risk distribution with reported/estimated split */}
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-8">
        <h2 className="text-lg font-semibold mb-4">Risk Distribution: Reported vs. Estimated</h2>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="py-3 px-3 font-medium text-gray-600">Risk Category</th>
                <th className="py-3 px-3 font-medium text-gray-600 text-right">Reported</th>
                <th className="py-3 px-3 font-medium text-gray-600 text-right">MC Estimated</th>
                <th className="py-3 px-3 font-medium text-gray-600 text-right">Combined</th>
                <th className="py-3 px-3 font-medium text-gray-600 w-1/3">Distribution</th>
              </tr>
            </thead>
            <tbody>
              {RISK_LEVELS.map((level) => {
                const reported = data.reported_risk[level] || 0;
                const estimated = data.estimated_risk[level] || 0;
                const combined = data.combined_risk[level] || 0;
                const pct = totalCombined > 0 ? (combined / totalCombined) * 100 : 0;
                const colors = RISK_COLORS[level];
                return (
                  <tr key={level} className="border-b last:border-0">
                    <td className="py-3 px-3">
                      <span className={`font-medium ${colors.text}`}>{level}</span>
                    </td>
                    <td className="py-3 px-3 text-right font-mono">
                      {formatNumber(reported)}
                    </td>
                    <td className="py-3 px-3 text-right font-mono text-gray-500">
                      {formatNumber(estimated)}
                    </td>
                    <td className="py-3 px-3 text-right font-mono font-semibold">
                      {formatNumber(combined)}
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${colors.bar} rounded-full`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500 w-12 text-right">{pct.toFixed(1)}%</span>
                      </div>
                    </td>
                  </tr>
                );
              })}
              <tr className="border-t-2 font-semibold">
                <td className="py-3 px-3">Total (risk-assessable)</td>
                <td className="py-3 px-3 text-right font-mono">{formatNumber(totalReported)}</td>
                <td className="py-3 px-3 text-right font-mono text-gray-500">{formatNumber(totalEstimated)}</td>
                <td className="py-3 px-3 text-right font-mono">{formatNumber(totalCombined)}</td>
                <td className="py-3 px-3"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual comparison: reported vs estimated */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h3 className="text-md font-semibold mb-1">Reported Earnings</h3>
          <p className="text-xs text-gray-500 mb-4">{formatNumber(data.with_earnings)} programs with College Scorecard data</p>
          <div className="space-y-3">
            {RISK_LEVELS.map((level) => {
              const count = data.reported_risk[level] || 0;
              const pct = totalReported > 0 ? (count / totalReported) * 100 : 0;
              const colors = RISK_COLORS[level];
              return (
                <div key={level}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={colors.text}>{level}</span>
                    <span className="font-mono">{formatNumber(count)} ({pct.toFixed(1)}%)</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className={`h-full ${colors.bar} rounded-full`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h3 className="text-md font-semibold mb-1">Monte Carlo Estimated</h3>
          <p className="text-xs text-gray-500 mb-4">{formatNumber(totalEstimated)} suppressed programs with MC estimates</p>
          <div className="space-y-3">
            {RISK_LEVELS.map((level) => {
              const count = data.estimated_risk[level] || 0;
              const pct = totalEstimated > 0 ? (count / totalEstimated) * 100 : 0;
              const colors = RISK_COLORS[level];
              return (
                <div key={level}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={colors.text}>{level}</span>
                    <span className="font-mono">{formatNumber(count)} ({pct.toFixed(1)}%)</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className={`h-full ${colors.bar} rounded-full`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* By sector */}
      {data.by_sector.length > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border mb-8">
          <h2 className="text-lg font-semibold mb-4">Risk by Sector</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-2 px-2 font-medium text-gray-600">Sector</th>
                  <th className="py-2 px-2 font-medium text-gray-600 text-right">Programs</th>
                  <th className="py-2 px-2 font-medium text-gray-600 text-right">Reported</th>
                  <th className="py-2 px-2 font-medium text-gray-600 text-right">Suppressed</th>
                  <th className="py-2 px-2 font-medium text-red-600 text-right">High Risk</th>
                  <th className="py-2 px-2 font-medium text-amber-600 text-right">Moderate</th>
                  <th className="py-2 px-2 font-medium text-blue-600 text-right">Low</th>
                  <th className="py-2 px-2 font-medium text-green-600 text-right">Very Low</th>
                </tr>
              </thead>
              <tbody>
                {data.by_sector.map((s) => (
                  <tr key={s.sector} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-2 px-2 text-xs">{s.sector}</td>
                    <td className="py-2 px-2 text-right text-xs">{formatNumber(s.total)}</td>
                    <td className="py-2 px-2 text-right text-xs">{formatNumber(s.with_earnings)}</td>
                    <td className="py-2 px-2 text-right text-xs text-purple-600">{formatNumber(s.suppressed)}</td>
                    <td className="py-2 px-2 text-right text-xs text-red-600 font-medium">{s.high_risk > 0 ? formatNumber(s.high_risk) : "—"}</td>
                    <td className="py-2 px-2 text-right text-xs text-amber-600">{s.moderate_risk > 0 ? formatNumber(s.moderate_risk) : "—"}</td>
                    <td className="py-2 px-2 text-right text-xs text-blue-600">{s.low_risk > 0 ? formatNumber(s.low_risk) : "—"}</td>
                    <td className="py-2 px-2 text-right text-xs text-green-600">{s.very_low_risk > 0 ? formatNumber(s.very_low_risk) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top states by risk */}
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-8">
        <h2 className="text-lg font-semibold mb-4">Top 20 States by High Risk Programs</h2>
        <p className="text-xs text-gray-500 mb-4">
          Shows how many High Risk programs come from reported earnings vs. Monte Carlo estimates.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="py-2 px-2 font-medium text-gray-600">State</th>
                <th className="py-2 px-2 font-medium text-gray-600 text-right">Programs</th>
                <th className="py-2 px-2 font-medium text-red-600 text-right">High Risk</th>
                <th className="py-2 px-2 font-medium text-gray-600 text-right">Reported</th>
                <th className="py-2 px-2 font-medium text-gray-600 text-right">Estimated</th>
                <th className="py-2 px-2 font-medium text-amber-600 text-right">Moderate</th>
                <th className="py-2 px-2 font-medium text-gray-600 w-1/4">High Risk Breakdown</th>
              </tr>
            </thead>
            <tbody>
              {data.by_state_top.map((s) => {
                const reportedPct = s.high_risk > 0 ? (s.reported_high_risk / s.high_risk) * 100 : 0;
                const estimatedPct = s.high_risk > 0 ? (s.estimated_high_risk / s.high_risk) * 100 : 0;
                return (
                  <tr key={s.state} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="py-2 px-2">
                      <Link href={`/states/${s.state}`} className="text-indigo-600 hover:underline font-medium">
                        {s.state}
                      </Link>
                    </td>
                    <td className="py-2 px-2 text-right text-xs">{formatNumber(s.total)}</td>
                    <td className="py-2 px-2 text-right text-xs text-red-600 font-semibold">{formatNumber(s.high_risk)}</td>
                    <td className="py-2 px-2 text-right text-xs">{formatNumber(s.reported_high_risk)}</td>
                    <td className="py-2 px-2 text-right text-xs text-gray-500">{formatNumber(s.estimated_high_risk)}</td>
                    <td className="py-2 px-2 text-right text-xs text-amber-600">{s.moderate_risk > 0 ? formatNumber(s.moderate_risk) : "—"}</td>
                    <td className="py-2 px-2">
                      {s.high_risk > 0 && (
                        <div className="flex h-3 rounded-full overflow-hidden bg-gray-100">
                          <div
                            className="bg-red-400"
                            style={{ width: `${reportedPct}%` }}
                            title={`Reported: ${s.reported_high_risk}`}
                          />
                          <div
                            className="bg-red-200"
                            style={{ width: `${estimatedPct}%` }}
                            title={`Estimated: ${s.estimated_high_risk}`}
                          />
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="flex gap-4 mt-3 text-xs text-gray-500">
          <div className="flex items-center gap-1.5">
            <span className="inline-block w-3 h-3 rounded bg-red-400" />
            <span>Reported</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="inline-block w-3 h-3 rounded bg-red-200" />
            <span>MC Estimated</span>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 rounded-xl p-6 border">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">About This Data</h3>
        <p className="text-sm text-gray-600 leading-relaxed">
          <strong>Reported</strong> risk levels are derived from College Scorecard median earnings compared against
          statewide high school graduate earnings thresholds. <strong>Estimated</strong> risk levels use Monte Carlo
          simulation for privacy-suppressed programs (cohort &lt; 30) — drawing from national field-of-study
          earnings priors adjusted for institution quality and local labor market conditions. Individual program
          estimates are not published. See{" "}
          <Link href="/programs" className="text-indigo-600 hover:underline">
            Programs &gt; Suppression Impact
          </Link>{" "}
          for methodology details.
        </p>
      </div>
    </div>
  );
}
