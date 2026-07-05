import { create } from "zustand";

export interface PriceTick {
  price: number;
  ts: string;
}

interface PriceState {
  prices: Record<string, PriceTick>;
  selected: string | null;
  interval: string;
  setPrice: (symbol: string, tick: PriceTick) => void;
  setSelected: (symbol: string) => void;
  setInterval: (interval: string) => void;
}

/** UI + live-price state. Server data (symbols, candles) stays in TanStack Query. */
export const usePriceStore = create<PriceState>((set) => ({
  prices: {},
  selected: null,
  interval: "1m",
  setPrice: (symbol, tick) => set((s) => ({ prices: { ...s.prices, [symbol]: tick } })),
  setSelected: (symbol) => set({ selected: symbol }),
  setInterval: (interval) => set({ interval }),
}));
