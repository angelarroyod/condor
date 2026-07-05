import type { StrategyResult } from "../api/types";

const fmt = (n: number, d = 2) => n.toLocaleString(undefined, { maximumFractionDigits: d });
const pnlColor = (n: number) => (n > 0 ? "text-terminal-up" : n < 0 ? "text-terminal-down" : "");

function Metric({ label, value, className = "" }: { label: string; value: string; className?: string }) {
  return (
    <div className="flex flex-col">
      <span className="text-[10px] uppercase tracking-wide text-slate-500">{label}</span>
      <span className={`tabular-nums text-sm ${className}`}>{value}</span>
    </div>
  );
}

export function GreeksPanel({ result }: { result: StrategyResult }) {
  const g = result.aggregate;
  const maxProfit = result.max_profit_unbounded ? "∞" : fmt(result.max_profit);
  const maxLoss = result.max_loss_unbounded ? "−∞" : fmt(result.max_loss);
  // net_premium: + = debit paid, − = credit received.
  const premiumLabel = result.net_premium >= 0 ? "Net debit" : "Net credit";

  return (
    <div className="flex flex-col gap-3 p-3">
      <div className="grid grid-cols-3 gap-3">
        <Metric label={premiumLabel} value={fmt(Math.abs(result.net_premium))} />
        <Metric label="Max profit" value={maxProfit} className="text-terminal-up" />
        <Metric label="Max loss" value={maxLoss} className="text-terminal-down" />
      </div>

      <div className="grid grid-cols-5 gap-2 border-t border-terminal-border pt-2">
        <Metric label="Delta" value={fmt(g.delta, 3)} className={pnlColor(g.delta)} />
        <Metric label="Gamma" value={fmt(g.gamma, 4)} />
        <Metric label="Vega" value={fmt(g.vega, 2)} />
        <Metric label="Theta/yr" value={fmt(g.theta, 2)} />
        <Metric label="Rho" value={fmt(g.rho, 2)} />
      </div>

      <div className="text-xs text-slate-500">
        Breakevens:{" "}
        <span className="text-slate-300">
          {result.breakevens.length ? result.breakevens.map((b) => fmt(b)).join(", ") : "—"}
        </span>
      </div>
    </div>
  );
}
