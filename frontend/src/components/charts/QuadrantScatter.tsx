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
import { CLASSIFICATION_COLORS } from "@/lib/utils";
import type { ReclassificationProgram } from "@/lib/api";

interface Props {
  programs: ReclassificationProgram[];
}

export default function QuadrantScatter({ programs }: Props) {
  const data = programs.map((p) => ({
    x: p.distance_state,
    y: p.distance_local,
    name: p.name,
    classification: p.classification,
  }));

  return (
    <ResponsiveContainer width="100%" height={450}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 40 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="x"
          name="Distance from State Benchmark"
          type="number"
          label={{
            value: "Distance from State Benchmark ($)",
            position: "bottom",
            offset: 20,
          }}
          tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
        />
        <YAxis
          dataKey="y"
          name="Distance from Local Benchmark"
          type="number"
          label={{
            value: "Distance from Local Benchmark ($)",
            angle: -90,
            position: "left",
            offset: 20,
          }}
          tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
        />
        <ReferenceLine x={0} stroke="#333" strokeWidth={1.5} />
        <ReferenceLine y={0} stroke="#333" strokeWidth={1.5} />
        <Tooltip
          content={({ payload }) => {
            if (!payload?.length) return null;
            const d = payload[0].payload;
            return (
              <div className="bg-white border rounded p-2 shadow text-sm">
                <p className="font-medium">{d.name}</p>
                <p>State distance: ${d.x.toLocaleString()}</p>
                <p>Local distance: ${d.y.toLocaleString()}</p>
                <p className="font-medium">{d.classification}</p>
              </div>
            );
          }}
        />
        <Scatter data={data}>
          {data.map((entry, i) => (
            <Cell
              key={i}
              fill={CLASSIFICATION_COLORS[entry.classification] || "#999"}
              fillOpacity={0.7}
            />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );
}
