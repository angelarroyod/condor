// Wire DTOs. Pydantic v2 serializes Decimal as a JSON string, so prices arrive
// as strings and are coerced with Number() at the render edge.
export interface SymbolInfo {
  id: number;
  symbol: string;
  name: string;
  asset_class: string;
  provider: string;
}

export type Side = "buy" | "sell";
export type OrderType = "market" | "limit";

export interface OrderCreate {
  symbol: string;
  side: Side;
  type: OrderType;
  quantity: string;
  limit_price?: string;
  idempotency_key: string;
}

export interface OrderDTO {
  id: string;
  symbol_id: number;
  side: string;
  type: string;
  quantity: string;
  limit_price: string | null;
  filled_quantity: string;
  avg_fill_price: string | null;
  status: string;
  reject_reason: string | null;
  created_at: string;
}

export interface PositionDTO {
  symbol: string;
  quantity: string;
  avg_price: string;
  realized_pnl: string;
  mark_price: string | null;
  unrealized_pnl: string | null;
}

export interface AccountDTO {
  id: string;
  label: string;
  cash_balance: string;
  equity: string;
}

// --- Options analytics ---
export type LegKind = "call" | "put" | "stock";

export interface GreeksDTO {
  delta: number;
  gamma: number;
  vega: number;
  theta: number;
  rho: number;
}

export interface LegInput {
  kind: LegKind;
  direction: "long" | "short";
  strike: number;
  iv: number;
  quantity: number;
}

export interface StrategyInput {
  legs: LegInput[];
  spot: number;
  rate: number;
  time_to_expiry: number;
  dividend_yield: number;
}

export interface PayoffPoint {
  spot: number;
  pnl: number;
}

export interface StrategyResult {
  legs: { premium: number; greeks: GreeksDTO }[];
  net_premium: number;
  theoretical_value: number;
  aggregate: GreeksDTO;
  payoff: PayoffPoint[];
  breakevens: number[];
  max_profit: number;
  max_loss: number;
  max_profit_unbounded: boolean;
  max_loss_unbounded: boolean;
}

export interface CandleDTO {
  bucket_start: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: string;
  trade_count: number;
}

export interface QuoteDTO {
  symbol: string;
  price: string;
  ts: string;
}
