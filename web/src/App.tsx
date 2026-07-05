import { lazy, Suspense, useState } from "react";

// Code-split the two chart-heavy pages so recharts / lightweight-charts load
// only for the tab in use.
const Terminal = lazy(() => import("./pages/Terminal").then((m) => ({ default: m.Terminal })));
const StrategyLab = lazy(() =>
  import("./pages/StrategyLab").then((m) => ({ default: m.StrategyLab })),
);

type View = "terminal" | "options";

const TABS: { id: View; label: string }[] = [
  { id: "terminal", label: "Terminal" },
  { id: "options", label: "Options" },
];

export default function App() {
  const [view, setView] = useState<View>("terminal");

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center gap-4 border-b border-terminal-border px-4 py-3">
        <span className="font-bold tracking-widest text-terminal-up">CONDOR</span>
        <nav className="flex gap-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setView(t.id)}
              className={`rounded px-3 py-1 text-xs ${
                view === t.id ? "bg-terminal-border text-slate-100" : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
        <span className="ml-auto text-xs text-slate-600">paper trading terminal</span>
      </header>
      <Suspense fallback={<div className="grid flex-1 place-items-center text-sm text-slate-600">Loading…</div>}>
        {view === "terminal" ? <Terminal /> : <StrategyLab />}
      </Suspense>
    </div>
  );
}
