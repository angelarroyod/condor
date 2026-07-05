import type { LegInput, LegKind } from "../api/types";
import { TEMPLATE_NAMES, type TemplateName } from "../options/templates";

export interface LegRow extends LegInput {
  id: string;
}

interface Props {
  legs: LegRow[];
  onChange: (id: string, patch: Partial<LegInput>) => void;
  onRemove: (id: string) => void;
  onAdd: () => void;
  onTemplate: (name: TemplateName) => void;
}

const inputCls =
  "w-full rounded bg-terminal-bg px-1.5 py-0.5 text-xs text-slate-100 outline-none ring-1 ring-terminal-border focus:ring-terminal-up disabled:opacity-30";

export function LegEditor({ legs, onChange, onRemove, onAdd, onTemplate }: Props) {
  return (
    <div className="flex flex-col gap-2 p-3">
      <div className="flex items-center gap-2">
        <select
          value=""
          onChange={(e) => e.target.value && onTemplate(e.target.value as TemplateName)}
          className="rounded bg-terminal-bg px-2 py-1 text-xs text-slate-200 ring-1 ring-terminal-border"
        >
          <option value="">Load template…</option>
          {TEMPLATE_NAMES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={onAdd}
          className="ml-auto rounded bg-terminal-border/50 px-2 py-1 text-xs text-slate-300 hover:bg-terminal-border"
        >
          + Leg
        </button>
      </div>

      <table className="w-full text-xs">
        <thead className="text-slate-500">
          <tr className="text-left">
            <th className="py-1 font-normal">Kind</th>
            <th className="py-1 font-normal">Dir</th>
            <th className="py-1 text-right font-normal">Strike</th>
            <th className="py-1 text-right font-normal">IV</th>
            <th className="py-1 text-right font-normal">Qty</th>
            <th className="py-1" />
          </tr>
        </thead>
        <tbody>
          {legs.map((leg) => {
            const isStock = leg.kind === "stock";
            return (
              <tr key={leg.id} className="border-t border-terminal-border/50">
                <td className="py-1 pr-1">
                  <select
                    value={leg.kind}
                    onChange={(e) => onChange(leg.id, { kind: e.target.value as LegKind })}
                    className={inputCls}
                  >
                    <option value="call">call</option>
                    <option value="put">put</option>
                    <option value="stock">stock</option>
                  </select>
                </td>
                <td className="py-1 pr-1">
                  <select
                    value={leg.direction}
                    onChange={(e) =>
                      onChange(leg.id, { direction: e.target.value as "long" | "short" })
                    }
                    className={inputCls}
                  >
                    <option value="long">long</option>
                    <option value="short">short</option>
                  </select>
                </td>
                <td className="py-1 pr-1">
                  <input
                    className={`${inputCls} text-right`}
                    inputMode="decimal"
                    disabled={isStock}
                    value={isStock ? "" : leg.strike}
                    onChange={(e) => onChange(leg.id, { strike: Number(e.target.value) })}
                  />
                </td>
                <td className="py-1 pr-1">
                  <input
                    className={`${inputCls} text-right`}
                    inputMode="decimal"
                    disabled={isStock}
                    value={isStock ? "" : leg.iv}
                    onChange={(e) => onChange(leg.id, { iv: Number(e.target.value) })}
                  />
                </td>
                <td className="py-1 pr-1">
                  <input
                    className={`${inputCls} text-right`}
                    inputMode="decimal"
                    value={leg.quantity}
                    onChange={(e) => onChange(leg.id, { quantity: Number(e.target.value) })}
                  />
                </td>
                <td className="py-1 text-right">
                  <button
                    type="button"
                    onClick={() => onRemove(leg.id)}
                    className="text-slate-500 hover:text-terminal-down"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
