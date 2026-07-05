import { useEffect } from "react";
import type { QuoteDTO } from "../api/types";
import { WS_URL } from "../config";
import { usePriceStore } from "../store/prices";

/**
 * Subscribe to the server's price fan-out for `symbols`, pushing ticks into the
 * store. Reconnects with jittered exponential backoff; the backoff resets on a
 * successful open. Keyed on the joined symbol list so it re-subscribes only when
 * the set actually changes.
 */
export function usePriceStream(symbols: string[]): void {
  const setPrice = usePriceStore((s) => s.setPrice);
  const key = symbols.join(",");

  useEffect(() => {
    if (!key) return;
    let closedByUs = false;
    let attempt = 0;
    let socket: WebSocket | null = null;
    let timer: number | undefined;

    const connect = () => {
      socket = new WebSocket(`${WS_URL}/ws/prices?symbols=${key}`);
      socket.onopen = () => {
        attempt = 0;
      };
      socket.onmessage = (ev) => {
        try {
          const q = JSON.parse(ev.data as string) as QuoteDTO;
          setPrice(q.symbol, { price: Number(q.price), ts: q.ts });
        } catch {
          // ignore malformed frame
        }
      };
      socket.onclose = () => {
        if (closedByUs) return;
        const ceiling = Math.min(30_000, 1_000 * 2 ** attempt);
        attempt += 1;
        timer = window.setTimeout(connect, ceiling * (0.5 + Math.random() * 0.5));
      };
      socket.onerror = () => socket?.close();
    };

    connect();
    return () => {
      closedByUs = true;
      if (timer !== undefined) window.clearTimeout(timer);
      socket?.close();
    };
  }, [key, setPrice]);
}
