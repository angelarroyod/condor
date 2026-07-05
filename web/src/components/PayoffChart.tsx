import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { StrategyResult } from "../api/types";

interface Props {
  result: StrategyResult;
  spot: number;
  domain: [number, number];
}

const fmt = (n: number) => n.toLocaleString(undefined, { maximumFractionDigits: 2 });

export function PayoffChart({ result, spot, domain }: Props) {
  // Focus the view on the interesting region (server grid runs 0 → 3× strike).
  const data = result.payoff.filter((p) => p.spot >= domain[0] && p.spot <= domain[1]);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data} margin={{ top: 12, right: 16, bottom: 8, left: 8 }}>
        <CartesianGrid stroke="#1f2733" />
        <XAxis
          dataKey="spot"
          type="number"
          domain={["dataMin", "dataMax"]}
          tickFormatter={fmt}
          stroke="#64748b"
          fontSize={11}
        />
        <YAxis tickFormatter={fmt} stroke="#64748b" fontSize={11} width={56} />
        <Tooltip
          contentStyle={{ background: "#121821", border: "1px solid #1f2733", fontSize: 12 }}
          labelFormatter={(v) => `Spot ${fmt(Number(v))}`}
          formatter={(v: number) => [fmt(v), "P&L"]}
        />
        <ReferenceLine y={0} stroke="#475569" />
        <ReferenceLine x={spot} stroke="#64748b" strokeDasharray="4 4" label={{ value: "spot", fill: "#64748b", fontSize: 10 }} />
        {result.breakevens.map((be) => (
          <ReferenceLine key={be} x={be} stroke="#eab308" strokeDasharray="2 2" />
        ))}
        <Line type="monotone" dataKey="pnl" stroke="#26a69a" dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}
