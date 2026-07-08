import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import { useAccount, useAllocation } from "../api/hooks";

const usd = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });

// CASH renders in a muted stone; assets cycle the champagne/stone/jade set.
const ASSET_COLORS = ["#C9A66B", "#A79F8E", "#64907F", "#B58455"];
const colorFor = (symbol: string, i: number) =>
  symbol === "CASH" ? "#3F3B33" : ASSET_COLORS[i % ASSET_COLORS.length];

export function AllocationDonut() {
  const { data } = useAllocation();
  const { data: account } = useAccount();

  const slices = (data ?? [])
    .filter((a) => a.weight > 0)
    .map((a, i) => ({
      name: a.symbol,
      value: Number((a.weight * 100).toFixed(2)),
      usd: Number(a.market_value),
      color: colorFor(a.symbol, i),
    }));

  if (slices.length === 0)
    return <div className="grid h-full place-items-center text-xs text-lx-text3">No allocation</div>;

  return (
    <div className="flex flex-1 items-center gap-2 py-2 pl-2.5 pr-[22px]">
      <div className="relative h-[218px] w-[218px] flex-none">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={slices}
              dataKey="value"
              nameKey="name"
              innerRadius="72%"
              outerRadius="94%"
              paddingAngle={2}
              startAngle={90}
              endAngle={-270}
              stroke="none"
            >
              {slices.map((s) => (
                <Cell key={s.name} fill={s.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-[9.5px] tracking-[0.3em] text-lx-text3">EQUITY</span>
          <span className="num mt-0.5 font-serif text-[23px] text-lx-bright">
            {usd(Number(account?.equity ?? 0))}
          </span>
        </div>
      </div>

      <ul className="flex flex-1 list-none flex-col gap-3 p-0">
        {slices.map((s) => (
          <li key={s.name} className="flex items-center gap-2.5">
            <span className="h-2 w-2 flex-none rounded-sm" style={{ background: s.color }} />
            <span className="text-[13px] text-lx-text">{s.name}</span>
            <span className="num ml-auto text-[13px] text-lx-bright">{s.value.toFixed(1)}%</span>
            <span className="num w-[74px] text-right text-[11px] text-lx-text3">{usd(s.usd)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
