// Small fetch helper with a hard timeout. Used everywhere network I/O happens
// so a hanging request can never block the UI — it rejects and the caller
// degrades gracefully (this is what keeps the core app alive when Whoop or any
// other service is slow/down).

export async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs = 10_000
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error(`Zeitüberschreitung nach ${timeoutMs / 1000}s.`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}
