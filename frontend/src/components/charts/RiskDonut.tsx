"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { RISK_COLORS } from "@/lib/utils";

interface Props {
  data: Record<string, number>;
}

const RISK_ORDER = ["Very Low Risk", "Low Risk", "Moderate Risk", "High Risk", "No Data", "No Cohort", "Privacy Suppressed"];

export default function RiskDonut({ data }: Props) {
  const chartData = RISK_ORDER.filter((k) => data[k] > 0).map((name) => ({
    name,
    value: data[name],
  }));

  return (
    <ResponsiveContainer width="100%" height={350}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="45%"
          innerRadius={60}
          outerRadius={110}
          paddingAngle={2}
          dataKey="value"
          label={({ name, percent, x, y, textAnchor }) => (
            <text x={x} y={y} textAnchor={textAnchor} dominantBaseline="central" fontSize={12} fill="#374151">
              {`${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
            </text>
          )}
          labelLine={true}
        >
          {chartData.map((entry) => (
            <Cell key={entry.name} fill={RISK_COLORS[entry.name]} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => String(value).replace(/\B(?=(\d{3})+(?!\d))/g, ",")} />
      </PieChart>
    </ResponsiveContainer>
  );
}
