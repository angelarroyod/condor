import { Terminal } from "./pages/Terminal";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex items-center gap-3 border-b border-terminal-border px-4 py-3">
        <span className="font-bold tracking-widest text-terminal-up">CONDOR</span>
        <span className="text-xs text-slate-500">paper trading terminal</span>
      </header>
      <Terminal />
    </div>
  );
}
