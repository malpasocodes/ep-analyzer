"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Overview } from "@/lib/api";
import { formatNumber } from "@/lib/utils";
import RiskDonut from "@/components/charts/RiskDonut";
import SectorBreakdown from "@/components/charts/SectorBreakdown";

export default function HomePage() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getOverview().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error)
    return (
      <div className="text-red-600 p-8">
        Failed to load data. Is the API running?{" "}
        <code className="text-sm">uvicorn backend.app.main:app</code>
        <p className="mt-2 text-sm">{error}</p>
      </div>
    );
  if (!data) return <div className="p-8 text-gray-500">Loading...</div>;

  const highRisk = data.risk_distribution["High Risk"] || 0;
  const moderate = data.risk_distribution["Moderate Risk"] || 0;

  return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          Earnings Premium Analyzer
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          How geographic bias in statewide earnings benchmarks affects college
          program accountability under the Earnings Premium test.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <StatCard
          label="Institutions"
          value={formatNumber(data.total_institutions)}
        />
        <StatCard
          label="With Earnings Data"
          value={formatNumber(data.with_earnings)}
        />
        <StatCard
          label="High Risk (Fail EP)"
          value={formatNumber(highRisk)}
          className="text-red-600"
        />
        <StatCard
          label="Near Threshold"
          value={formatNumber(moderate)}
          className="text-amber-600"
        />
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-10">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">Risk Distribution</h2>
          <RiskDonut data={data.risk_distribution} />
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="text-lg font-semibold mb-4">
            Institutions by Sector
          </h2>
          <SectorBreakdown data={data.sector_distribution} />
        </div>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border mb-10">
        <h2 className="text-lg font-semibold mb-4">Program-Level Exposure</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-gray-500">Total Programs Nationwide</p>
            <p className="text-2xl font-bold">
              {formatNumber(data.total_programs)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">
              Assessable (15+ completions)
            </p>
            <p className="text-2xl font-bold">
              {formatNumber(data.assessable_programs)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">States Covered</p>
            <p className="text-2xl font-bold">
              {formatNumber(data.states_covered)}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-indigo-50 rounded-xl p-6 border border-indigo-100 mb-10">
        <h2 className="text-lg font-semibold text-indigo-900 mb-3">
          What Is the Earnings Premium Test?
        </h2>
        <p className="text-sm text-indigo-800 leading-relaxed mb-3">
          Under the One Big Beautiful Bill Act (effective July 2026), college
          programs must demonstrate that graduates earn more than the median
          high school graduate earnings in their state. Programs failing for 2
          out of 3 consecutive years lose Title IV federal aid eligibility.
        </p>
        <p className="text-sm text-indigo-800 leading-relaxed">
          This tool shows that a single statewide benchmark creates geographic
          bias: programs in low-wage regions can fail even when outperforming
          their local labor market, while programs in high-wage metros can pass
          while underperforming locally.{" "}
          <Link
            href="/analysis"
            className="font-medium underline hover:text-indigo-600"
          >
            Explore the reclassification analysis
          </Link>
          .
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <NavCard
          href="/states"
          title="Explore by State"
          description="See risk distributions, margin histograms, and institution lists for each state."
        />
        <NavCard
          href="/institutions"
          title="Institution Lookup"
          description="Search for any institution to see its earnings, risk level, and peer comparison."
        />
        <NavCard
          href="/analysis"
          title="Benchmark Analysis"
          description="Compare statewide vs. local benchmarks and explore sensitivity scenarios."
        />
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  className = "",
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border">
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className={`text-3xl font-bold ${className}`}>{value}</p>
    </div>
  );
}

function NavCard({
  href,
  title,
  description,
}: {
  href: string;
  title: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md hover:border-indigo-300 transition-all"
    >
      <h3 className="font-semibold text-indigo-600 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </Link>
  );
}
