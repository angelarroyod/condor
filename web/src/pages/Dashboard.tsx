import { useMemo } from "react";
import { useAccount, useEquityCurve, usePositions, useSymbols } from "../api/hooks";
import { AllocationDonut } from "../components/AllocationDonut";
import { EquityCurve } from "../components/EquityCurve";
import { MetricsCards } from "../components/MetricsCards";
import { Positions } from "../components/Positions";
import { usePriceStream } from "../ws/priceStream";

const usd = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const dateFmt = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });

function PanelHead({ title, meta }: { title: string; meta: string }) {
  return (
    <div className="flex items-baseline px-[22px] pb-1.5 pt-[15px]">
      <span className="lx-label">{title}</span>
      <span className="ml-auto text-xs text-lx-text3">{meta}</span>
    </div>
  );
}

export function Dashboard() {
  const { data: symbols } = useSymbols();
  const { data: account } = useAccount();
  const { data: curve } = useEquityCurve();
  const { data: positions } = usePositions();

  const all = useMemo(() => symbols?.map((s) => s.symbol) ?? [], [symbols]);
  usePriceStream(all);

  const equity = Number(account?.equity ?? 0);
  const first = curve?.[0];
  const inception = first ? Number(first.equity) : equity;
  const change = equity - inception;
  const changePct = inception ? (change / inception) * 100 : 0;
  const up = change >= 0;

  return (
    <div className="min-h-0 flex-1 overflow-y-auto">
      <div className="mx-auto flex max-w-[1160px] flex-col gap-6 px-9 pb-10 pt-[34px]">
        <div className="flex items-end justify-between gap-6">
          <div className="flex flex-col gap-0.5">
            <span className="lx-label !tracking-[0.16em]">Portfolio equity</span>
            <span className="font-serif text-[58px] leading-[1.05] tracking-[0.01em] text-lx-bright">
              {usd(equity)}
            </span>
            <div className="mt-2.5">
              <span
                className={`num inline-flex items-center rounded-full px-3 py-1 text-[12.5px] ${
                  up ? "bg-lx-up-dim text-lx-up-text" : "bg-lx-down-dim text-lx-down-text"
                }`}
              >
                {up ? "+" : ""}
                {usd(change)} · {up ? "+" : ""}
                {changePct.toFixed(1)}% all-time
              </span>
            </div>
          </div>
          <div className="pb-1 text-right text-xs leading-[1.7] text-lx-text3">
            <div>As of {dateFmt(new Date().toISOString())}</div>
            {first && <div>Since inception · {dateFmt(first.ts)}</div>}
          </div>
        </div>

        <MetricsCards />

        <div className="lx-panel flex flex-col overflow-hidden">
          <PanelHead title="Equity curve" meta={`${curve?.length ?? 0} days`} />
          <div className="relative h-[296px]">
            <EquityCurve />
          </div>
        </div>

        <div className="grid grid-cols-[5fr_7fr] items-stretch gap-6">
          <div className="lx-panel flex flex-col overflow-hidden">
            <PanelHead title="Allocation" meta={`${positions?.length ?? 0} assets`} />
            <AllocationDonut />
          </div>
          <div className="lx-panel flex flex-col overflow-hidden">
            <PanelHead title="Positions" meta={`${positions?.length ?? 0} open`} />
            <Positions showRealized />
          </div>
        </div>
      </div>
    </div>
  );
}
