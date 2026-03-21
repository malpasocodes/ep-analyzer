"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api, CipSummary, ProgramBrief } from "@/lib/api";
import StatCard from "@/components/StatCard";
import RiskBar from "@/components/charts/RiskBar";
import {
  formatCurrency,
  formatNumber,
  riskBadgeClass,
} from "@/lib/utils";

export default function CipDetailPage() {
  const { cipcode } = useParams<{ cipcode: string }>();
  const [summary, setSummary] = useState<CipSummary | null>(null);
  const [programs, setPrograms] = useState<ProgramBrief[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "observed" | "suppressed">("all");

  useEffect(() => {
    if (!cipcode) return;
    api.getCipSummary(cipcode).then(setSummary).catch((e) => setError(e.message));
    api.searchPrograms({ cipcode, limit: "200" }).then(setPrograms).catch(() => {});
  }, [cipcode]);

  if (error) return <div className="text-red-600 p-8">{error}</div>;
  if (!summary) return <div className="p-8 text-gray-500">Loading...</div>;

  const filtered = programs.filter((p) => {
    if (filter === "observed") return !p.earnings_suppressed;
    if (filter === "suppressed") return p.earnings_suppressed;
    return true;
  });

  return (
    <div>
      <Link
        href="/programs"
        className="text-sm text-indigo-600 hover:underline mb-4 inline-block"
      >
        &larr; All Programs
      </Link>

      <h1 className="text-3xl font-bold mb-1">
        {summary.cipcode} &mdash; {summary.cip_desc.replace(/\.$/, "")}
      </h1>
      <p className="text-gray-500 mb-6">
        {formatNumber(summary.total_programs)} programs at{" "}
        {formatNumber(summary.with_earnings)} institutions with earnings data
      </p>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Programs" value={formatNumber(summary.total_programs)} />
        <StatCard
          label="Median Earnings"
          value={summary.median_earnings ? formatCurrency(summary.median_earnings) : "N/A"}
        />
        <StatCard
          label="% Passing EP Test"
          value={summary.pct_passing != null ? `${summary.pct_passing.toFixed(0)}%` : "N/A"}
          className={
            summary.pct_passing != null
              ? summary.pct_passing >= 70
                ? "text-green-600"
                : summary.pct_passing >= 40
                  ? "text-amber-600"
                  : "text-red-600"
              : ""
          }
        />
        <StatCard
          label="% High Risk"
          value={summary.pct_high_risk != null ? `${summary.pct_high_risk.toFixed(0)}%` : "N/A"}
          className={
            summary.pct_high_risk != null && summary.pct_high_risk > 50
              ? "text-red-600"
              : ""
          }
        />
      </div>

      {/* Risk bar */}
      <div className="bg-white rounded-xl p-4 shadow-sm border mb-6">
        <RiskBar
          distribution={summary.risk_distribution}
          riskOnly
          title="Risk Distribution"
        />
      </div>

      {/* Programs table */}
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">
            Programs Offering {summary.cipcode}
          </h2>
          <div className="flex gap-1">
            {(["all", "observed", "suppressed"] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium ${
                  filter === f
                    ? "bg-indigo-600 text-white"
                    : "bg-white border text-gray-600 hover:bg-gray-50"
                }`}
              >
                {f === "all" ? "All" : f === "observed" ? "With Earnings" : "Suppressed"}
              </button>
            ))}
          </div>
        </div>


        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="py-2 px-2 font-medium text-gray-600">Institution</th>
                <th className="py-2 px-2 font-medium text-gray-600">State</th>
                <th className="py-2 px-2 font-medium text-gray-600">Credential</th>
                <th className="py-2 px-2 font-medium text-gray-600 text-right">Completions</th>
                <th className="py-2 px-2 font-medium text-gray-600 text-right">Earnings</th>
                <th className="py-2 px-2 font-medium text-gray-600 text-right">
                  <span title="Earnings at 1yr / 2yr / 4yr / 5yr after completion">Trajectory</span>
                </th>
                <th className="py-2 px-2 font-medium text-gray-600 text-right">Margin</th>
                <th className="py-2 px-2 font-medium text-gray-600">Risk</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p, i) => (
                <tr key={`${p.unit_id}-${p.credential_level}-${i}`} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-2 px-2">
                    <Link
                      href={`/institutions/${p.unit_id}`}
                      className="text-indigo-600 hover:underline"
                    >
                      {p.institution}
                    </Link>
                  </td>
                  <td className="py-2 px-2 text-gray-600">{p.state}</td>
                  <td className="py-2 px-2 text-gray-600">{p.credential_desc || "—"}</td>
                  <td className="py-2 px-2 text-right">
                    {p.completions != null ? formatNumber(p.completions) : "—"}
                  </td>
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
                    {p.earnings_margin_pct != null ? (
                      <span className={p.earnings_margin_pct < 0 ? "text-red-600" : "text-green-600"}>
                        {p.earnings_margin_pct >= 0 ? "+" : ""}{p.earnings_margin_pct.toFixed(1)}%
                      </span>
                    ) : "—"}
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
          {filtered.length === 0 && (
            <p className="text-gray-400 text-sm py-4 text-center">
              No programs match this filter.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

