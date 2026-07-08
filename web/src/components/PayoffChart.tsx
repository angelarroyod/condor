import {
  Area,
  AreaChart,
  CartesianGrid,
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
const AXIS = "#6E6759";
const GRID = "rgba(214,200,176,0.055)";

export function PayoffChart({ result, spot, domain }: Props) {
  const data = result.payoff.filter((p) => p.spot >= domain[0] && p.spot <= domain[1]);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 18, right: 30, bottom: 8, left: 8 }}>
        <defs>
          <linearGradient id="payoff" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#C9A66B" stopOpacity={0.22} />
            <stop offset="100%" stopColor="#C9A66B" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke={GRID} />
        <XAxis
          dataKey="spot"
          type="number"
          domain={["dataMin", "dataMax"]}
          tickFormatter={fmt}
          stroke={AXIS}
          fontSize={11}
        />
        <YAxis tickFormatter={fmt} stroke={AXIS} fontSize={11} width={56} />
        <Tooltip
          contentStyle={{
            background: "#14120F",
            border: "1px solid rgba(214,200,176,0.1)",
            borderRadius: 8,
            fontSize: 12,
            color: "#EAE4D6",
          }}
          labelFormatter={(v) => `Spot ${fmt(Number(v))}`}
          formatter={(v: number) => [fmt(v), "P&L"]}
        />
        <ReferenceLine y={0} stroke="rgba(234,228,214,0.25)" />
        <ReferenceLine
          x={spot}
          stroke="#C9A66B"
          strokeDasharray="3 4"
          label={{ value: `SPOT ${fmt(spot)}`, fill: "#C9A66B", fontSize: 10, position: "top" }}
        />
        {result.breakevens.map((be) => (
          <ReferenceLine key={be} x={be} stroke="rgba(167,159,142,0.5)" strokeDasharray="1.5 3.5" />
        ))}
        <Area
          type="monotone"
          dataKey="pnl"
          stroke="#E4C98F"
          strokeWidth={2}
          fill="url(#payoff)"
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
