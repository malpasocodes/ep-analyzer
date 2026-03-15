"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, StateSummary } from "@/lib/api";
import { formatCurrency, formatNumber, riskBadgeClass } from "@/lib/utils";

export default function StatesPage() {
  const [states, setStates] = useState<StateSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getStates().then(setStates).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="text-red-600 p-8">{error}</div>;
  if (!states.length)
    return <div className="p-8 text-gray-500">Loading...</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">State Analysis</h1>
      <p className="text-gray-600 mb-8">
        Select a state to see its EP threshold, risk distribution, and
        institution details.
      </p>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {states.map((s) => {
          const hr = s.risk_distribution["High Risk"] || 0;
          const total = s.institution_count;
          const hrPct = total > 0 ? ((hr / total) * 100).toFixed(0) : "0";
          return (
            <Link
              key={s.state}
              href={`/states/${s.state}`}
              className="bg-white rounded-lg p-4 border hover:shadow-md hover:border-indigo-300 transition-all"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <span className="text-lg font-semibold">{s.state_name}</span>
                  <span className="text-sm text-gray-400 ml-2">
                    ({s.state})
                  </span>
                </div>
                <span className="text-xs bg-gray-100 rounded px-2 py-1">
                  {formatNumber(s.institution_count)} inst.
                </span>
              </div>
              <p className="text-sm text-gray-500">
                Threshold: {formatCurrency(s.threshold)}
              </p>
              {hr > 0 && (
                <p className="text-sm text-red-600 mt-1">
                  {hr} High Risk ({hrPct}%)
                </p>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
