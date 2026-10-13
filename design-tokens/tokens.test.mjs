import { URL } from "node:url";
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { generate } from "./generate.mjs";
test("generated CSS matches JSON and text/control contrast meets AA", () => {
  const t = JSON.parse(
    readFileSync(new URL("tokens.json", import.meta.url), "utf8").replace(/^\uFEFF/, ""),
  );
  assert.equal(readFileSync(new URL("tokens.css", import.meta.url), "utf8"), generate(t));
  const lum = (h) => {
    const v = h
      .slice(1)
      .match(/../g)
      .map((s) => parseInt(s, 16) / 255)
      .map((n) => (n <= 0.04045 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4));
    return v[0] * 0.2126 + v[1] * 0.7152 + v[2] * 0.0722;
  };
  const ratio = (a, b) => (Math.max(lum(a), lum(b)) + 0.05) / (Math.min(lum(a), lum(b)) + 0.05);
  for (const theme of [t.dark, t.light]) {
    for (const bg of ["bg", "surface"])
      for (const ink of ["ink", "muted", "pass", "fail", "pending"])
        assert.ok(ratio(theme[bg], theme[ink]) >= 4.5, `${bg}/${ink}`);
    assert.ok(ratio(theme.accent, theme["on-accent"]) >= 4.5);
    assert.ok(ratio(theme.surface, theme.line) >= 3);
  }
});
