import { useQuery } from "@tanstack/react-query";
import { apiGet } from "./client";
import type { CandleDTO, SymbolInfo } from "./types";

export function useSymbols() {
  return useQuery({
    queryKey: ["symbols"],
    queryFn: () => apiGet<SymbolInfo[]>("/api/symbols"),
    staleTime: Infinity, // reference data
  });
}

export function useCandles(symbol: string | null, interval: string) {
  return useQuery({
    queryKey: ["candles", symbol, interval],
    queryFn: () =>
      apiGet<CandleDTO[]>(`/api/symbols/${symbol}/candles?interval=${interval}&limit=500`),
    enabled: symbol !== null,
  });
}
