import type { StrategyResult } from "../api/types";

const fmt = (n: number, d = 2) => n.toLocaleString(undefined, { maximumFractionDigits: d });
const pnlColor = (n: number) =>
  n > 0 ? "text-lx-up-text" : n < 0 ? "text-lx-down-text" : "text-lx-text";

function Big({ label, value, className = "text-lx-bright" }: { label: string; value: string; className?: string }) {
  return (
    <div className="flex flex-col gap-[3px]">
      <span className="lx-th">{label}</span>
      <span className={`num text-base ${className}`}>{value}</span>
    </div>
  );
}

function Greek({ label, value, className = "text-lx-text" }: { label: string; value: string; className?: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="lx-th">{label}</span>
      <span className={`num text-[13px] ${className}`}>{value}</span>
    </div>
  );
}

export function GreeksPanel({ result }: { result: StrategyResult }) {
  const g = result.aggregate;
  const maxProfit = result.max_profit_unbounded ? "Unlimited" : fmt(result.max_profit);
  const maxLoss = result.max_loss_unbounded ? "Unlimited" : fmt(result.max_loss);
  const premiumLabel = result.net_premium >= 0 ? "Net debit" : "Net credit";

  return (
    <div className="flex flex-col gap-3.5 border-t border-lx-faint px-5 py-[18px]">
      <div className="grid grid-cols-3 gap-3">
        <Big label={premiumLabel} value={fmt(Math.abs(result.net_premium))} />
        <Big label="Max profit" value={maxProfit} className="text-lx-up-text" />
        <Big label="Max loss" value={maxLoss} className="text-lx-down-text" />
      </div>

      <div className="grid grid-cols-5 gap-2.5 border-t border-lx-faint pt-3">
        <Greek label="Delta" value={fmt(g.delta, 3)} className={pnlColor(g.delta)} />
        <Greek label="Gamma" value={fmt(g.gamma, 4)} />
        <Greek label="Vega" value={fmt(g.vega, 2)} />
        <Greek label="Theta/yr" value={fmt(g.theta, 2)} />
        <Greek label="Rho" value={fmt(g.rho, 2)} />
      </div>

      <div className="text-xs text-lx-text3">
        Breakevens ·{" "}
        <span className="num text-lx-text2">
          {result.breakevens.length ? result.breakevens.map((b) => fmt(b)).join("  ·  ") : "—"}
        </span>
      </div>
    </div>
  );
}
