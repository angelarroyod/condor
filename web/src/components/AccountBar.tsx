import { useAccount, usePositions } from "../api/hooks";
import { usePriceStore } from "../store/prices";

const usd = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export function AccountBar() {
  const { data: account } = useAccount();
  const { data: positions } = usePositions();
  const prices = usePriceStore((s) => s.prices);

  const cash = Number(account?.cash_balance ?? 0);
  // Live equity = cash + Σ signed qty × latest price (falls back to server mark).
  const marketValue = (positions ?? []).reduce((sum, p) => {
    const live = prices[p.symbol]?.price ?? Number(p.mark_price ?? p.avg_price);
    return sum + Number(p.quantity) * live;
  }, 0);
  const equity = cash + marketValue;

  return (
    <div className="flex items-center gap-6 px-3 py-2 text-xs tabular-nums">
      <div>
        <span className="text-slate-500">Cash </span>
        <span className="text-slate-100">{usd(cash)}</span>
      </div>
      <div>
        <span className="text-slate-500">Equity </span>
        <span className="font-semibold text-terminal-up">{usd(equity)}</span>
      </div>
    </div>
  );
}
