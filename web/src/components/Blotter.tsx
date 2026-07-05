import { useCancelOrder, useOrders, useSymbols } from "../api/hooks";

const STATUS_COLOR: Record<string, string> = {
  filled: "text-terminal-up",
  rejected: "text-terminal-down",
  cancelled: "text-slate-500",
  pending: "text-amber-400",
};

export function Blotter() {
  const { data: orders } = useOrders();
  const { data: symbols } = useSymbols();
  const cancel = useCancelOrder();

  const nameById = new Map(symbols?.map((s) => [s.id, s.symbol]));

  if (!orders || orders.length === 0)
    return <div className="p-3 text-xs text-slate-600">No orders yet</div>;

  return (
    <table className="w-full text-xs">
      <thead className="text-slate-500">
        <tr className="text-left">
          <th className="px-3 py-1 font-normal">Symbol</th>
          <th className="px-3 py-1 font-normal">Side</th>
          <th className="px-3 py-1 font-normal">Type</th>
          <th className="px-3 py-1 text-right font-normal">Qty</th>
          <th className="px-3 py-1 font-normal">Status</th>
          <th className="px-3 py-1" />
        </tr>
      </thead>
      <tbody className="tabular-nums">
        {orders.map((o) => (
          <tr key={o.id} className="border-t border-terminal-border/50">
            <td className="px-3 py-1 font-semibold">{nameById.get(o.symbol_id) ?? o.symbol_id}</td>
            <td className={`px-3 py-1 ${o.side === "buy" ? "text-terminal-up" : "text-terminal-down"}`}>
              {o.side}
            </td>
            <td className="px-3 py-1 text-slate-400">{o.type}</td>
            <td className="px-3 py-1 text-right">{Number(o.quantity)}</td>
            <td className={`px-3 py-1 ${STATUS_COLOR[o.status] ?? ""}`}>{o.status}</td>
            <td className="px-3 py-1 text-right">
              {o.status === "pending" && (
                <button
                  type="button"
                  onClick={() => cancel.mutate(o.id)}
                  className="text-slate-500 hover:text-terminal-down"
                >
                  ✕
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
