import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { accessDate } from "./lighthouse-date.mjs";

const record = (fetchTime) => ({ fetchTime });

test("earliest real instant wins independent of report order across UTC midnight", () => {
  const earlier = record("2026-11-11T22:00:00Z");
  const later = record("2026-11-12T01:00:00+02:00");
  assert.deepEqual(accessDate([later, earlier], "2026-11-20T00:00:00Z"), {
    access_date: "2026-11-11",
    access_date_source: "lighthouse_fetchTime",
  });
  assert.deepEqual(accessDate([earlier, later], "2026-11-20T00:00:00Z"), {
    access_date: "2026-11-11",
    access_date_source: "lighthouse_fetchTime",
  });
});

test("offset and fractional timestamps use their UTC date and leap day is accepted", () => {
  assert.deepEqual(accessDate([record("2026-11-11T23:30:00.500-05:00")], "2026-01-01T00:00:00Z"), {
    access_date: "2026-11-12",
    access_date_source: "lighthouse_fetchTime",
  });
  assert.deepEqual(accessDate([record("2026-11-11T00:30:00+02:00")], "2026-01-01T00:00:00Z"), {
    access_date: "2026-11-10",
    access_date_source: "lighthouse_fetchTime",
  });
  assert.deepEqual(accessDate([record("2028-02-29T12:00:00Z")], "2026-01-01T00:00:00Z"), {
    access_date: "2028-02-29",
    access_date_source: "lighthouse_fetchTime",
  });
});

test("missing, empty, numeric, garbage and partial timestamps are ignored", () => {
  const reports = [
    {},
    record(""),
    record(0),
    record(1780000000000),
    record("garbage"),
    record("2026-11-11T08:23Z"),
    record("2026-11-11"),
    record("2026-11-11T08:23:34Z"),
  ];
  assert.deepEqual(accessDate(reports, "2030-01-01T00:00:00Z"), {
    access_date: "2026-11-11",
    access_date_source: "lighthouse_fetchTime",
  });
});

test("malformed calendar days, months and hours are rejected without normalization", () => {
  for (const fetchTime of [
    "2026-02-30T00:00:00Z",
    "2026-04-31T00:00:00Z",
    "2026-13-01T00:00:00Z",
    "2026-00-10T00:00:00Z",
    "2026-01-00T00:00:00Z",
    "2026-01-01T24:00:00Z",
    "2026-01-01T00:00:00+25:00",
  ]) {
    assert.deepEqual(accessDate([record(fetchTime)], "2030-06-15T12:00:00Z"), {
      access_date: "2030-06-15",
      access_date_source: "build_time_fallback",
    });
  }
});

test("zero valid timestamps use the caller build time with an explicit fallback label", () => {
  assert.deepEqual(accessDate([], "2026-11-11T10:00:00Z"), {
    access_date: "2026-11-11",
    access_date_source: "build_time_fallback",
  });
  assert.deepEqual(accessDate([record(null), record("nope")], "2026-11-11T23:59:59Z"), {
    access_date: "2026-11-11",
    access_date_source: "build_time_fallback",
  });
});

test("mixed valid and invalid reports use the earliest valid measurement", () => {
  const reports = [
    record("not-a-time"),
    record("2026-11-12T06:00:00Z"),
    record(42),
    record("2026-11-09T20:00:00-02:00"),
    record("2026-11-11T00:00:00+03:00"),
  ];
  assert.deepEqual(accessDate(reports, "2030-01-01T00:00:00Z"), {
    access_date: "2026-11-09",
    access_date_source: "lighthouse_fetchTime",
  });
});

test("committed historical measurement reports are not rewritten", () => {
  const paths = [
    new URL("../docs/lighthouse-results.json", import.meta.url),
    new URL("../docs/lighthouse-contention.json", import.meta.url),
    new URL("../docs/browser-performance.json", import.meta.url),
    new URL("../docs/recent-history.json", import.meta.url),
  ];
  const before = paths.map((path) => readFileSync(path, "utf8"));
  accessDate([record("2026-11-11T10:00:00Z")], "2030-01-01T00:00:00Z");
  const after = paths.map((path) => readFileSync(path, "utf8"));
  assert.deepEqual(after, before);
  for (const text of after) assert.equal(JSON.parse(text).access_date, "2026-10-13");
});
