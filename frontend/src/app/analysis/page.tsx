"use client";

import { useEffect, useState, useCallback } from "react";
import {
  api,
  ReclassificationResult,
  MarginDistribution,
  EarlyVsLate,
} from "@/lib/api";
import { formatNumber, CLASSIFICATION_COLORS } from "@/lib/utils";
import QuadrantScatter from "@/components/charts/QuadrantScatter";
import MarginHistogram from "@/components/charts/MarginHistogram";
import EarningsComparison from "@/components/charts/EarningsComparison";

export default function AnalysisPage() {
  const [tab, setTab] = useState<
    "reclassification" | "margins" | "earlyLate"
  >("reclassification");

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Benchmark Analysis</h1>
      <p className="text-gray-600 mb-6">
        Explore how benchmark choice affects which programs pass or fail the
        Earnings Premium test.
      </p>

      <div className="flex gap-2 mb-8">
        {[
          { id: "reclassification" as const, label: "Reclassification" },
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
      {tab === "margins" && <MarginTab />}
      {tab === "earlyLate" && <EarlyLateTab />}
    </div>
  );
}

function ReclassificationTab() {
  const [state, setState] = useState("CA");
  const [inequality, setInequality] = useState(0.5);
  const [data, setData] = useState<ReclassificationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const run = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getReclassification(state, inequality);
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
          Statewide vs. Local Benchmark Comparison
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          This analysis takes real institutions and their real earnings, then
          compares outcomes using local county-level benchmarks (from Census ACS)
          versus the single statewide threshold. Where county data is unavailable,
          synthetic local benchmarks fill the gap.
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
        </div>
      </div>

      {loading && <p className="text-gray-500">Loading...</p>}
      {data && !loading && (
        <>
          {/* Classification summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[
              {
                label: "Pass Both",
                value: data.pass_both,
                color: "text-green-600",
              },
              {
                label: "Fail Both",
                value: data.fail_both,
                color: "text-red-600",
              },
              {
                label: "Pass Local Only",
                value: data.pass_local_only,
                color: "text-blue-600",
                desc: "Would pass with local benchmark",
              },
              {
                label: "Pass State Only",
                value: data.pass_state_only,
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
                  <strong>{data.real_benchmark_count}</strong> real county benchmarks
                  <span className="text-gray-400 ml-1">(Census ACS B20004, ages 25+)</span>
                </span>
              </div>
              {data.synthetic_benchmark_count > 0 && (
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-gray-400" />
                  <span>
                    <strong>{data.synthetic_benchmark_count}</strong> synthetic
                    <span className="text-gray-400 ml-1">(no county match)</span>
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Narratives */}
          {data.pass_local_only > 0 && (
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-100 mb-6">
              <p className="text-sm text-blue-800">
                <strong>{data.pass_local_only} institution{data.pass_local_only !== 1 ? "s" : ""}</strong>{" "}
                fail the statewide EP test but would pass if measured against
                local labor market conditions. These programs are penalized for
                their geography, not their quality.
              </p>
            </div>
          )}
          {data.pass_state_only > 0 && (
            <div className="bg-amber-50 rounded-xl p-4 border border-amber-100 mb-6">
              <p className="text-sm text-amber-800">
                <strong>{data.pass_state_only} institution{data.pass_state_only !== 1 ? "s" : ""}</strong>{" "}
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
            <QuadrantScatter programs={data.programs} />
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
        </>
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
