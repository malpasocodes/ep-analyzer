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
          Analyzing how the Earnings Premium test in the One Big Beautiful Bill
          Act would affect college programs nationwide.
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
          This tool maps which institutions and sectors are most exposed,
          identifies those near the pass/fail threshold, and explores how
          alternative benchmarks would change outcomes.{" "}
          <Link
            href="/analysis"
            className="font-medium underline hover:text-indigo-600"
          >
            Explore the reclassification analysis
          </Link>
          .
        </p>
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm border mb-10">
        <h2 className="text-lg font-semibold mb-4">
          How Risk Is Calculated
        </h2>
        <p className="text-sm text-gray-700 leading-relaxed mb-4">
          Each institution&apos;s median graduate earnings are compared to the
          state&apos;s high school earnings threshold. The margin determines the
          risk level:
        </p>
        <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 font-mono mb-4">
          earnings margin % = (median earnings &minus; state threshold) &divide; state threshold &times; 100
        </p>
        <div className="overflow-x-auto mb-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="py-2 pr-4 font-semibold text-gray-700">Risk Level</th>
                <th className="py-2 pr-4 font-semibold text-gray-700">Margin %</th>
                <th className="py-2 font-semibold text-gray-700">Meaning</th>
              </tr>
            </thead>
            <tbody className="text-gray-600">
              <tr className="border-b">
                <td className="py-2 pr-4"><span className="inline-block w-3 h-3 rounded-full bg-green-600 mr-2" />Very Low Risk</td>
                <td className="py-2 pr-4">&ge; +50%</td>
                <td className="py-2">Earnings comfortably exceed the benchmark</td>
              </tr>
              <tr className="border-b">
                <td className="py-2 pr-4"><span className="inline-block w-3 h-3 rounded-full bg-blue-500 mr-2" />Low Risk</td>
                <td className="py-2 pr-4">+20% to +49.9%</td>
                <td className="py-2">Solid margin above the benchmark</td>
              </tr>
              <tr className="border-b">
                <td className="py-2 pr-4"><span className="inline-block w-3 h-3 rounded-full bg-amber-500 mr-2" />Moderate Risk</td>
                <td className="py-2 pr-4">0% to +19.9%</td>
                <td className="py-2">Passes but vulnerable to failing</td>
              </tr>
              <tr className="border-b">
                <td className="py-2 pr-4"><span className="inline-block w-3 h-3 rounded-full bg-red-600 mr-2" />High Risk</td>
                <td className="py-2 pr-4">&lt; 0%</td>
                <td className="py-2">Below the benchmark — fails the EP test</td>
              </tr>
              <tr>
                <td className="py-2 pr-4"><span className="inline-block w-3 h-3 rounded-full bg-gray-400 mr-2" />No Data</td>
                <td className="py-2 pr-4">N/A</td>
                <td className="py-2">No reported median earnings</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
          <p className="font-semibold mb-2">Example</p>
          <p className="leading-relaxed">
            Miller-Motte College in Jacksonville, NC has median earnings of
            $31,102 against North Carolina&apos;s threshold of $29,344. The
            margin is ($31,102 &minus; $29,344) &divide; $29,344 = <span className="font-semibold text-amber-600">+6.0%</span>,
            placing it at <span className="font-semibold text-amber-600">Moderate Risk</span>.
            It passes today, but a small drop in earnings could push it below
            the threshold.
          </p>
        </div>
      </div>

      <div className="bg-amber-50 rounded-xl p-5 border border-amber-200 mb-10">
        <p className="text-sm text-amber-800 leading-relaxed">
          <span className="font-semibold">Data note:</span> This analysis
          differs from the actual EP test in two ways. First, it uses
          institution-level earnings rather than program-level earnings.
          Second, it relies on 10-year post-enrollment median earnings from
          the College Scorecard, while DOE will likely use a shorter
          time horizon. Results here estimate institutional exposure but
          will not match exact program-level outcomes. However,
          institution-level earnings measured at 10 years are likely
          higher than program-level earnings measured over a shorter
          period — meaning this analysis represents a best-case
          scenario. Institutions flagged as high risk or near the
          threshold here are likely to face equal or greater exposure
          under the actual test.
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
