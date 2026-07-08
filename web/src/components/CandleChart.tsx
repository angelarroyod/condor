import {
  createChart,
  type CandlestickData,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import { useCandles, useSymbols } from "../api/hooks";
import { usePriceStore } from "../store/prices";

const INTERVALS = ["1m", "5m", "1h", "1d"] as const;

const toTime = (iso: string): UTCTimestamp => (Date.parse(iso) / 1000) as UTCTimestamp;
const fmt = (n: number) => n.toLocaleString(undefined, { maximumFractionDigits: 2 });

export function CandleChart() {
  const selected = usePriceStore((s) => s.selected);
  const interval = usePriceStore((s) => s.interval);
  const setInterval = usePriceStore((s) => s.setInterval);
  const tick = usePriceStore((s) => (s.selected ? s.prices[s.selected] : undefined));

  const { data: candles } = useCandles(selected, interval);
  const { data: symbols } = useSymbols();
  const name = symbols?.find((s) => s.symbol === selected)?.name ?? "";

  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: { background: { color: "transparent" }, textColor: "#6E6759" },
      grid: {
        vertLines: { color: "rgba(214,200,176,0.055)" },
        horzLines: { color: "rgba(214,200,176,0.055)" },
      },
      timeScale: { timeVisible: true, borderColor: "rgba(214,200,176,0.1)" },
      rightPriceScale: { borderColor: "rgba(214,200,176,0.1)" },
      crosshair: { horzLine: { color: "#C9A66B" }, vertLine: { color: "#C9A66B" } },
    });
    seriesRef.current = chart.addCandlestickSeries({
      upColor: "#3E8E72",
      downColor: "#B05244",
      wickUpColor: "#3E8E72",
      wickDownColor: "#B05244",
      borderVisible: false,
    });
    chartRef.current = chart;
    return () => {
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

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
      <div className="flex flex-none items-center gap-4 border-b border-lx-hair px-[22px] py-[11px]">
        <div className="flex flex-col">
          <span className="text-base font-semibold leading-tight text-lx-bright">
            {selected ?? "Select a symbol"}
          </span>
          <span className="text-[11px] text-lx-text3">{name}</span>
        </div>
        {tick && <span className="num text-base text-lx-bright">{fmt(tick.price)}</span>}
        <div className="ml-auto flex gap-0.5">
          {INTERVALS.map((iv) => (
            <button
              key={iv}
              type="button"
              onClick={() => setInterval(iv)}
              className={`num rounded-md px-[11px] py-1 text-xs transition-colors ${
                iv === interval
                  ? "bg-lx-accent-dim text-lx-accent-bright"
                  : "text-lx-text3 hover:text-lx-text2"
              }`}
            >
              {iv}
            </button>
          ))}
        </div>
      </div>
      <div className="min-h-0 flex-1" ref={containerRef} />
    </div>
  );
}
