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

const legSelect =
  "w-full rounded-md border border-lx-hair bg-lx-input px-1.5 py-[5px] text-xs text-lx-text outline-none";
const legNum =
  "w-full rounded-md border border-lx-hair bg-lx-input px-2 py-[5px] text-right font-mono text-xs text-lx-text outline-none transition-colors focus:border-lx-accent disabled:opacity-30";

export function LegEditor({ legs, onChange, onRemove, onAdd, onTemplate }: Props) {
  return (
    <>
      <div className="flex items-center gap-2.5 border-t border-lx-faint px-5 pb-2.5 pt-3.5">
        <span className="lx-label">Legs</span>
        <div className="ml-auto flex gap-2">
          <select
            value=""
            onChange={(e) => e.target.value && onTemplate(e.target.value as TemplateName)}
            className="lx-select"
          >
            <option value="">Template…</option>
            {TEMPLATE_NAMES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <button type="button" onClick={onAdd} className="lx-ghost-btn">
            + Leg
          </button>
        </div>
      </div>

      <div className="px-5 pb-4">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="lx-th w-[72px] pb-1.5 pr-2 pt-1 text-left">Kind</th>
              <th className="lx-th w-[76px] pb-1.5 pr-2 pt-1 text-left">Dir</th>
              <th className="lx-th pb-1.5 pr-2 pt-1 text-right">Strike</th>
              <th className="lx-th pb-1.5 pr-2 pt-1 text-right">IV</th>
              <th className="lx-th pb-1.5 pr-2 pt-1 text-right">Qty</th>
              <th className="pb-1.5 pt-1" />
            </tr>
          </thead>
          <tbody>
            {legs.map((leg) => {
              const isStock = leg.kind === "stock";
              const td = "border-t border-lx-faint py-[5px] pr-2";
              return (
                <tr key={leg.id}>
                  <td className={td}>
                    <select
                      value={leg.kind}
                      onChange={(e) => onChange(leg.id, { kind: e.target.value as LegKind })}
                      className={legSelect}
                    >
                      <option value="call">call</option>
                      <option value="put">put</option>
                      <option value="stock">stock</option>
                    </select>
                  </td>
                  <td className={td}>
                    <select
                      value={leg.direction}
                      onChange={(e) =>
                        onChange(leg.id, { direction: e.target.value as "long" | "short" })
                      }
                      className={legSelect}
                    >
                      <option value="long">long</option>
                      <option value="short">short</option>
                    </select>
                  </td>
                  <td className={td}>
                    <input
                      className={legNum}
                      inputMode="decimal"
                      disabled={isStock}
                      value={isStock ? "" : leg.strike}
                      onChange={(e) => onChange(leg.id, { strike: Number(e.target.value) })}
                    />
                  </td>
                  <td className={td}>
                    <input
                      className={legNum}
                      inputMode="decimal"
                      disabled={isStock}
                      value={isStock ? "" : leg.iv}
                      onChange={(e) => onChange(leg.id, { iv: Number(e.target.value) })}
                    />
                  </td>
                  <td className={td}>
                    <input
                      className={legNum}
                      inputMode="decimal"
                      value={leg.quantity}
                      onChange={(e) => onChange(leg.id, { quantity: Number(e.target.value) })}
                    />
                  </td>
                  <td className="border-t border-lx-faint py-[5px] text-right">
                    <button
                      type="button"
                      onClick={() => onRemove(leg.id)}
                      className="text-lx-text3 transition-colors hover:text-lx-down-text"
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
    </>
  );
}
