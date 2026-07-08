import { useState } from "react";
import { usePlaceOrder } from "../api/hooks";
import type { OrderType, Side } from "../api/types";
import { usePriceStore } from "../store/prices";

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

  const seg = "py-[9px] text-xs font-semibold uppercase tracking-[0.1em] transition-colors";
  const lastColor =
    place.data?.status === "filled"
      ? "text-lx-up-text"
      : place.data?.status === "rejected"
        ? "text-lx-down-text"
        : "text-lx-accent";

  return (
    <div className="flex flex-col gap-3 px-5 pb-[18px] pt-0.5">
      <div className="grid grid-cols-2 overflow-hidden rounded-lg border border-lx-hair">
        <button
          type="button"
          onClick={() => setSide("buy")}
          className={`${seg} ${side === "buy" ? "bg-lx-up-dim text-lx-up-text" : "text-lx-text3"}`}
        >
          Buy
        </button>
        <button
          type="button"
          onClick={() => setSide("sell")}
          className={`${seg} border-l border-lx-hair ${
            side === "sell" ? "bg-lx-down-dim text-lx-down-text" : "text-lx-text3"
          }`}
        >
          Sell
        </button>
      </div>

      <div className="flex gap-1">
        {TYPES.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setType(t)}
            className={`flex-1 rounded-md px-[13px] py-[5px] text-[12.5px] capitalize transition-colors ${
              type === t ? "bg-lx-surface2 text-lx-text" : "text-lx-text3"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <label className="lx-label block">
        Quantity
        <input
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          inputMode="decimal"
          className="lx-input"
        />
      </label>

      {type === "limit" && (
        <label className="lx-label block">
          Limit price
          <input
            value={limitPrice}
            onChange={(e) => setLimitPrice(e.target.value)}
            inputMode="decimal"
            className="lx-input"
          />
        </label>
      )}

      <button
        type="button"
        onClick={submit}
        disabled={!symbol || place.isPending}
        className={`mt-0.5 rounded-lg py-[11px] text-[13px] font-semibold tracking-[0.04em] text-lx-bg transition-[filter] hover:brightness-110 disabled:opacity-40 ${
          side === "buy" ? "bg-lx-up" : "bg-lx-down"
        }`}
      >
        {side === "buy" ? "Buy" : "Sell"} {symbol ?? "—"}
      </button>

      {place.isError && <p className="m-0 text-xs text-lx-down-text">{place.error.message}</p>}
      {place.data && (
        <p className="m-0 text-xs text-lx-text3">
          Last order · <span className={lastColor}>{place.data.status}</span>
          {place.data.reject_reason ? ` (${place.data.reject_reason})` : ""}
        </p>
      )}
    </div>
  );
}
