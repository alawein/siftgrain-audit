const ISO_DATETIME = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(Z|[+-]\d{2}:\d{2})$/;

function isLeapYear(year) {
  return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
}

function daysInMonth(year, month) {
  if (month === 2) return isLeapYear(year) ? 29 : 28;
  return [4, 6, 9, 11].includes(month) ? 30 : 31;
}

function instantOf(value) {
  if (typeof value !== "string") return null;
  const match = ISO_DATETIME.exec(value);
  if (!match) return null;
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const hour = Number(match[4]);
  const minute = Number(match[5]);
  const second = Number(match[6]);
  const zone = match[7];
  if (month < 1 || month > 12 || day < 1 || day > daysInMonth(year, month)) return null;
  if (hour > 23 || minute > 59 || second > 59) return null;
  if (zone !== "Z") {
    const [zoneHour, zoneMinute] = zone.slice(1).split(":").map(Number);
    if (zoneHour > 23 || zoneMinute > 59) return null;
  }
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function accessDate(reports, buildTime) {
  const instants = (Array.isArray(reports) ? reports : [])
    .map((report) => instantOf(report && report.fetchTime))
    .filter((instant) => instant !== null);
  if (instants.length > 0) {
    return {
      access_date: new Date(Math.min(...instants)).toISOString().slice(0, 10),
      access_date_source: "lighthouse_fetchTime",
    };
  }
  return {
    access_date: new Date(buildTime).toISOString().slice(0, 10),
    access_date_source: "build_time_fallback",
  };
}
