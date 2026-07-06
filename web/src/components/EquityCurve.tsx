import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useEquityCurve } from "../api/hooks";

const usd = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const day = (iso: string) => new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" });

export function EquityCurve() {
  const { data } = useEquityCurve();
  const points = (data ?? []).map((p) => ({ ts: p.ts, equity: Number(p.equity) }));

  if (points.length === 0)
    return <div className="grid h-full place-items-center text-sm text-slate-600">No equity history yet</div>;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={points} margin={{ top: 12, right: 16, bottom: 8, left: 8 }}>
        <defs>
          <linearGradient id="eq" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#26a69a" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#26a69a" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#1f2733" />
        <XAxis dataKey="ts" tickFormatter={day} stroke="#64748b" fontSize={11} minTickGap={40} />
        <YAxis
          tickFormatter={usd}
          stroke="#64748b"
          fontSize={11}
          width={64}
          domain={["auto", "auto"]}
        />
        <Tooltip
          contentStyle={{ background: "#121821", border: "1px solid #1f2733", fontSize: 12 }}
          labelFormatter={day}
          formatter={(v: number) => [usd(v), "Equity"]}
        />
        <Area type="monotone" dataKey="equity" stroke="#26a69a" fill="url(#eq)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
