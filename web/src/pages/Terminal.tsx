import { useEffect, useMemo } from "react";
import { useSymbols } from "../api/hooks";
import { CandleChart } from "../components/CandleChart";
import { Watchlist } from "../components/Watchlist";
import { usePriceStore } from "../store/prices";
import { usePriceStream } from "../ws/priceStream";

export function Terminal() {
  const { data: symbols } = useSymbols();
  const selected = usePriceStore((s) => s.selected);
  const setSelected = usePriceStore((s) => s.setSelected);

  const all = useMemo(() => symbols?.map((s) => s.symbol) ?? [], [symbols]);
  usePriceStream(all);

  // Auto-select the first symbol once the list loads.
  useEffect(() => {
    const first = all[0];
    if (selected === null && first !== undefined) setSelected(first);
  }, [all, selected, setSelected]);

  return (
    <div className="grid min-h-0 flex-1 grid-cols-[260px_1fr]">
      <aside className="overflow-y-auto border-r border-terminal-border">
        <div className="border-b border-terminal-border px-3 py-2 text-xs uppercase tracking-widest text-slate-500">
          Watchlist
        </div>
        <Watchlist />
      </aside>
      <section className="min-h-0">
        <CandleChart />
      </section>
    </div>
  );
}
