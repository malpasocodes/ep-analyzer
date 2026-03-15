"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";

interface Props {
  margins: number[];
}

export default function MarginHistogram({ margins }: Props) {
  // Bucket margins into bins
  const binWidth = 10;
  const minBin = Math.floor(Math.min(...margins) / binWidth) * binWidth;
  const maxBin = Math.ceil(Math.max(...margins) / binWidth) * binWidth;

  const bins: Record<number, number> = {};
  for (let b = minBin; b <= maxBin; b += binWidth) {
    bins[b] = 0;
  }
  for (const m of margins) {
    const bin = Math.floor(m / binWidth) * binWidth;
    bins[bin] = (bins[bin] || 0) + 1;
  }

  const chartData = Object.entries(bins)
    .map(([bin, count]) => ({
      bin: `${bin}%`,
      binVal: Number(bin),
      count,
    }))
    .sort((a, b) => a.binVal - b.binVal);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="bin" fontSize={11} />
        <YAxis />
        <Tooltip />
        <ReferenceLine x="0%" stroke="#ef4444" strokeWidth={2} label="Threshold" />
        <Bar
          dataKey="count"
          fill="#3b82f6"
          radius={[2, 2, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
