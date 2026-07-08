import { useCancelOrder, useOrders, useSymbols } from "../api/hooks";

const STATUS_COLOR: Record<string, string> = {
  filled: "text-lx-up-text",
  rejected: "text-lx-down-text",
  cancelled: "text-lx-text3",
  pending: "text-lx-accent",
};

export function Blotter() {
  const { data: orders } = useOrders();
  const { data: symbols } = useSymbols();
  const cancel = useCancelOrder();

  const nameById = new Map(symbols?.map((s) => [s.id, s.symbol]));

  if (!orders || orders.length === 0)
    return <div className="px-5 py-3 text-xs text-lx-text3">No orders yet</div>;

  const cell = "border-t border-lx-faint px-2 py-2 text-xs";
  return (
    <table className="mb-4 w-full border-collapse">
      <thead>
        <tr>
          <th className="lx-th px-5 pb-1.5 pt-1 text-left">Symbol</th>
          <th className="lx-th px-2 pb-1.5 pt-1 text-left">Side</th>
          <th className="lx-th px-2 pb-1.5 pt-1 text-right">Qty</th>
          <th className="lx-th px-2 pb-1.5 pt-1 text-left">Status</th>
          <th className="pb-1.5 pl-2 pr-5 pt-1" />
        </tr>
      </thead>
      <tbody>
        {orders.map((o) => (
          <tr key={o.id}>
            <td className="border-t border-lx-faint py-2 pl-5 pr-2 text-[12.5px] font-semibold text-lx-text">
              {nameById.get(o.symbol_id) ?? o.symbol_id}
            </td>
            <td className={`${cell} ${o.side === "buy" ? "text-lx-up-text" : "text-lx-down-text"}`}>
              {o.side}
            </td>
            <td className={`${cell} num text-right text-lx-text2`}>{Number(o.quantity)}</td>
            <td className={`${cell} ${STATUS_COLOR[o.status] ?? ""}`}>{o.status}</td>
            <td className="border-t border-lx-faint py-2 pl-2 pr-5 text-right">
              {o.status === "pending" && (
                <button
                  type="button"
                  onClick={() => cancel.mutate(o.id)}
                  className="text-lx-text3 transition-colors hover:text-lx-down-text"
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
