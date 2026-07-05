import { useEffect, useMemo } from "react";
import { useSymbols } from "../api/hooks";
import { AccountBar } from "../components/AccountBar";
import { Blotter } from "../components/Blotter";
import { CandleChart } from "../components/CandleChart";
import { OrderTicket } from "../components/OrderTicket";
import { Positions } from "../components/Positions";
import { Watchlist } from "../components/Watchlist";
import { usePriceStore } from "../store/prices";
import { usePriceStream } from "../ws/priceStream";

function SectionLabel({ children }: { children: string }) {
  return (
    <div className="border-y border-terminal-border px-3 py-1.5 text-xs uppercase tracking-widest text-slate-500">
      {children}
    </div>
  );
}

export function Terminal() {
  const { data: symbols } = useSymbols();
  const selected = usePriceStore((s) => s.selected);
  const setSelected = usePriceStore((s) => s.setSelected);

  const all = useMemo(() => symbols?.map((s) => s.symbol) ?? [], [symbols]);
  usePriceStream(all);

  useEffect(() => {
    const first = all[0];
    if (selected === null && first !== undefined) setSelected(first);
  }, [all, selected, setSelected]);

  return (
    <div className="grid min-h-0 flex-1 grid-cols-[240px_1fr_340px]">
      <aside className="overflow-y-auto border-r border-terminal-border">
        <SectionLabel>Watchlist</SectionLabel>
        <Watchlist />
      </aside>

      <section className="min-h-0">
        <CandleChart />
      </section>

      <aside className="flex flex-col overflow-y-auto border-l border-terminal-border">
        <AccountBar />
        <SectionLabel>Order</SectionLabel>
        <OrderTicket />
        <SectionLabel>Positions</SectionLabel>
        <Positions />
        <SectionLabel>Orders</SectionLabel>
        <Blotter />
      </aside>
    </div>
  );
}
