import type { LegInput } from "../api/types";

// Templates are editable presets: they seed the legs table from the current
// spot; the user tweaks any leg afterwards. The server only ever sees legs.
const strike = (spot: number, pct: number) => Math.round(spot * (1 + pct));

export const TEMPLATE_NAMES = [
  "Long Call",
  "Long Put",
  "Covered Call",
  "Cash-Secured Put",
  "Bull Call Spread",
  "Bear Put Spread",
  "Straddle",
  "Strangle",
  "Iron Condor",
] as const;

export type TemplateName = (typeof TEMPLATE_NAMES)[number];

export function buildTemplate(name: TemplateName, spot: number, iv: number): LegInput[] {
  const call = (dir: "long" | "short", pct: number): LegInput => ({
    kind: "call",
    direction: dir,
    strike: strike(spot, pct),
    iv,
    quantity: 1,
  });
  const put = (dir: "long" | "short", pct: number): LegInput => ({
    kind: "put",
    direction: dir,
    strike: strike(spot, pct),
    iv,
    quantity: 1,
  });
  const stock: LegInput = { kind: "stock", direction: "long", strike: 0, iv: 0, quantity: 1 };

  switch (name) {
    case "Long Call":
      return [call("long", 0)];
    case "Long Put":
      return [put("long", 0)];
    case "Covered Call":
      return [stock, call("short", 0.1)];
    case "Cash-Secured Put":
      return [put("short", -0.05)];
    case "Bull Call Spread":
      return [call("long", 0), call("short", 0.1)];
    case "Bear Put Spread":
      return [put("long", 0), put("short", -0.1)];
    case "Straddle":
      return [call("long", 0), put("long", 0)];
    case "Strangle":
      return [call("long", 0.1), put("long", -0.1)];
    case "Iron Condor":
      return [put("long", -0.2), put("short", -0.1), call("short", 0.1), call("long", 0.2)];
  }
}
