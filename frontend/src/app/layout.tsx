import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "EP Analyzer — Earnings Premium Analysis",
  description:
    "Analyze how geographic bias in statewide earnings benchmarks affects college program accountability.",
};

const navLinks = [
  { href: "/", label: "Overview" },
  { href: "/states", label: "States" },
  { href: "/institutions", label: "Institutions" },
  { href: "/programs", label: "Programs" },
  { href: "/analysis", label: "Analysis" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className="antialiased bg-gray-50 text-gray-900 font-sans"
      >
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <Link href="/" className="text-xl font-bold text-indigo-600">
                EP Analyzer
              </Link>
              <nav className="flex gap-6">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="text-sm font-medium text-gray-600 hover:text-indigo-600 transition-colors"
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-200 mt-16 py-8 text-center text-sm text-gray-500">
          EP Analyzer — Earnings Premium Analysis Tool. Data from College
          Scorecard, IPEDS, and Census ACS.
        </footer>
      </body>
    </html>
  );
}
