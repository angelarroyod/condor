import { useSymbols } from "../api/hooks";
import { usePriceStore } from "../store/prices";

export function Watchlist() {
  const { data: symbols, isLoading, error } = useSymbols();
  const prices = usePriceStore((s) => s.prices);
  const selected = usePriceStore((s) => s.selected);
  const setSelected = usePriceStore((s) => s.setSelected);

  if (isLoading) return <div className="p-3 text-sm text-slate-500">Loading…</div>;
  if (error) return <div className="p-3 text-sm text-terminal-down">API offline</div>;

  return (
    <ul className="divide-y divide-terminal-border">
      {symbols?.map((s) => {
        const tick = prices[s.symbol];
        const active = s.symbol === selected;
        return (
          <li key={s.symbol}>
            <button
              type="button"
              onClick={() => setSelected(s.symbol)}
              className={`flex w-full items-center justify-between px-3 py-2 text-sm hover:bg-terminal-border/40 ${
                active ? "bg-terminal-border/60" : ""
              }`}
            >
              <span className="font-semibold">{s.symbol}</span>
              <span className="tabular-nums text-slate-300">
                {tick ? tick.price.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "—"}
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
