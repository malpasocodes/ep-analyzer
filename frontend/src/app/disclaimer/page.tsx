import Link from "next/link";

export default function DisclaimerPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <Link
        href="/"
        className="text-sm text-indigo-600 hover:underline mb-4 inline-block"
      >
        &larr; Home
      </Link>

      <h1 className="text-3xl font-bold mb-6">Research Disclaimer</h1>

      <div className="bg-white rounded-xl p-6 shadow-sm border space-y-4 text-gray-700 leading-relaxed">
        <p>
          This site is an independent research tool for exploring how the
          Earnings Premium test under the One Big Beautiful Bill Act could
          affect higher education programs. It is not affiliated with the U.S.
          Department of Education or any government agency.
        </p>

        <p>
          All analysis is based on publicly available data from the College
          Scorecard, IPEDS, and the Census American Community Survey. Data may
          be incomplete, outdated, or subject to methodological limitations.
          Estimates for privacy-suppressed programs are generated using
          statistical simulation and carry inherent uncertainty.
        </p>

        <p className="font-semibold">
          This site should not be used to make decisions about specific
          institutions or programs, including enrollment, investment,
          accreditation, or policy decisions. Risk classifications shown here
          are analytical approximations and do not represent official
          determinations under any federal or state law.
        </p>

        <p>
          The authors make no warranty regarding the accuracy, completeness, or
          fitness for any particular purpose of the information presented.
        </p>
      </div>
    </div>
  );
}
