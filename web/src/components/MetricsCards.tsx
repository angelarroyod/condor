import { useMetrics } from "../api/hooks";

const pct = (n: number) => `${(n * 100).toFixed(1)}%`;

function Card({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded border border-terminal-border bg-terminal-panel px-4 py-3">
      <div className="text-[10px] uppercase tracking-widest text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold tabular-nums text-slate-100">{value}</div>
      {hint && <div className="text-[10px] text-slate-600">{hint}</div>}
    </div>
  );
}

export function MetricsCards() {
  const { data: metrics, isLoading } = useMetrics();

  if (isLoading) return <div className="text-sm text-slate-600">Loading metrics…</div>;
  if (!metrics)
    return (
      <div className="rounded border border-terminal-border bg-terminal-panel px-4 py-3 text-sm text-slate-500">
        Need ≥2 days of equity history for risk metrics.
      </div>
    );

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      <Card label="Sharpe" value={metrics.sharpe.toFixed(2)} hint="annualized, rf=0" />
      <Card label="Volatility" value={pct(metrics.annualized_vol)} hint="annualized" />
      <Card label="Max Drawdown" value={pct(metrics.max_drawdown)} hint="peak-to-trough" />
      <Card label="VaR 95%" value={pct(metrics.var_95)} hint="1-day historical" />
    </div>
  );
}
