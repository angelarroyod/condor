import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { useAllocation } from "../api/hooks";

const COLORS = ["#334155", "#26a69a", "#3b82f6", "#eab308", "#a855f7", "#ef5350", "#14b8a6"];

export function AllocationDonut() {
  const { data } = useAllocation();
  const slices = (data ?? [])
    .filter((a) => a.weight > 0)
    .map((a) => ({ name: a.symbol, value: Number((a.weight * 100).toFixed(2)) }));

  if (slices.length === 0)
    return <div className="grid h-full place-items-center text-xs text-slate-600">No allocation</div>;

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={slices}
          dataKey="value"
          nameKey="name"
          innerRadius="55%"
          outerRadius="80%"
          paddingAngle={2}
          stroke="none"
          label={(e: { name: string }) => e.name}
        >
          {slices.map((s, i) => (
            <Cell key={s.name} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: "#121821", border: "1px solid #1f2733", fontSize: 12 }}
          formatter={(v: number, name: string) => [`${v}%`, name]}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
