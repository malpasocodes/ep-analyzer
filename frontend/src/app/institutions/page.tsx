"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api, InstitutionBrief } from "@/lib/api";
import {
  formatCurrency,
  formatPct,
  riskBadgeClass,
} from "@/lib/utils";

const RISK_OPTIONS = [
  "Very Low Risk",
  "Low Risk",
  "Moderate Risk",
  "High Risk",
  "No Data",
];

export default function InstitutionsPage() {
  const [results, setResults] = useState<InstitutionBrief[]>([]);
  const [search, setSearch] = useState("");
  const [state, setState] = useState("");
  const [risk, setRisk] = useState("");
  const [loading, setLoading] = useState(false);

  const doSearch = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { limit: "100" };
      if (search.length >= 2) params.search = search;
      if (state) params.state = state;
      if (risk) params.risk = risk;
      const data = await api.searchInstitutions(params);
      setResults(data);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [search, state, risk]);

  useEffect(() => {
    const timer = setTimeout(doSearch, 300);
    return () => clearTimeout(timer);
  }, [doSearch]);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Institution Lookup</h1>
      <p className="text-gray-600 mb-6">
        Search by name, filter by state or risk level.
      </p>

      <div className="flex flex-wrap gap-3 mb-6">
        <input
          type="text"
          placeholder="Search institution name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded-lg px-4 py-2 text-sm flex-1 min-w-[200px]"
        />
        <input
          type="text"
          placeholder="State (e.g., CA)"
          value={state}
          onChange={(e) => setState(e.target.value.toUpperCase().slice(0, 2))}
          className="border rounded-lg px-4 py-2 text-sm w-24"
        />
        <select
          value={risk}
          onChange={(e) => setRisk(e.target.value)}
          className="border rounded-lg px-4 py-2 text-sm"
        >
          <option value="">All Risk Levels</option>
          {RISK_OPTIONS.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <p className="text-gray-500">Searching...</p>
      ) : results.length === 0 ? (
        <p className="text-gray-500">
          No results. Try a different search or filter.
        </p>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500 bg-gray-50">
                <th className="p-3">Institution</th>
                <th className="p-3">State</th>
                <th className="p-3">Sector</th>
                <th className="p-3 text-right">Earnings</th>
                <th className="p-3 text-right">Margin</th>
                <th className="p-3">Risk</th>
              </tr>
            </thead>
            <tbody>
              {results.map((inst) => (
                <tr
                  key={inst.unit_id}
                  className="border-b last:border-0 hover:bg-gray-50"
                >
                  <td className="p-3">
                    <Link
                      href={`/institutions/${inst.unit_id}`}
                      className="text-indigo-600 hover:underline"
                    >
                      {inst.name}
                    </Link>
                  </td>
                  <td className="p-3 text-gray-500">{inst.state}</td>
                  <td className="p-3 text-gray-500">{inst.sector || "—"}</td>
                  <td className="p-3 text-right">
                    {formatCurrency(inst.median_earnings)}
                  </td>
                  <td className="p-3 text-right">
                    {formatPct(inst.earnings_margin_pct)}
                  </td>
                  <td className="p-3">
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
      )}
    </div>
  );
}
