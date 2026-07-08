import { useMemo, useState } from "react";
import { useSavedStrategies, useSaveStrategy, useStrategy } from "../api/hooks";
import type { LegInput, StrategyInput } from "../api/types";
import { GreeksPanel } from "../components/GreeksPanel";
import { LegEditor, type LegRow } from "../components/LegEditor";
import { PayoffChart } from "../components/PayoffChart";
import { buildTemplate, type TemplateName } from "../options/templates";

const withId = (leg: LegInput): LegRow => ({ ...leg, id: crypto.randomUUID() });

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
  const { data: saved } = useSavedStrategies();
  const saveStrategy = useSaveStrategy();

  const domain = useMemo((): [number, number] => {
    const strikes = legs.filter((l) => l.kind !== "stock" && l.strike > 0).map((l) => l.strike);
    const points = [...strikes, spot];
    const lo = Math.min(...points);
    const hi = Math.max(...points);
    const pad = Math.max(hi - lo, spot * 0.2);
    return [Math.max(0, lo - pad), hi + pad];
  }, [legs, spot]);

  const loadSaved = (id: string) => {
    const def = saved?.find((s) => s.id === id)?.definition;
    if (!def) return;
    setSpot(def.spot);
    setRatePct(def.rate * 100);
    setDays(Math.round(def.time_to_expiry * 365));
    setLegs(def.legs.map(withId));
  };
  const saveCurrent = () => {
    if (!input) return;
    const name = window.prompt("Save strategy as:");
    if (name) saveStrategy.mutate({ name, definition: input });
  };

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

  const field = (label: string, value: number, set: (n: number) => void, mode = "decimal") => (
    <label className="lx-label block">
      {label}
      <input
        className="lx-input"
        inputMode={mode as "decimal" | "numeric"}
        value={value}
        onChange={(e) => set(Number(e.target.value))}
      />
    </label>
  );

  return (
    <div className="grid min-h-0 flex-1 grid-cols-[404px_1fr]">
      <aside className="flex flex-col overflow-y-auto border-r border-lx-hair">
        <div className="flex items-center gap-2.5 border-b border-lx-faint px-5 py-3.5">
          <select
            value=""
            onChange={(e) => e.target.value && loadSaved(e.target.value)}
            className="lx-select min-w-0 flex-1"
          >
            <option value="">Saved strategies…</option>
            {saved?.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={saveCurrent}
            disabled={!input || saveStrategy.isPending}
            className="lx-ghost-btn disabled:opacity-40"
          >
            Save
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3 px-5 py-4">
          {field("Spot", spot, setSpot)}
          {field("Rate %", ratePct, setRatePct)}
          {field("Days to expiry", days, setDays, "numeric")}
          {field("Default IV", defaultIv, setDefaultIv)}
        </div>

        <LegEditor
          legs={legs}
          onChange={patchLeg}
          onRemove={removeLeg}
          onAdd={addLeg}
          onTemplate={applyTemplate}
        />

        {result && <GreeksPanel result={result} />}
        {isError && <p className="px-5 py-3 text-xs text-lx-down-text">{error.message}</p>}
      </aside>

      <section className="flex min-h-0 flex-col">
        <div className="flex flex-none items-center px-[22px] pb-2.5 pt-4">
          <span className="lx-label">Payoff at expiry</span>
          <span className="ml-auto text-xs text-lx-text3">
            {legs.length} {legs.length === 1 ? "leg" : "legs"} · {days}d to expiry
          </span>
        </div>
        <div className="min-h-0 flex-1 p-2">
          {result ? (
            <PayoffChart result={result} spot={spot} domain={domain} />
          ) : (
            <div className="grid h-full place-items-center text-sm text-lx-text3">
              Add a leg to see the payoff
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
