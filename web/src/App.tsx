// Terminal shell. Phase 1 fills this with the live watchlist + candlestick chart.
export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-terminal-border px-4 py-3 flex items-center gap-3">
        <span className="text-terminal-up font-bold tracking-widest">CONDOR</span>
        <span className="text-xs text-slate-500">paper trading terminal</span>
      </header>
      <main className="flex-1 grid place-items-center text-slate-500 text-sm">
        Phase 1 — market data wiring in progress.
      </main>
    </div>
  );
}
