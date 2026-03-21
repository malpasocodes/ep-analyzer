import Link from "next/link";

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          Earnings Premium Analyzer
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          How the One Big Beautiful Bill Act&apos;s earnings test could reshape
          higher education &mdash; and why using statewide benchmarks introduces
          geographic bias.
        </p>
      </div>

      {/* Research disclaimer */}
      <div className="bg-amber-50 rounded-xl p-4 border border-amber-200 mb-10">
        <p className="text-sm text-amber-800 leading-relaxed">
          <span className="font-semibold">Research Tool</span> &mdash; This is
          an independent research project, not an official government resource.
          Analysis is based on publicly available data and may be incomplete,
          inaccurate, and subject to methodological limitations. Do not use this site to make
          decisions about specific institutions or programs.{" "}
          <Link
            href="/disclaimer"
            className="font-medium underline hover:text-amber-600"
          >
            Full disclaimer
          </Link>
        </p>
      </div>

      {/* Key questions */}
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-10">
        <h2 className="text-lg font-semibold mb-3">
          Three Questions This Site Answers
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center p-4">
            <div className="text-3xl mb-2">📊</div>
            <h3 className="font-semibold text-gray-900 mb-1">How many programs are at risk?</h3>
            <p className="text-sm text-gray-600">
              213K+ programs analyzed across 424 fields of study,
              with risk levels from reported earnings and Monte Carlo estimates for suppressed data.
            </p>
          </div>
          <div className="text-center p-4">
            <div className="text-3xl mb-2">🏛️</div>
            <h3 className="font-semibold text-gray-900 mb-1">How many institutions are at risk?</h3>
            <p className="text-sm text-gray-600">
              5,700+ institutions assessed. An institution is at risk if any of its programs
              fail the earnings test.
            </p>
          </div>
          <div className="text-center p-4">
            <div className="text-3xl mb-2">🎓</div>
            <h3 className="font-semibold text-gray-900 mb-1">How many students are affected?</h3>
            <p className="text-sm text-gray-600">
              Nearly 5 million annual program completions, broken down by risk level
              of the program they completed.
            </p>
          </div>
        </div>
        <div className="text-center mt-4">
          <Link
            href="/risk-analytics"
            className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors"
          >
            Explore Risk Analytics &rarr;
          </Link>
        </div>
      </div>

      {/* Legislative context */}
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-10">
        <h2 className="text-lg font-semibold mb-3">Background</h2>
        <p className="text-sm text-gray-700 leading-relaxed mb-3">
          The One Big Beautiful Bill Act created a new federal rule for judging college programs.
          For the first time, the law ties eligibility for student loans directly to what graduates earn.
        </p>
        <p className="text-sm text-gray-700 leading-relaxed mb-3">
          The rule is simple. A program passes if its graduates earn at least as much as the median
          high school graduate in the same state. If it fails this test in two out of three consecutive
          years, the program loses access to federal Direct Loans.
        </p>
        <p className="text-sm text-gray-700 leading-relaxed mb-3">
          To put this into practice, the Department of Education is replacing the existing Gainful
          Employment and Financial Value Transparency rules. The old system used debt-to-earnings
          ratios and different penalties for different programs. The new system uses a single
          measure&mdash;the earnings premium&mdash;and applies the same penalty to all programs,
          regardless of institution type.
        </p>
        <p className="text-sm text-gray-700 leading-relaxed">
          For undergraduate programs, the benchmark is based on Census data: the median earnings of
          working high school graduates ages 25&ndash;34 in the same state, excluding those enrolled
          in college.
        </p>
      </div>

      {/* What is the EP test */}
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-10">
        <h2 className="text-lg font-semibold mb-4">
          What Is the Earnings Premium Test?
        </h2>
        <p className="text-sm text-gray-700 leading-relaxed mb-4">
          The earnings premium is calculated as the difference between a program&apos;s
          graduates&apos; median earnings four years after completion and the state threshold.
          A program whose completers&apos; earnings meet or exceed the threshold passes; a program
          whose completers fall short is designated a &ldquo;low-earning outcome program.&rdquo;
        </p>

        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          How Risk Is Calculated
        </h3>
        <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 font-mono mb-4">
          earnings margin % = (program earnings &minus; state threshold)
          &divide; state threshold &times; 100
        </p>
        <div className="overflow-x-auto mb-5">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left">
                <th className="py-2 pr-4 font-semibold text-gray-700">
                  Risk Level
                </th>
                <th className="py-2 pr-4 font-semibold text-gray-700">
                  Margin %
                </th>
                <th className="py-2 font-semibold text-gray-700">Meaning</th>
              </tr>
            </thead>
            <tbody className="text-gray-600">
              <tr className="border-b">
                <td className="py-2 pr-4">
                  <span className="inline-block w-3 h-3 rounded-full bg-green-600 mr-2" />
                  Very Low Risk
                </td>
                <td className="py-2 pr-4">&ge; +50%</td>
                <td className="py-2">
                  Earnings comfortably exceed the benchmark
                </td>
              </tr>
              <tr className="border-b">
                <td className="py-2 pr-4">
                  <span className="inline-block w-3 h-3 rounded-full bg-lime-500 mr-2" />
                  Low Risk
                </td>
                <td className="py-2 pr-4">+20% to +49.9%</td>
                <td className="py-2">Solid margin above the benchmark</td>
              </tr>
              <tr className="border-b">
                <td className="py-2 pr-4">
                  <span className="inline-block w-3 h-3 rounded-full bg-amber-500 mr-2" />
                  Moderate Risk
                </td>
                <td className="py-2 pr-4">0% to +19.9%</td>
                <td className="py-2">Passes but vulnerable to failing</td>
              </tr>
              <tr>
                <td className="py-2 pr-4">
                  <span className="inline-block w-3 h-3 rounded-full bg-red-600 mr-2" />
                  High Risk
                </td>
                <td className="py-2 pr-4">&lt; 0%</td>
                <td className="py-2">
                  Below the benchmark &mdash; fails the EP test
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
          <p className="font-semibold mb-2">Example</p>
          <p className="leading-relaxed">
            Suppose a medical assisting program in North Carolina has median
            graduate earnings of $31,100 against the state&apos;s threshold of
            $29,300. The margin is ($31,100 &minus; $29,300) &divide; $29,300 ={" "}
            <span className="font-semibold text-amber-600">+6.1%</span>,
            placing it at{" "}
            <span className="font-semibold text-amber-600">Moderate Risk</span>.
            It passes today, but a small drop in earnings could push it below
            the threshold.
          </p>
        </div>
      </div>

      {/* Navigation cards */}
      <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
        Explore the Data
      </h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Link
          href="/risk-analytics"
          className="bg-indigo-600 text-white rounded-xl p-6 shadow-sm hover:bg-indigo-700 transition-all md:col-span-2 lg:col-span-1"
        >
          <h3 className="font-semibold text-lg mb-2">Risk Analytics</h3>
          <p className="text-sm text-indigo-100">
            The big picture: programs, institutions, and students at each risk level,
            split by reported earnings vs. Monte Carlo estimates.
          </p>
        </Link>
        <NavCard
          href="/programs"
          title="Programs"
          description="Explore 213K+ programs across 424 fields of study. See which fields and credentials are most at risk."
        />
        <NavCard
          href="/states"
          title="States"
          description="Compare thresholds and see state-level risk distributions across institutions."
        />
        <NavCard
          href="/institutions"
          title="Institutions"
          description="Look up any institution to see its programs, earnings, and risk exposure."
        />
        <NavCard
          href="/analysis"
          title="Benchmark Analysis"
          description="What if the test used local benchmarks? Explore how geography changes outcomes."
        />
      </div>
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
