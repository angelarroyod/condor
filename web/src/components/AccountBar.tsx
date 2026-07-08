import { useAccount } from "../api/hooks";

const usd = (n: number) =>
  n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="lx-label">{label}</span>
      <span className="num text-sm text-lx-text">{value}</span>
    </div>
  );
}

export function AccountBar() {
  const { data: account } = useAccount();
  const cash = Number(account?.cash_balance ?? 0);
  const marketValue = Number(account?.equity ?? 0) - cash;

  return (
    <div className="flex flex-none gap-9 border-b border-lx-faint px-5 py-4">
      <Stat label="Cash" value={usd(cash)} />
      <Stat label="Market value" value={usd(marketValue)} />
    </div>
  );
}
