import { useMetrics } from "../api/hooks";

const pct = (n: number) => `${(n * 100).toFixed(1)}%`;

function Stat({ label, value, sub, first }: { label: string; value: string; sub: string; first?: boolean }) {
  return (
    <div className={first ? "pl-1.5" : "border-l border-lx-faint pl-[30px]"}>
      <div className="lx-label">{label}</div>
      <div className="mt-[5px] font-serif text-[30px] leading-tight text-lx-bright">{value}</div>
      <div className="mt-0.5 text-[11.5px] text-lx-text3">{sub}</div>
    </div>
  );
}

export function MetricsCards() {
  const { data: metrics, isLoading } = useMetrics();

  const shell = "grid grid-cols-4 border-y border-lx-hair py-5";
  if (isLoading) return <div className={`${shell} text-sm text-lx-text3`}>Loading metrics…</div>;
  if (!metrics)
    return (
      <div className="rounded-xl border border-lx-hair bg-lx-panel px-4 py-3 text-sm text-lx-text3">
        Need ≥2 days of equity history for risk metrics.
      </div>
    );

  return (
    <div className={shell}>
      <Stat first label="Sharpe" value={metrics.sharpe.toFixed(2)} sub="annualized, rf = 0" />
      <Stat label="Volatility" value={pct(metrics.annualized_vol)} sub="annualized" />
      <Stat label="Max drawdown" value={pct(metrics.max_drawdown)} sub="peak to trough" />
      <Stat label="VaR 95%" value={pct(metrics.var_95)} sub="1-day, historical" />
    </div>
  );
}
