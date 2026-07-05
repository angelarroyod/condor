import { usePositions } from "../api/hooks";
import { usePriceStore } from "../store/prices";

const fmt = (n: number) => n.toLocaleString(undefined, { maximumFractionDigits: 2 });
const pnlColor = (n: number) => (n > 0 ? "text-terminal-up" : n < 0 ? "text-terminal-down" : "");

export function Positions() {
  const { data: positions } = usePositions();
  const prices = usePriceStore((s) => s.prices);

  if (!positions || positions.length === 0)
    return <div className="p-3 text-xs text-slate-600">No open positions</div>;

  return (
    <table className="w-full text-xs">
      <thead className="text-slate-500">
        <tr className="text-left">
          <th className="px-3 py-1 font-normal">Symbol</th>
          <th className="px-3 py-1 text-right font-normal">Qty</th>
          <th className="px-3 py-1 text-right font-normal">Avg</th>
          <th className="px-3 py-1 text-right font-normal">Last</th>
          <th className="px-3 py-1 text-right font-normal">uP&L</th>
          <th className="px-3 py-1 text-right font-normal">rP&L</th>
        </tr>
      </thead>
      <tbody className="tabular-nums">
        {positions.map((p) => {
          const qty = Number(p.quantity);
          const avg = Number(p.avg_price);
          const live = prices[p.symbol]?.price ?? Number(p.mark_price ?? p.avg_price);
          const unreal = qty * (live - avg);
          const realized = Number(p.realized_pnl);
          return (
            <tr key={p.symbol} className="border-t border-terminal-border/50">
              <td className="px-3 py-1 font-semibold">{p.symbol}</td>
              <td className="px-3 py-1 text-right">{qty}</td>
              <td className="px-3 py-1 text-right">{fmt(avg)}</td>
              <td className="px-3 py-1 text-right">{fmt(live)}</td>
              <td className={`px-3 py-1 text-right ${pnlColor(unreal)}`}>{fmt(unreal)}</td>
              <td className={`px-3 py-1 text-right ${pnlColor(realized)}`}>{fmt(realized)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
