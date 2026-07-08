import { useSymbols } from "../api/hooks";
import { usePriceStore } from "../store/prices";

const fmt = (n: number) => n.toLocaleString(undefined, { maximumFractionDigits: 2 });

export function Watchlist() {
  const { data: symbols, isLoading, error } = useSymbols();
  const prices = usePriceStore((s) => s.prices);
  const selected = usePriceStore((s) => s.selected);
  const setSelected = usePriceStore((s) => s.setSelected);

  if (isLoading) return <div className="p-4 text-sm text-lx-text3">Loading…</div>;
  if (error) return <div className="p-4 text-sm text-lx-down-text">API offline</div>;

  return (
    <ul className="flex list-none flex-col p-0">
      {symbols?.map((s) => {
        const tick = prices[s.symbol];
        const active = s.symbol === selected;
        return (
          <li key={s.symbol} className="flex">
            <button
              type="button"
              onClick={() => setSelected(s.symbol)}
              className={`flex flex-1 items-center justify-between gap-2 border-l-2 py-[11px] pl-4 pr-5 text-left transition-colors ${
                active
                  ? "border-lx-accent bg-lx-surface"
                  : "border-transparent hover:bg-[rgba(214,200,176,0.04)]"
              }`}
            >
              <span className="flex flex-col gap-px">
                <span className="text-sm font-semibold text-lx-text">{s.symbol}</span>
                <span className="text-[11px] text-lx-text3">{s.name}</span>
              </span>
              <span className="num text-[13px] text-lx-text">
                {tick ? fmt(tick.price) : "—"}
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
