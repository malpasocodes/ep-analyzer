"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { RISK_COLORS } from "@/lib/utils";

interface Props {
  data: Record<string, number>;
}

const RISK_KEYS = ["Very Low Risk", "Low Risk", "Moderate Risk", "High Risk", "No Data"];

export default function SectorBreakdown({ data }: Props) {
  // data is sector_distribution {sector_name: count}
  // For a risk-by-sector view, we'd need more data.
  // For now, show sector distribution as a bar chart.
  const chartData = Object.entries(data)
    .filter(([k]) => k !== "Unknown")
    .map(([name, value]) => ({ name: name.replace(" ", "\n"), value }))
    .sort((a, b) => b.value - a.value);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 120 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis type="category" dataKey="name" width={120} fontSize={11} />
        <Tooltip />
        <Bar dataKey="value" fill="#6366f1" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
