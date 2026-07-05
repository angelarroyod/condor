import {
  createChart,
  type CandlestickData,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import { useCandles } from "../api/hooks";
import { usePriceStore } from "../store/prices";

const INTERVALS = ["1m", "5m", "1h", "1d"] as const;

const toTime = (iso: string): UTCTimestamp => (Date.parse(iso) / 1000) as UTCTimestamp;

export function CandleChart() {
  const selected = usePriceStore((s) => s.selected);
  const interval = usePriceStore((s) => s.interval);
  const setInterval = usePriceStore((s) => s.setInterval);
  const tick = usePriceStore((s) => (s.selected ? s.prices[s.selected] : undefined));

  const { data: candles } = useCandles(selected, interval);

  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  // Create the chart once.
  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: { background: { color: "transparent" }, textColor: "#94a3b8" },
      grid: { vertLines: { color: "#1f2733" }, horzLines: { color: "#1f2733" } },
      timeScale: { timeVisible: true, borderColor: "#1f2733" },
      rightPriceScale: { borderColor: "#1f2733" },
    });
    seriesRef.current = chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
      borderVisible: false,
    });
    chartRef.current = chart;
    return () => {
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  // Load fetched candles.
  useEffect(() => {
    if (!seriesRef.current || !candles) return;
    const data: CandlestickData[] = candles.map((c) => ({
      time: toTime(c.bucket_start),
      open: Number(c.open),
      high: Number(c.high),
      low: Number(c.low),
      close: Number(c.close),
    }));
    seriesRef.current.setData(data);
    chartRef.current?.timeScale().fitContent();
  }, [candles]);

  // Live-update the forming bar from the tick stream.
  useEffect(() => {
    const series = seriesRef.current;
    const last = candles?.at(-1);
    if (!series || !tick || !last) return;
    series.update({
      time: toTime(last.bucket_start),
      open: Number(last.open),
      high: Math.max(Number(last.high), tick.price),
      low: Math.min(Number(last.low), tick.price),
      close: tick.price,
    });
  }, [tick, candles]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-terminal-border px-3 py-2">
        <span className="text-sm font-semibold">{selected ?? "Select a symbol"}</span>
        <div className="ml-auto flex gap-1">
          {INTERVALS.map((iv) => (
            <button
              key={iv}
              type="button"
              onClick={() => setInterval(iv)}
              className={`rounded px-2 py-0.5 text-xs ${
                iv === interval ? "bg-terminal-up text-black" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {iv}
            </button>
          ))}
        </div>
      </div>
      <div ref={containerRef} className="min-h-0 flex-1" />
    </div>
  );
}
