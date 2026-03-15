"use client";

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface Institution {
  unit_id: number;
  name: string;
  earnings_p6: number;
  earnings_p10: number;
  threshold: number | null;
  changed: boolean | null;
}

interface Props {
  institutions: Institution[];
}

export default function EarningsComparison({ institutions }: Props) {
  const data = institutions.map((inst) => ({
    x: inst.earnings_p6,
    y: inst.earnings_p10,
    name: inst.name,
    changed: inst.changed,
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 40 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="x"
          type="number"
          name="6-Year Earnings"
          tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
          label={{
            value: "6-Year Median Earnings",
            position: "bottom",
            offset: 20,
          }}
        />
        <YAxis
          dataKey="y"
          type="number"
          name="10-Year Earnings"
          tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
          label={{
            value: "10-Year Median Earnings",
            angle: -90,
            position: "left",
            offset: 20,
          }}
        />
        {/* Diagonal line: y = x */}
        <ReferenceLine
          segment={[
            { x: 0, y: 0 },
            { x: 150000, y: 150000 },
          ]}
          stroke="#999"
          strokeDasharray="5 5"
        />
        <Tooltip
          content={({ payload }) => {
            if (!payload?.length) return null;
            const d = payload[0].payload;
            return (
              <div className="bg-white border rounded p-2 shadow text-sm">
                <p className="font-medium">{d.name}</p>
                <p>6-Year: ${d.x.toLocaleString()}</p>
                <p>10-Year: ${d.y.toLocaleString()}</p>
                {d.changed && (
                  <p className="text-amber-600 font-medium">
                    Pass/fail changes between P6 and P10
                  </p>
                )}
              </div>
            );
          }}
        />
        <Scatter data={data}>
          {data.map((entry, i) => (
            <Cell
              key={i}
              fill={entry.changed ? "#f59e0b" : "#3b82f6"}
              fillOpacity={0.6}
            />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );
}
