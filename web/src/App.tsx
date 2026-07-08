import { lazy, Suspense, useState } from "react";
import { useAccount } from "./api/hooks";

// Code-split the three chart-heavy pages.
const Terminal = lazy(() => import("./pages/Terminal").then((m) => ({ default: m.Terminal })));
const StrategyLab = lazy(() =>
  import("./pages/StrategyLab").then((m) => ({ default: m.StrategyLab })),
);
const Dashboard = lazy(() => import("./pages/Dashboard").then((m) => ({ default: m.Dashboard })));

type View = "terminal" | "options" | "dashboard";

const TABS: { id: View; label: string }[] = [
  { id: "terminal", label: "Terminal" },
  { id: "options", label: "Options" },
  { id: "dashboard", label: "Dashboard" },
];

const usd = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });

function HeaderEquity() {
  const { data: account } = useAccount();
  if (!account) return null;
  return (
    <div className="flex items-baseline gap-[9px]">
      <span className="lx-label !tracking-[0.14em]">Equity</span>
      <span className="num text-sm text-lx-bright">{usd(Number(account.equity))}</span>
    </div>
  );
}

export default function App() {
  const [view, setView] = useState<View>("terminal");

  return (
    <div className="flex h-screen min-w-[1280px] flex-col bg-lx-bg text-lx-text">
      <header className="flex h-[58px] flex-none items-stretch gap-7 border-b border-lx-hair px-[26px]">
        <div className="flex items-center gap-[11px]">
          <span className="inline-block h-[7px] w-[7px] rotate-45 bg-lx-accent" />
          <span className="font-serif text-[22px] tracking-[0.02em] text-lx-bright">Condor</span>
        </div>

        <nav className="flex items-stretch">
          {TABS.map((t) => {
            const active = view === t.id;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setView(t.id)}
                className={`mr-[11px] flex items-center border-y-2 border-transparent px-[3px] text-[13.5px] font-medium transition-colors hover:text-lx-text ${
                  active ? "!border-b-lx-accent text-lx-text" : "text-lx-text3"
                }`}
              >
                {t.label}
              </button>
            );
          })}
        </nav>

        <div className="ml-auto flex items-center gap-[18px]">
          <span className="rounded-full border border-lx-accent-border px-[11px] py-[5px] text-[10px] font-semibold uppercase tracking-[0.18em] text-lx-accent">
            Paper
          </span>
          <HeaderEquity />
        </div>
      </header>

      <Suspense
        fallback={<div className="grid flex-1 place-items-center text-sm text-lx-text3">Loading…</div>}
      >
        {view === "terminal" && <Terminal />}
        {view === "options" && <StrategyLab />}
        {view === "dashboard" && <Dashboard />}
      </Suspense>
    </div>
  );
}
