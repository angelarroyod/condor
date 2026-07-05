import { useMemo, useState } from "react";
import { useStrategy } from "../api/hooks";
import type { LegInput, StrategyInput } from "../api/types";
import { GreeksPanel } from "../components/GreeksPanel";
import { LegEditor, type LegRow } from "../components/LegEditor";
import { PayoffChart } from "../components/PayoffChart";
import { buildTemplate, type TemplateName } from "../options/templates";

const withId = (leg: LegInput): LegRow => ({ ...leg, id: crypto.randomUUID() });

const numberInput =
  "w-full rounded bg-terminal-bg px-2 py-1 text-sm text-slate-100 outline-none ring-1 ring-terminal-border focus:ring-terminal-up";

export function StrategyLab() {
  const [spot, setSpot] = useState(100);
  const [ratePct, setRatePct] = useState(5);
  const [days, setDays] = useState(30);
  const [defaultIv, setDefaultIv] = useState(0.5);
  const [legs, setLegs] = useState<LegRow[]>(() =>
    buildTemplate("Bull Call Spread", 100, 0.5).map(withId),
  );

  const input: StrategyInput | null = useMemo(() => {
    if (legs.length === 0 || spot <= 0 || days <= 0) return null;
    return {
      legs: legs.map(({ id: _id, ...leg }) => leg),
      spot,
      rate: ratePct / 100,
      time_to_expiry: days / 365,
      dividend_yield: 0,
    };
  }, [legs, spot, ratePct, days]);

  const { data: result, isError, error } = useStrategy(input);

  // Payoff view window: strikes + spot, padded so the flat tails stay visible.
  const domain = useMemo((): [number, number] => {
    const strikes = legs.filter((l) => l.kind !== "stock" && l.strike > 0).map((l) => l.strike);
    const points = [...strikes, spot];
    const lo = Math.min(...points);
    const hi = Math.max(...points);
    const pad = Math.max(hi - lo, spot * 0.2);
    return [Math.max(0, lo - pad), hi + pad];
  }, [legs, spot]);

  const patchLeg = (id: string, patch: Partial<LegInput>) =>
    setLegs((rows) => rows.map((r) => (r.id === id ? { ...r, ...patch } : r)));
  const removeLeg = (id: string) => setLegs((rows) => rows.filter((r) => r.id !== id));
  const addLeg = () =>
    setLegs((rows) => [
      ...rows,
      withId({ kind: "call", direction: "long", strike: Math.round(spot), iv: defaultIv, quantity: 1 }),
    ]);
  const applyTemplate = (name: TemplateName) =>
    setLegs(buildTemplate(name, spot, defaultIv).map(withId));

  return (
    <div className="grid min-h-0 flex-1 grid-cols-[380px_1fr]">
      <aside className="flex flex-col overflow-y-auto border-r border-terminal-border">
        <div className="grid grid-cols-2 gap-2 p-3">
          <label className="text-xs text-slate-500">
            Spot
            <input
              className={`mt-1 ${numberInput}`}
              inputMode="decimal"
              value={spot}
              onChange={(e) => setSpot(Number(e.target.value))}
            />
          </label>
          <label className="text-xs text-slate-500">
            Rate %
            <input
              className={`mt-1 ${numberInput}`}
              inputMode="decimal"
              value={ratePct}
              onChange={(e) => setRatePct(Number(e.target.value))}
            />
          </label>
          <label className="text-xs text-slate-500">
            Days to expiry
            <input
              className={`mt-1 ${numberInput}`}
              inputMode="numeric"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
            />
          </label>
          <label className="text-xs text-slate-500">
            Default IV
            <input
              className={`mt-1 ${numberInput}`}
              inputMode="decimal"
              value={defaultIv}
              onChange={(e) => setDefaultIv(Number(e.target.value))}
            />
          </label>
        </div>

        <div className="border-t border-terminal-border" />
        <LegEditor
          legs={legs}
          onChange={patchLeg}
          onRemove={removeLeg}
          onAdd={addLeg}
          onTemplate={applyTemplate}
        />
        <div className="border-t border-terminal-border" />
        {result && <GreeksPanel result={result} />}
        {isError && <p className="p-3 text-xs text-terminal-down">{error.message}</p>}
      </aside>

      <section className="min-h-0 p-2">
        {result ? (
          <PayoffChart result={result} spot={spot} domain={domain} />
        ) : (
          <div className="grid h-full place-items-center text-sm text-slate-600">
            Add a leg to see the payoff
          </div>
        )}
      </section>
    </div>
  );
}
