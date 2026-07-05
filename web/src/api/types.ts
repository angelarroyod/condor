// Wire DTOs. Pydantic v2 serializes Decimal as a JSON string, so prices arrive
// as strings and are coerced with Number() at the render edge.
export interface SymbolInfo {
  symbol: string;
  name: string;
  asset_class: string;
  provider: string;
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
