import { readFileSync, writeFileSync } from "node:fs";
import process from "node:process";
import { URL } from "node:url";
import { fileURLToPath } from "node:url";
export function generate(t) {
  const vars = (o, p = "") =>
    Object.entries(o)
      .map(([k, v]) => `--${p}${k}:${v};`)
      .join("");
  return (
    `/* Generated from tokens.json; edit the JSON owner. */\n:root{${vars(t.dark)}${vars(t.space, "space-")}${vars(t.type, "font-")}--sw-bg:var(--bg);--sw-panel:var(--surface);--sw-text:var(--ink);--sw-muted:var(--muted);--sw-accent:var(--accent);--sw-good:var(--pass);--sw-bad:var(--fail);--sw-warn:var(--pending);color-scheme:dark;}\n[data-theme="light"],[data-appearance="light"]{${vars(t.light)}color-scheme:light;}\n` +
    Object.entries(t.vibes)
      .map(([k, v]) => `[data-vibe="${k}"]{${vars(v)}}`)
      .join("\n") +
    "\n"
  );
}
if (process.argv[1] === fileURLToPath(import.meta.url))
  writeFileSync(
    new URL("tokens.css", import.meta.url),
    generate(
      JSON.parse(
        readFileSync(new URL("tokens.json", import.meta.url), "utf8").replace(/^\uFEFF/, ""),
      ),
    ),
  );
