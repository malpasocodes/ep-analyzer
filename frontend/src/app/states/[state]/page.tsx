"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api, StateDetail } from "@/lib/api";
import {
  formatCurrency,
  formatNumber,
  formatPct,
  riskBadgeClass,
} from "@/lib/utils";
import RiskDonut from "@/components/charts/RiskDonut";
import MarginHistogram from "@/components/charts/MarginHistogram";

export default function StateDetailPage() {
  const { state } = useParams<{ state: string }>();
  const [data, setData] = useState<StateDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<string>("margin");

  useEffect(() => {
    if (state)
      api.getState(state).then(setData).catch((e) => setError(e.message));
  }, [state]);

  if (error) return <div className="text-red-600 p-8">{error}</div>;
  if (!data) return <div className="p-8 text-gray-500">Loading...</div>;

  const sorted = [...data.institutions].sort((a, b) => {
    if (sortBy === "margin")
      return (a.earnings_margin_pct ?? -999) - (b.earnings_margin_pct ?? -999);
    if (sortBy === "name") return a.name.localeCompare(b.name);
    if (sortBy === "earnings")
      return (b.median_earnings ?? 0) - (a.median_earnings ?? 0);
    return 0;
  });

  return (
    <div>
      <Link
        href="/states"
        className="text-sm text-indigo-600 hover:underline mb-4 inline-block"
      >
        &larr; All States
      </Link>
      <div className="flex items-baseline gap-4 mb-2">
        <h1 className="text-3xl font-bold">{data.state_name}</h1>
        <span className="text-gray-400">({data.state})</span>
      </div>
      <p className="text-gray-600 mb-8">
        EP Threshold: {formatCurrency(data.threshold)} &middot;{" "}
        {formatNumber(data.institution_count)} institutions
      </p>

      <div className="grid md:grid-cols-2 gap-8 mb-10">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Risk Distribution</h2>
          <RiskDonut data={data.risk_distribution} />
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">
            Earnings Margin Distribution
          </h2>
          {data.margin_histogram.length > 0 ? (
            <MarginHistogram margins={data.margin_histogram} />
          ) : (
            <p className="text-gray-500 text-sm">No margin data available</p>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Institutions</h2>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="margin">Sort by Margin (low to high)</option>
            <option value="name">Sort by Name</option>
            <option value="earnings">Sort by Earnings (high to low)</option>
          </select>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="pb-2 pr-4">Institution</th>
                <th className="pb-2 pr-4">Sector</th>
                <th className="pb-2 pr-4 text-right">Earnings</th>
                <th className="pb-2 pr-4 text-right">Margin</th>
                <th className="pb-2">Risk</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((inst) => (
                <tr key={inst.unit_id} className="border-b last:border-0">
                  <td className="py-2 pr-4">
                    <Link
                      href={`/institutions/${inst.unit_id}`}
                      className="text-indigo-600 hover:underline"
                    >
                      {inst.name}
                    </Link>
                  </td>
                  <td className="py-2 pr-4 text-gray-500">
                    {inst.sector || "—"}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {formatCurrency(inst.median_earnings)}
                  </td>
                  <td className="py-2 pr-4 text-right">
                    {formatPct(inst.earnings_margin_pct)}
                  </td>
                  <td className="py-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${riskBadgeClass(inst.risk_level)}`}
                    >
                      {inst.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
