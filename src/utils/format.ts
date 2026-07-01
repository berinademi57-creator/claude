// Display formatting helpers.

export function msToHhMm(ms: number | null | undefined): string {
  if (ms == null) return '–';
  const totalMin = Math.round(ms / 60000);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return `${h}h ${m}m`;
}

export function num(v: number | null | undefined, digits = 0, unit = ''): string {
  if (v == null || Number.isNaN(v)) return '–';
  const s = digits > 0 ? v.toFixed(digits) : Math.round(v).toString();
  return unit ? `${s} ${unit}` : s;
}

export function timeHm(iso: string | null | undefined): string {
  if (!iso) return '–';
  const d = new Date(iso);
  return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}
