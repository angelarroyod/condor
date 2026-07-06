import { useMemo } from "react";
import { useSymbols } from "../api/hooks";
import { AllocationDonut } from "../components/AllocationDonut";
import { EquityCurve } from "../components/EquityCurve";
import { MetricsCards } from "../components/MetricsCards";
import { Positions } from "../components/Positions";
import { usePriceStream } from "../ws/priceStream";

function Panel({ title, children, className = "" }: { title: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`flex flex-col rounded border border-terminal-border bg-terminal-panel ${className}`}>
      <div className="border-b border-terminal-border px-3 py-1.5 text-xs uppercase tracking-widest text-slate-500">
        {title}
      </div>
      <div className="min-h-0 flex-1">{children}</div>
    </div>
  );
}

export function Dashboard() {
  const { data: symbols } = useSymbols();
  const all = useMemo(() => symbols?.map((s) => s.symbol) ?? [], [symbols]);
  usePriceStream(all); // keep positions' live P&L updating here too

  return (
    <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
      <MetricsCards />
      <Panel title="Equity Curve" className="h-72">
        <EquityCurve />
      </Panel>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel title="Allocation" className="h-64">
          <AllocationDonut />
        </Panel>
        <Panel title="Positions">
          <Positions />
        </Panel>
      </div>
    </div>
  );
}
