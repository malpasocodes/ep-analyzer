"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  api,
  ReclassificationResult,
  ReclassificationProgram,
  MarginDistribution,
  EarlyVsLate,
  ProgramReclassificationResult,
  ProgramReclassificationProgram,
} from "@/lib/api";
import { formatNumber, formatCurrency, CLASSIFICATION_COLORS } from "@/lib/utils";
import QuadrantScatter from "@/components/charts/QuadrantScatter";
import MarginHistogram from "@/components/charts/MarginHistogram";
import EarningsComparison from "@/components/charts/EarningsComparison";

export default function AnalysisPage() {
  const [tab, setTab] = useState<
    "reclassification" | "programReclass" | "margins" | "earlyLate"
  >("reclassification");

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Benchmark Analysis</h1>
      <p className="text-gray-600 mb-6">
        Explore how benchmark choice affects which programs pass or fail the
        Earnings Premium test.
      </p>

      <div className="bg-indigo-50 rounded-xl p-6 border border-indigo-100 mb-8">
        <h2 className="text-lg font-semibold text-indigo-900 mb-3">
          The Geographic Bias Problem
        </h2>
        <p className="text-sm text-indigo-800 leading-relaxed mb-3">
          The EP test compares every program to a single statewide benchmark
          &mdash; the median earnings of high school graduates in the state. But
          earnings vary dramatically within states. A nursing program in rural
          Appalachia faces the same bar as one in Manhattan.
        </p>
        <p className="text-sm text-indigo-800 leading-relaxed">
          Our analysis shows that many programs fail the statewide benchmark but
          would pass if measured against local (county-level) earnings.
          Conversely, some programs that pass statewide actually underperform
          their local labor market.
        </p>
      </div>

      <div className="flex gap-2 mb-8">
        {[
          { id: "reclassification" as const, label: "Reclassification" },
          { id: "programReclass" as const, label: "Program Reclassification" },
          { id: "margins" as const, label: "Margin Distribution" },
          { id: "earlyLate" as const, label: "Early vs. Late" },
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

      {tab === "reclassification" && <ReclassificationTab />}
      {tab === "programReclass" && <ProgramReclassificationTab />}
      {tab === "margins" && <MarginTab />}
      {tab === "earlyLate" && <EarlyLateTab />}
    </div>
  );
}

const QUADRANT_TABS = ["Pass Both", "Fail Both", "Pass Local Only", "Pass State Only"] as const;

function ReclassificationTab() {
  const [state, setState] = useState("CA");
  const [inequality, setInequality] = useState(0.5);
  const [metric, setMetric] = useState<"P6" | "P10">("P10");
  const [data, setData] = useState<ReclassificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [quadrantTab, setQuadrantTab] = useState<string>("Pass Both");
  const [sortCol, setSortCol] = useState<string>("earnings");
  const [sortAsc, setSortAsc] = useState(false);
  const [sourceFilter, setSourceFilter] = useState<"all" | "real" | "synthetic">("all");

  const handleSort = (col: string) => {
    if (sortCol === col) {
      setSortAsc(!sortAsc);
    } else {
      setSortCol(col);
      setSortAsc(true);
    }
  };

  const sortPrograms = (programs: ReclassificationProgram[]) => {
    return [...programs].sort((a, b) => {
      let aVal: string | number = 0;
      let bVal: string | number = 0;
      switch (sortCol) {
        case "name": aVal = a.name; bVal = b.name; break;
        case "county": aVal = a.county || ""; bVal = b.county || ""; break;
        case "earnings": aVal = a.earnings; bVal = b.earnings; break;
        case "state_benchmark": aVal = a.state_benchmark; bVal = b.state_benchmark; break;
        case "local_benchmark": aVal = a.local_benchmark; bVal = b.local_benchmark; break;
        case "benchmark_source": aVal = a.benchmark_source; bVal = b.benchmark_source; break;
      }
      if (aVal < bVal) return sortAsc ? -1 : 1;
      if (aVal > bVal) return sortAsc ? 1 : -1;
      return 0;
    });
  };

  const columns = [
    { key: "name", label: "Institution" },
    { key: "county", label: "County" },
    { key: "earnings", label: "Earnings" },
    { key: "state_benchmark", label: "State Benchmark" },
    { key: "local_benchmark", label: "Local Benchmark" },
    { key: "benchmark_source", label: "Source" },
  ];

  const run = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getReclassification(state, inequality, metric);
      setData(result);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [state, inequality, metric]);

  useEffect(() => {
    run();
  }, [run]);

  return (
    <div>
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
        <h2 className="text-lg font-semibold mb-4">
          Statewide vs. Local Benchmark Comparison
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          This analysis takes real institutions and their real earnings, then
          compares outcomes using local county-level benchmarks (from Census ACS)
          versus the single statewide threshold. Where county data is unavailable,
          synthetic local benchmarks fill the gap.
        </p>
        <p className="text-xs text-gray-500 mb-4">
          Note: County benchmarks use Census ACS B20004 (workers aged 25+),
          while the EP test targets younger graduates. This age difference
          inflates local benchmarks somewhat, so divergence counts represent an
          upper bound.
        </p>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="text-sm text-gray-500 block mb-1">State</label>
            <input
              type="text"
              value={state}
              onChange={(e) => setState(e.target.value.toUpperCase().slice(0, 2))}
              className="border rounded-lg px-3 py-2 w-20 text-sm"
            />
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="text-sm text-gray-500 block mb-1">
              Local Inequality: {inequality.toFixed(2)}
            </label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={inequality}
              onChange={(e) => setInequality(Number(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-400">
              <span>Low variation</span>
              <span>High variation</span>
            </div>
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">Earnings Metric</label>
            <div className="flex gap-1">
              {([
                { id: "P10" as const, label: "10-Year" },
                { id: "P6" as const, label: "6-Year" },
              ]).map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => setMetric(opt.id)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    metric === opt.id
                      ? "bg-indigo-600 text-white"
                      : "bg-white border text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading...</p>}
      {data && !loading && (
        (() => {
          const filteredPrograms = data.programs.filter(
            (p) => sourceFilter === "all" || p.benchmark_source === sourceFilter
          );
          const counts = {
            pass_both: filteredPrograms.filter(p => p.classification === "Pass Both").length,
            fail_both: filteredPrograms.filter(p => p.classification === "Fail Both").length,
            pass_local_only: filteredPrograms.filter(p => p.classification === "Pass Local Only").length,
            pass_state_only: filteredPrograms.filter(p => p.classification === "Pass State Only").length,
          };
          const realCount = filteredPrograms.filter(p => p.benchmark_source === "real").length;
          const syntheticCount = filteredPrograms.filter(p => p.benchmark_source === "synthetic").length;

          return <>
          {/* Source filter */}
          <div className="flex items-center gap-3 mb-6">
            <span className="text-sm font-medium text-gray-600">Source:</span>
            <div className="flex gap-1">
              {([
                { id: "all" as const, label: "All" },
                { id: "real" as const, label: "Real" },
                { id: "synthetic" as const, label: "Synthetic" },
              ]).map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => setSourceFilter(opt.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    sourceFilter === opt.id
                      ? "bg-indigo-600 text-white"
                      : "bg-white border text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Classification summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[
              {
                label: "Pass Both",
                value: counts.pass_both,
                color: "text-green-600",
              },
              {
                label: "Fail Both",
                value: counts.fail_both,
                color: "text-red-600",
              },
              {
                label: "Pass Local Only",
                value: counts.pass_local_only,
                color: "text-blue-600",
                desc: "Would pass with local benchmark",
              },
              {
                label: "Pass State Only",
                value: counts.pass_state_only,
                color: "text-amber-600",
                desc: "Would fail with local benchmark",
              },
            ].map((item) => (
              <div key={item.label} className="bg-white rounded-xl p-4 shadow-sm border">
                <p className="text-sm text-gray-500">{item.label}</p>
                <p className={`text-3xl font-bold ${item.color}`}>
                  {item.value}
                </p>
                {item.desc && (
                  <p className="text-xs text-gray-400 mt-1">{item.desc}</p>
                )}
              </div>
            ))}
          </div>

          {/* Data source indicator */}
          <div className="bg-gray-50 rounded-xl p-4 border mb-6">
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
                <span>
                  <strong>{realCount}</strong> real county benchmarks
                  <span className="text-gray-400 ml-1">(Census ACS B20004, ages 25+)</span>
                </span>
              </div>
              {syntheticCount > 0 && (
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-gray-400" />
                  <span>
                    <strong>{syntheticCount}</strong> synthetic
                    <span className="text-gray-400 ml-1">(no county match)</span>
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Narratives */}
          {counts.pass_local_only > 0 && (
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-100 mb-6">
              <p className="text-sm text-blue-800">
                <strong>{counts.pass_local_only} institution{counts.pass_local_only !== 1 ? "s" : ""}</strong>{" "}
                fail the statewide EP test but would pass if measured against
                local labor market conditions. These programs are penalized for
                their geography, not their quality.
              </p>
            </div>
          )}
          {counts.pass_state_only > 0 && (
            <div className="bg-amber-50 rounded-xl p-4 border border-amber-100 mb-6">
              <p className="text-sm text-amber-800">
                <strong>{counts.pass_state_only} institution{counts.pass_state_only !== 1 ? "s" : ""}</strong>{" "}
                pass the statewide EP test but their graduates earn less than
                high school graduates in their own county. The statewide
                benchmark masks local underperformance.
              </p>
            </div>
          )}

          {/* Quadrant scatter */}
          <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
            <h3 className="text-md font-semibold mb-2">
              Quadrant Plot: Distance from State vs. Local Benchmarks
            </h3>
            <p className="text-xs text-gray-500 mb-4">
              Each dot is an institution. The axes show how far earnings are from
              each benchmark. Institutions in the upper-left quadrant (blue) pass
              locally but fail statewide.
            </p>
            <QuadrantScatter programs={filteredPrograms} />
          </div>

          {/* Institution list tabs */}
          <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
            <h3 className="text-md font-semibold mb-4">Institutions by Classification</h3>
            <div className="flex flex-wrap gap-1 mb-4 border-b">
              {QUADRANT_TABS.map((label) => {
                const count = filteredPrograms.filter((p) => p.classification === label).length;
                const color = CLASSIFICATION_COLORS[label as keyof typeof CLASSIFICATION_COLORS];
                const isActive = quadrantTab === label;
                return (
                  <button
                    key={label}
                    onClick={() => setQuadrantTab(label)}
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive ? "text-gray-900" : "text-gray-500 hover:text-gray-700"
                    }`}
                    style={isActive ? { borderBottom: `2px solid ${color}` } : {}}
                  >
                    {label} ({count})
                  </button>
                );
              })}
            </div>
            {(() => {
              const filtered = filteredPrograms.filter((p) => p.classification === quadrantTab);
              if (filtered.length === 0) {
                return (
                  <p className="text-sm text-gray-400 py-4">
                    No institutions in this category.
                  </p>
                );
              }
              const sorted = sortPrograms(filtered);
              return (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        {columns.map((col) => (
                          <th
                            key={col.key}
                            onClick={() => handleSort(col.key)}
                            className="text-left py-2 px-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900 select-none"
                          >
                            {col.label}
                            {sortCol === col.key && (
                              <span className="ml-1">{sortAsc ? "↑" : "↓"}</span>
                            )}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {sorted.map((p) => (
                        <tr key={p.unit_id} className="border-b last:border-0 hover:bg-gray-50">
                          <td className="py-2 px-3 font-medium">
                            <Link
                              href={`/institutions/${p.unit_id}`}
                              className="text-indigo-600 hover:underline"
                            >
                              {p.name}
                            </Link>
                          </td>
                          <td className="py-2 px-3 text-gray-600">{p.county || "—"}</td>
                          <td className="py-2 px-3">{formatCurrency(p.earnings)}</td>
                          <td className="py-2 px-3">{formatCurrency(p.state_benchmark)}</td>
                          <td className="py-2 px-3">{formatCurrency(p.local_benchmark)}</td>
                          <td className="py-2 px-3">
                            <span
                              className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                                p.benchmark_source === "real"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-600"
                              }`}
                            >
                              {p.benchmark_source}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              );
            })()}
          </div>

          {/* Legend */}
          <div className="flex flex-wrap gap-4 text-sm">
            {Object.entries(CLASSIFICATION_COLORS).map(([label, color]) => (
              <div key={label} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: color }}
                />
                <span>{label}</span>
              </div>
            ))}
          </div>
        </>;
        })()
      )}
    </div>
  );
}

function MarginTab() {
  const [state, setState] = useState("");
  const [data, setData] = useState<MarginDistribution | null>(null);

  useEffect(() => {
    api
      .getMargins(state ? { state: state.toUpperCase() } : {})
      .then(setData)
      .catch(() => setData(null));
  }, [state]);

  return (
    <div>
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
        <h2 className="text-lg font-semibold mb-4">
          How Close to the Cliff?
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          The margin distribution shows how far each institution&apos;s earnings
          are above or below their state threshold. Institutions clustered near
          0% are one bad cohort away from failing.
        </p>
        <div>
          <label className="text-sm text-gray-500 block mb-1">
            Filter by State (leave blank for national)
          </label>
          <input
            type="text"
            value={state}
            onChange={(e) => setState(e.target.value.toUpperCase().slice(0, 2))}
            placeholder="e.g., CA"
            className="border rounded-lg px-3 py-2 w-24 text-sm"
          />
        </div>
      </div>

      {data && (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-xl p-4 shadow-sm border">
              <p className="text-sm text-gray-500">Total Institutions</p>
              <p className="text-2xl font-bold">
                {formatNumber(data.total_count)}
              </p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border">
              <p className="text-sm text-gray-500">
                Near Threshold (0-20%)
              </p>
              <p className="text-2xl font-bold text-amber-600">
                {formatNumber(data.near_threshold_count)}
              </p>
            </div>
            <div className="bg-white rounded-xl p-4 shadow-sm border">
              <p className="text-sm text-gray-500">Below Threshold</p>
              <p className="text-2xl font-bold text-red-600">
                {formatNumber(data.risk_counts["High Risk"] || 0)}
              </p>
            </div>
          </div>

          {data.margins.length > 0 && (
            <div className="bg-white rounded-xl p-6 shadow-sm border">
              <MarginHistogram margins={data.margins} />
            </div>
          )}
        </>
      )}
    </div>
  );
}

function ProgramReclassificationTab() {
  const [state, setState] = useState("CA");
  const [inequality, setInequality] = useState(0.5);
  const [data, setData] = useState<ProgramReclassificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [progQuadrantTab, setProgQuadrantTab] = useState<string>("Pass Both");
  const [progSortCol, setProgSortCol] = useState<string>("earnings");
  const [progSortAsc, setProgSortAsc] = useState(false);

  const handleProgSort = (col: string) => {
    if (progSortCol === col) {
      setProgSortAsc(!progSortAsc);
    } else {
      setProgSortCol(col);
      setProgSortAsc(true);
    }
  };

  const sortProgs = (programs: ProgramReclassificationProgram[]) => {
    return [...programs].sort((a, b) => {
      let aVal: string | number = 0;
      let bVal: string | number = 0;
      switch (progSortCol) {
        case "cip_desc": aVal = a.cip_desc || ""; bVal = b.cip_desc || ""; break;
        case "institution": aVal = a.institution || ""; bVal = b.institution || ""; break;
        case "credential_desc": aVal = a.credential_desc || ""; bVal = b.credential_desc || ""; break;
        case "earnings": aVal = a.earnings; bVal = b.earnings; break;
        case "state_benchmark": aVal = a.state_benchmark; bVal = b.state_benchmark; break;
        case "local_benchmark": aVal = a.local_benchmark; bVal = b.local_benchmark; break;
        case "benchmark_source": aVal = a.benchmark_source; bVal = b.benchmark_source; break;
      }
      if (aVal < bVal) return progSortAsc ? -1 : 1;
      if (aVal > bVal) return progSortAsc ? 1 : -1;
      return 0;
    });
  };

  const progColumns = [
    { key: "cip_desc", label: "Program" },
    { key: "institution", label: "Institution" },
    { key: "credential_desc", label: "Credential" },
    { key: "earnings", label: "Earnings" },
    { key: "state_benchmark", label: "State Benchmark" },
    { key: "local_benchmark", label: "Local Benchmark" },
    { key: "benchmark_source", label: "Source" },
  ];

  const run = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getProgramReclassification(state, inequality);
      setData(result);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [state, inequality]);

  useEffect(() => {
    run();
  }, [run]);

  return (
    <div>
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
        <h2 className="text-lg font-semibold mb-4">
          Program-Level Reclassification
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          The same statewide vs. local benchmark comparison applied at the
          program level. Each program&apos;s earnings are compared against both
          the state threshold and the county-level HS earnings benchmark.
          Only programs with non-suppressed earnings are included.
        </p>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="text-sm text-gray-500 block mb-1">State</label>
            <input
              type="text"
              value={state}
              onChange={(e) => setState(e.target.value.toUpperCase().slice(0, 2))}
              className="border rounded-lg px-3 py-2 w-20 text-sm"
            />
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="text-sm text-gray-500 block mb-1">
              Local Inequality: {inequality.toFixed(2)}
            </label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={inequality}
              onChange={(e) => setInequality(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading...</p>}
      {data && !loading && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[
              { label: "Pass Both", value: data.pass_both, color: "text-green-600" },
              { label: "Fail Both", value: data.fail_both, color: "text-red-600" },
              { label: "Pass Local Only", value: data.pass_local_only, color: "text-blue-600", desc: "Penalized by geography" },
              { label: "Pass State Only", value: data.pass_state_only, color: "text-amber-600", desc: "Masked underperformance" },
            ].map((item) => (
              <div key={item.label} className="bg-white rounded-xl p-4 shadow-sm border">
                <p className="text-sm text-gray-500">{item.label}</p>
                <p className={`text-3xl font-bold ${item.color}`}>{item.value}</p>
                {item.desc && <p className="text-xs text-gray-400 mt-1">{item.desc}</p>}
              </div>
            ))}
          </div>

          {/* Suppression context */}
          <div className="bg-purple-50 rounded-xl p-4 border border-purple-100 mb-6">
            <p className="text-sm text-purple-800">
              <strong>{formatNumber(data.suppressed)} programs</strong> in {data.state} have
              suppressed earnings and cannot be reclassified.{" "}
              <strong>{formatNumber(data.with_earnings)} of {formatNumber(data.total_programs)}</strong>{" "}
              total programs ({((data.with_earnings / data.total_programs) * 100).toFixed(0)}%)
              are shown here.
            </p>
          </div>

          {/* Narratives */}
          {data.pass_local_only > 0 && (
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-100 mb-6">
              <p className="text-sm text-blue-800">
                <strong>{data.pass_local_only} program{data.pass_local_only !== 1 ? "s" : ""}</strong>{" "}
                fail the statewide EP test but would pass with local benchmarks.
                These programs are penalized for their geography, not quality.
              </p>
            </div>
          )}
          {data.pass_state_only > 0 && (
            <div className="bg-amber-50 rounded-xl p-4 border border-amber-100 mb-6">
              <p className="text-sm text-amber-800">
                <strong>{data.pass_state_only} program{data.pass_state_only !== 1 ? "s" : ""}</strong>{" "}
                pass statewide but fail locally. The statewide benchmark masks
                underperformance relative to local labor markets.
              </p>
            </div>
          )}

          {/* Quadrant scatter reused */}
          <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
            <h3 className="text-md font-semibold mb-2">
              Program Quadrant: Distance from State vs. Local Benchmarks
            </h3>
            <p className="text-xs text-gray-500 mb-4">
              Each dot is a program. Programs in the upper-left pass locally but
              fail statewide.
            </p>
            <QuadrantScatter programs={data.programs} />
          </div>

          {/* Programs by classification tabs */}
          <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
            <h3 className="text-md font-semibold mb-4">Programs by Classification</h3>
            <div className="flex flex-wrap gap-1 mb-4 border-b">
              {QUADRANT_TABS.map((label) => {
                const count = data.programs.filter((p) => p.classification === label).length;
                const color = CLASSIFICATION_COLORS[label as keyof typeof CLASSIFICATION_COLORS];
                const isActive = progQuadrantTab === label;
                return (
                  <button
                    key={label}
                    onClick={() => setProgQuadrantTab(label)}
                    className={`px-3 py-2 text-sm font-medium transition-colors ${
                      isActive ? "text-gray-900" : "text-gray-500 hover:text-gray-700"
                    }`}
                    style={isActive ? { borderBottom: `2px solid ${color}` } : {}}
                  >
                    {label} ({count})
                  </button>
                );
              })}
            </div>
            {(() => {
              const filtered = data.programs.filter((p) => p.classification === progQuadrantTab);
              if (filtered.length === 0) {
                return (
                  <p className="text-sm text-gray-400 py-4">
                    No programs in this category.
                  </p>
                );
              }
              const sorted = sortProgs(filtered);
              return (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        {progColumns.map((col) => (
                          <th
                            key={col.key}
                            onClick={() => handleProgSort(col.key)}
                            className="text-left py-2 px-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900 select-none"
                          >
                            {col.label}
                            {progSortCol === col.key && (
                              <span className="ml-1">{progSortAsc ? "↑" : "↓"}</span>
                            )}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {sorted.map((p, i) => (
                        <tr key={`${p.unit_id}-${p.cipcode}-${i}`} className="border-b last:border-0 hover:bg-gray-50">
                          <td className="py-2 px-3 font-medium">
                            <Link
                              href={`/programs/${p.cipcode}`}
                              className="text-indigo-600 hover:underline"
                            >
                              {p.cip_desc || p.cipcode}
                            </Link>
                          </td>
                          <td className="py-2 px-3">
                            <Link
                              href={`/institutions/${p.unit_id}`}
                              className="text-indigo-600 hover:underline"
                            >
                              {p.institution}
                            </Link>
                          </td>
                          <td className="py-2 px-3 text-gray-600">{p.credential_desc || "—"}</td>
                          <td className="py-2 px-3">{formatCurrency(p.earnings)}</td>
                          <td className="py-2 px-3">{formatCurrency(p.state_benchmark)}</td>
                          <td className="py-2 px-3">{formatCurrency(p.local_benchmark)}</td>
                          <td className="py-2 px-3">
                            <span
                              className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                                p.benchmark_source === "real"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-600"
                              }`}
                            >
                              {p.benchmark_source}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              );
            })()}
          </div>

          {/* Data source */}
          <div className="bg-gray-50 rounded-xl p-4 border text-sm">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
                <span><strong>{data.real_benchmark_count}</strong> real county benchmarks</span>
              </div>
              {data.synthetic_benchmark_count > 0 && (
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-gray-400" />
                  <span><strong>{data.synthetic_benchmark_count}</strong> synthetic</span>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function EarlyLateTab() {
  const [state, setState] = useState("");
  const [data, setData] = useState<EarlyVsLate | null>(null);

  useEffect(() => {
    api
      .getEarlyVsLate(state || undefined)
      .then(setData)
      .catch(() => setData(null));
  }, [state]);

  const changed = data?.institutions.filter((i) => i.changed) || [];

  return (
    <div>
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-6">
        <h2 className="text-lg font-semibold mb-4">
          Early vs. Late Earnings
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Some programs look bad at 6 years but recover by 10 years. If the EP
          test uses early earnings, these programs are penalized for a timing
          issue, not a quality issue.
        </p>
        <div>
          <label className="text-sm text-gray-500 block mb-1">
            Filter by State
          </label>
          <input
            type="text"
            value={state}
            onChange={(e) => setState(e.target.value.toUpperCase().slice(0, 2))}
            placeholder="e.g., NY"
            className="border rounded-lg px-3 py-2 w-24 text-sm"
          />
        </div>
      </div>

      {data && (
        <>
          {changed.length > 0 && (
            <div className="bg-amber-50 rounded-xl p-4 border border-amber-100 mb-6">
              <p className="text-sm text-amber-800">
                <strong>{changed.length} institution{changed.length !== 1 ? "s" : ""}</strong>{" "}
                would have a different pass/fail outcome depending on whether 6-year
                or 10-year earnings are used. These represent programs where timing
                matters more than quality.
              </p>
            </div>
          )}

          <div className="bg-white rounded-xl p-6 shadow-sm border">
            <p className="text-xs text-gray-500 mb-4">
              Each dot is an institution. Dots above the diagonal earn more at 10
              years than at 6 years. Amber dots change pass/fail status between the
              two time horizons.
            </p>
            <EarningsComparison institutions={data.institutions} />
          </div>
        </>
      )}
    </div>
  );
}
