import { PROGRAM_RISK_COLORS, formatNumber } from "@/lib/utils";

const RISK_LEVELS = ["Very Low Risk", "Low Risk", "Moderate Risk", "High Risk"];

interface RiskBarProps {
  distribution: Record<string, number>;
  riskOnly?: boolean;
  title?: string;
}

export default function RiskBar({ distribution, riskOnly = true, title }: RiskBarProps) {
  const entries = Object.entries(distribution)
    .filter(([level]) => (riskOnly ? RISK_LEVELS.includes(level) : true))
    .sort(([a], [b]) => {
      const order = [...RISK_LEVELS, "Privacy Suppressed", "No Cohort", "No Data"];
      return order.indexOf(a) - order.indexOf(b);
    });

  const total = entries.reduce((sum, [, c]) => sum + c, 0);
  if (total === 0) return null;

  return (
    <div>
      {title && (
        <p className="text-sm font-medium text-gray-600 mb-2">{title}</p>
      )}
      <div className="flex h-6 rounded-full overflow-hidden bg-gray-100">
        {entries.map(([level, count]) => (
          <div
            key={level}
            style={{
              width: `${(count / total) * 100}%`,
              backgroundColor: PROGRAM_RISK_COLORS[level] || "#9ca3af",
            }}
            title={`${level}: ${formatNumber(count)}`}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-3 mt-2 text-xs">
        {entries.map(([level, count]) => (
          <div key={level} className="flex items-center gap-1">
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: PROGRAM_RISK_COLORS[level] || "#9ca3af" }}
            />
            <span>
              {level}: {formatNumber(count)} ({((count / total) * 100).toFixed(1)}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
