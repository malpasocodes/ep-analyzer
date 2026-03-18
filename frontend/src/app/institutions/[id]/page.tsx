"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  api,
  InstitutionDetail,
  PeerInstitution,
  InstitutionProgramsResponse,
  InstitutionSimulationResponse,
} from "@/lib/api";
import {
  formatCurrency,
  formatNumber,
  formatPct,
  riskBadgeClass,
} from "@/lib/utils";

export default function InstitutionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<InstitutionDetail | null>(null);
  const [peers, setPeers] = useState<PeerInstitution[]>([]);
  const [programData, setProgramData] = useState<InstitutionProgramsResponse | null>(null);
  const [simData, setSimData] = useState<InstitutionSimulationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const unitId = Number(id);
    api.getInstitution(unitId).then(setData).catch((e) => setError(e.message));
    api.getPeers(unitId).then(setPeers).catch(() => {});
    api.getInstitutionPrograms(unitId).then(setProgramData).catch(() => {});
    api.getInstitutionSimulation(unitId).then(setSimData).catch(() => {});
  }, [id]);

  if (error) return <div className="text-red-600 p-8">{error}</div>;
  if (!data) return <div className="p-8 text-gray-500">Loading...</div>;

  const marginColor =
    data.earnings_margin_pct != null
      ? data.earnings_margin_pct < 0
        ? "text-red-600"
        : data.earnings_margin_pct < 20
          ? "text-amber-600"
          : "text-green-600"
      : "";

  return (
    <div>
      <Link
        href="/institutions"
        className="text-sm text-indigo-600 hover:underline mb-4 inline-block"
      >
        &larr; Search
      </Link>

      <div className="flex items-start gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold">{data.name}</h1>
          <p className="text-gray-500">
            {data.state} &middot; {data.sector || "Unknown Sector"}
          </p>
        </div>
        <span
          className={`text-sm px-3 py-1 rounded-full mt-1 ${riskBadgeClass(data.risk_level)}`}
        >
          {data.risk_level}
        </span>
      </div>

      {/* Key metrics */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard label="Median Earnings" value={formatCurrency(data.median_earnings)} />
        <MetricCard label="State Threshold" value={formatCurrency(data.threshold)} />
        <MetricCard
          label="Earnings Margin"
          value={formatPct(data.earnings_margin_pct)}
          className={marginColor}
        />
        <MetricCard
          label="Enrollment"
          value={data.enrollment != null ? formatNumber(data.enrollment) : "N/A"}
        />
      </div>

      {/* Earnings gauge */}
      {data.median_earnings != null && data.threshold != null && (
        <div className="bg-white rounded-xl p-6 shadow-sm border mb-8">
          <h2 className="text-lg font-semibold mb-4">
            Earnings vs. Threshold
          </h2>
          <EarningsGauge
            earnings={data.median_earnings}
            threshold={data.threshold}
          />
        </div>
      )}

      {/* P6 vs P10 */}
      {data.earnings_p6 != null && data.earnings_p10 != null && (
        <div className="bg-white rounded-xl p-6 shadow-sm border mb-8">
          <h2 className="text-lg font-semibold mb-4">
            Early vs. Late Earnings
          </h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-500">
                6-Year (Early Career)
              </p>
              <p className="text-2xl font-bold">
                {formatCurrency(data.earnings_p6)}
              </p>
              {data.threshold && (
                <p
                  className={`text-sm ${data.earnings_p6 >= data.threshold ? "text-green-600" : "text-red-600"}`}
                >
                  {data.earnings_p6 >= data.threshold ? "PASS" : "FAIL"} EP test
                </p>
              )}
            </div>
            <div>
              <p className="text-sm text-gray-500">
                10-Year (Mid Career)
              </p>
              <p className="text-2xl font-bold">
                {formatCurrency(data.earnings_p10)}
              </p>
              {data.threshold && (
                <p
                  className={`text-sm ${data.earnings_p10 >= data.threshold ? "text-green-600" : "text-red-600"}`}
                >
                  {data.earnings_p10 >= data.threshold ? "PASS" : "FAIL"} EP test
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Additional details */}
      <div className="grid sm:grid-cols-2 gap-4 mb-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-3">Institution Details</h2>
          <dl className="space-y-2 text-sm">
            <Row label="Graduation Rate" value={data.graduation_rate != null ? `${data.graduation_rate.toFixed(0)}%` : "N/A"} />
            <Row label="Cost" value={formatCurrency(data.cost)} />
            <Row label="Total Programs" value={data.total_programs != null ? formatNumber(data.total_programs) : "N/A"} />
            <Row label="Assessable Programs" value={data.assessable_programs != null ? formatNumber(data.assessable_programs) : "N/A"} />
            <Row label="Total Completions" value={data.total_completions != null ? formatNumber(data.total_completions) : "N/A"} />
          </dl>
        </div>

        {/* Peers */}
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-3">
            Peers ({data.state}, {data.sector || "same sector"})
          </h2>
          {peers.length === 0 ? (
            <p className="text-sm text-gray-500">No peers found</p>
          ) : (
            <div className="space-y-2 text-sm max-h-64 overflow-y-auto">
              {peers.map((p) => (
                <div
                  key={p.unit_id}
                  className="flex justify-between items-center py-1 border-b last:border-0"
                >
                  <Link
                    href={`/institutions/${p.unit_id}`}
                    className="text-indigo-600 hover:underline truncate mr-2"
                  >
                    {p.name}
                  </Link>
                  <div className="flex items-center gap-2 shrink-0">
                    <span>{formatPct(p.earnings_margin_pct)}</span>
                    <span
                      className={`text-xs px-1.5 py-0.5 rounded-full ${riskBadgeClass(p.risk_level)}`}
                    >
                      {p.risk_level.replace(" Risk", "")}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Programs at this institution */}
      {programData && programData.total_programs > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-sm border mb-8">
          <h2 className="text-lg font-semibold mb-2">
            Programs ({programData.total_programs})
          </h2>
          <div className="flex gap-4 text-sm text-gray-500 mb-4">
            <span>{programData.with_earnings} with earnings</span>
            <span className="text-purple-600">{programData.suppressed} suppressed</span>
          </div>

          {/* Simulation summary if available */}
          {simData && (
            <div className="bg-purple-50 rounded-lg p-3 border border-purple-100 mb-4">
              <p className="text-sm text-purple-800">
                <strong>Simulation:</strong> Of {simData.summary.estimable} estimable
                suppressed programs, {simData.summary.estimated_high_risk} are estimated
                High Risk (P(pass) avg: {simData.summary.prob_pass_state_mean != null
                  ? `${(simData.summary.prob_pass_state_mean * 100).toFixed(0)}%`
                  : "N/A"}).
              </p>
            </div>
          )}

          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-white">
                <tr className="border-b text-left">
                  <th className="py-2 px-2 font-medium text-gray-600">Program</th>
                  <th className="py-2 px-2 font-medium text-gray-600">Credential</th>
                  <th className="py-2 px-2 font-medium text-gray-600 text-right">Earnings</th>
                  <th className="py-2 px-2 font-medium text-gray-600">Risk</th>
                </tr>
              </thead>
              <tbody>
                {programData.programs.map((p, i) => {
                  const sim = simData?.programs.find(
                    (s) => s.cipcode === p.cipcode && s.credential_level === p.credential_level
                  );
                  return (
                    <tr key={`${p.cipcode}-${p.credential_level}-${i}`} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="py-1.5 px-2">
                        <Link
                          href={`/programs/${p.cipcode}`}
                          className="text-indigo-600 hover:underline text-xs"
                        >
                          {p.cip_desc.replace(/\.$/, "").slice(0, 40)}
                        </Link>
                      </td>
                      <td className="py-1.5 px-2 text-gray-500 text-xs">
                        {p.credential_desc || "—"}
                      </td>
                      <td className="py-1.5 px-2 text-right text-xs">
                        {p.program_earnings != null ? (
                          formatCurrency(p.program_earnings)
                        ) : sim && sim.estimated_earnings != null ? (
                          <span className="text-purple-600" title={`Simulated: ${formatCurrency(sim.earnings_ci_low)}–${formatCurrency(sim.earnings_ci_high)}, P(pass)=${sim.prob_pass_state != null ? (sim.prob_pass_state * 100).toFixed(0) + "%" : "?"}`}>
                            ~{formatCurrency(sim.estimated_earnings)}
                          </span>
                        ) : (
                          <span className="text-purple-400 text-xs">suppressed</span>
                        )}
                      </td>
                      <td className="py-1.5 px-2">
                        <span className={`text-xs px-1.5 py-0.5 rounded-full ${riskBadgeClass(p.risk_level)}`}>
                          {p.risk_level.replace(" Risk", "")}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({
  label,
  value,
  className = "",
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${className}`}>{value}</p>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}

function EarningsGauge({
  earnings,
  threshold,
}: {
  earnings: number;
  threshold: number;
}) {
  const maxVal = Math.max(earnings, threshold) * 1.3;
  const earningsPct = (earnings / maxVal) * 100;
  const thresholdPct = (threshold / maxVal) * 100;
  const passes = earnings >= threshold;

  return (
    <div>
      <div className="relative h-8 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`absolute top-0 left-0 h-full rounded-full ${passes ? "bg-green-400" : "bg-red-400"}`}
          style={{ width: `${earningsPct}%` }}
        />
        <div
          className="absolute top-0 h-full w-0.5 bg-gray-800"
          style={{ left: `${thresholdPct}%` }}
        />
      </div>
      <div className="flex justify-between mt-2 text-xs text-gray-500">
        <span>$0</span>
        <span
          className="absolute"
          style={{ left: `${thresholdPct}%`, position: "relative" }}
        >
          Threshold: {formatCurrency(threshold)}
        </span>
        <span>{formatCurrency(maxVal)}</span>
      </div>
      <p className={`text-center mt-3 font-semibold ${passes ? "text-green-600" : "text-red-600"}`}>
        {passes ? "PASSES" : "FAILS"} the Earnings Premium test by{" "}
        {formatCurrency(Math.abs(earnings - threshold))}
      </p>
    </div>
  );
}
