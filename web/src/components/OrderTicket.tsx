import { useState } from "react";
import { usePlaceOrder } from "../api/hooks";
import type { OrderType, Side } from "../api/types";
import { usePriceStore } from "../store/prices";

const SIDES: Side[] = ["buy", "sell"];
const TYPES: OrderType[] = ["market", "limit"];

export function OrderTicket() {
  const symbol = usePriceStore((s) => s.selected);
  const place = usePlaceOrder();
  const [side, setSide] = useState<Side>("buy");
  const [type, setType] = useState<OrderType>("market");
  const [quantity, setQuantity] = useState("0.01");
  const [limitPrice, setLimitPrice] = useState("");

  const submit = () => {
    if (!symbol) return;
    place.mutate({
      symbol,
      side,
      type,
      quantity,
      idempotency_key: crypto.randomUUID(),
      ...(type === "limit" && limitPrice ? { limit_price: limitPrice } : {}),
    });
  };

  const sideColor = side === "buy" ? "bg-terminal-up" : "bg-terminal-down";

  return (
    <div className="flex flex-col gap-2 p-3">
      <div className="grid grid-cols-2 gap-1">
        {SIDES.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setSide(s)}
            className={`rounded py-1 text-xs font-semibold uppercase ${
              side === s
                ? `${s === "buy" ? "bg-terminal-up" : "bg-terminal-down"} text-black`
                : "bg-terminal-border/40 text-slate-400"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="flex gap-1">
        {TYPES.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setType(t)}
            className={`flex-1 rounded py-1 text-xs ${
              type === t ? "bg-terminal-border text-slate-100" : "text-slate-500"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <label className="text-xs text-slate-500">
        Quantity
        <input
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          inputMode="decimal"
          className="mt-1 w-full rounded bg-terminal-bg px-2 py-1 text-sm text-slate-100 outline-none ring-1 ring-terminal-border focus:ring-terminal-up"
        />
      </label>

      {type === "limit" && (
        <label className="text-xs text-slate-500">
          Limit price
          <input
            value={limitPrice}
            onChange={(e) => setLimitPrice(e.target.value)}
            inputMode="decimal"
            className="mt-1 w-full rounded bg-terminal-bg px-2 py-1 text-sm text-slate-100 outline-none ring-1 ring-terminal-border focus:ring-terminal-up"
          />
        </label>
      )}

      <button
        type="button"
        onClick={submit}
        disabled={!symbol || place.isPending}
        className={`mt-1 rounded py-2 text-sm font-semibold text-black disabled:opacity-40 ${sideColor}`}
      >
        {side === "buy" ? "Buy" : "Sell"} {symbol ?? "—"}
      </button>

      {place.isError && <p className="text-xs text-terminal-down">{place.error.message}</p>}
      {place.data && (
        <p className="text-xs text-slate-400">
          Last: {place.data.status}
          {place.data.reject_reason ? ` (${place.data.reject_reason})` : ""}
        </p>
      )}
    </div>
  );
}
