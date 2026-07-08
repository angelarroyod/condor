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
    <div className="grid min-h-0 flex-1 grid-cols-[268px_1fr_372px]">
      <aside className="overflow-y-auto border-r border-lx-hair">
        <div className="lx-label px-5 pb-2 pt-4">Watchlist</div>
        <Watchlist />
      </aside>

      <section className="flex min-h-0 flex-col">
        <CandleChart />
      </section>

      <aside className="flex flex-col overflow-y-auto border-l border-lx-hair">
        <AccountBar />
        <div className="lx-label px-5 pb-2 pt-4">Order</div>
        <OrderTicket />
        <div className="lx-label border-t border-lx-faint px-5 pb-2 pt-3.5">Positions</div>
        <Positions showRealized={false} />
        <div className="lx-label mt-2.5 border-t border-lx-faint px-5 pb-2 pt-3.5">Orders</div>
        <Blotter />
      </aside>
    </div>
  );
}
