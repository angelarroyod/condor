import { usePositions } from "../api/hooks";
import { usePriceStore } from "../store/prices";

const fmt = (n: number) => n.toLocaleString(undefined, { maximumFractionDigits: 2 });
const signed = (n: number) => (n > 0 ? "+" : "") + fmt(n);
const pnlColor = (n: number) =>
  n > 0 ? "text-lx-up-text" : n < 0 ? "text-lx-down-text" : "text-lx-text";

export function Positions({ showRealized = true }: { showRealized?: boolean }) {
  const { data: positions } = usePositions();
  const prices = usePriceStore((s) => s.prices);

  if (!positions || positions.length === 0)
    return <div className="px-5 py-3 text-xs text-lx-text3">No open positions</div>;

  const cell = "border-t border-lx-faint px-2 py-2 text-right text-xs";
  return (
    <table className="w-full border-collapse">
      <thead>
        <tr>
          <th className="lx-th px-5 pb-1.5 pt-1 text-left">Symbol</th>
          <th className="lx-th px-2 pb-1.5 pt-1 text-right">Qty</th>
          <th className="lx-th px-2 pb-1.5 pt-1 text-right">Avg</th>
          <th className="lx-th px-2 pb-1.5 pt-1 text-right">Last</th>
          <th className={`lx-th pb-1.5 pt-1 text-right ${showRealized ? "px-2" : "pl-2 pr-5"}`}>
            uP&amp;L
          </th>
          {showRealized && <th className="lx-th pb-1.5 pl-2 pr-5 pt-1 text-right">rP&amp;L</th>}
        </tr>
      </thead>
      <tbody>
        {positions.map((p) => {
          const qty = Number(p.quantity);
          const avg = Number(p.avg_price);
          const live = prices[p.symbol]?.price ?? Number(p.mark_price ?? p.avg_price);
          const unreal = qty * (live - avg);
          const realized = Number(p.realized_pnl);
          return (
            <tr key={p.symbol}>
              <td className="border-t border-lx-faint py-2 pl-5 pr-2 text-[12.5px] font-semibold text-lx-text">
                {p.symbol}
              </td>
              <td className={`${cell} num text-lx-text2`}>{fmt(qty)}</td>
              <td className={`${cell} num text-lx-text2`}>{fmt(avg)}</td>
              <td className={`${cell} num text-lx-text`}>{fmt(live)}</td>
              <td className={`${cell} num ${pnlColor(unreal)} ${showRealized ? "" : "pr-5"}`}>
                {signed(unreal)}
              </td>
              {showRealized && (
                <td className={`border-t border-lx-faint py-2 pl-2 pr-5 text-right text-xs num ${pnlColor(realized)}`}>
                  {signed(realized)}
                </td>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
