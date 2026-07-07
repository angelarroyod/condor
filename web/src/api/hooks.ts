import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiDelete, apiGet, apiPost } from "./client";
import type {
  AccountDTO,
  AllocationEntry,
  CandleDTO,
  EquityPoint,
  MetricsDTO,
  OrderCreate,
  OrderDTO,
  PositionDTO,
  SavedStrategy,
  StrategyInput,
  StrategyResult,
  SymbolInfo,
} from "./types";

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

export function useOrders() {
  return useQuery({ queryKey: ["orders"], queryFn: () => apiGet<OrderDTO[]>("/api/orders") });
}

export function usePositions() {
  return useQuery({
    queryKey: ["positions"],
    queryFn: () => apiGet<PositionDTO[]>("/api/positions"),
  });
}

export function useAccount() {
  return useQuery({ queryKey: ["account"], queryFn: () => apiGet<AccountDTO>("/api/account") });
}

/** Invalidate everything the account's trading state touches after a write. */
function useInvalidateTrading() {
  const qc = useQueryClient();
  return () =>
    ["orders", "positions", "account", "fills"].forEach((k) =>
      qc.invalidateQueries({ queryKey: [k] }),
    );
}

export function usePlaceOrder() {
  const invalidate = useInvalidateTrading();
  return useMutation({
    mutationFn: (body: OrderCreate) => apiPost<OrderDTO>("/api/orders", body),
    onSuccess: invalidate,
  });
}

export function useCancelOrder() {
  const invalidate = useInvalidateTrading();
  return useMutation({
    mutationFn: (id: string) => apiDelete<OrderDTO>(`/api/orders/${id}`),
    onSuccess: invalidate,
  });
}

export function useStrategy(input: StrategyInput | null) {
  return useQuery({
    queryKey: ["strategy", input],
    queryFn: () => apiPost<StrategyResult>("/api/options/strategy", input),
    enabled: input !== null && input.legs.length > 0,
  });
}

export function useSavedStrategies() {
  return useQuery({
    queryKey: ["strategies"],
    queryFn: () => apiGet<SavedStrategy[]>("/api/options/strategies"),
  });
}

export function useSaveStrategy() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; definition: StrategyInput }) =>
      apiPost<SavedStrategy>("/api/options/strategies", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["strategies"] }),
  });
}

export function useEquityCurve() {
  return useQuery({
    queryKey: ["equity"],
    queryFn: () => apiGet<EquityPoint[]>("/api/portfolio/equity"),
  });
}

export function useAllocation() {
  return useQuery({
    queryKey: ["allocation"],
    queryFn: () => apiGet<AllocationEntry[]>("/api/portfolio/allocation"),
  });
}

export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: () => apiGet<MetricsDTO | null>("/api/portfolio/metrics"),
  });
}
