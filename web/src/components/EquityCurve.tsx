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
const day = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" });

export function EquityCurve() {
  const { data } = useEquityCurve();
  const points = (data ?? []).map((p) => ({ ts: p.ts, equity: Number(p.equity) }));

  if (points.length === 0)
    return <div className="grid h-full place-items-center text-sm text-lx-text3">No equity history yet</div>;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={points} margin={{ top: 14, right: 26, bottom: 8, left: 8 }}>
        <defs>
          <linearGradient id="equity" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#C9A66B" stopOpacity={0.22} />
            <stop offset="100%" stopColor="#C9A66B" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(214,200,176,0.055)" />
        <XAxis dataKey="ts" tickFormatter={day} stroke="#6E6759" fontSize={11} minTickGap={44} />
        <YAxis tickFormatter={usd} stroke="#6E6759" fontSize={11} width={72} domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{
            background: "#14120F",
            border: "1px solid rgba(214,200,176,0.1)",
            borderRadius: 8,
            fontSize: 12,
            color: "#EAE4D6",
          }}
          labelFormatter={day}
          formatter={(v: number) => [usd(v), "Equity"]}
        />
        <Area type="monotone" dataKey="equity" stroke="#C9A66B" strokeWidth={1.75} fill="url(#equity)" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
