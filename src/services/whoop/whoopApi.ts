// Whoop data fetching. Every fetcher is individually guarded: on error it
// returns null instead of throwing, and the orchestrator uses Promise.allSettled
// so one failing endpoint never blocks the others — and none of it can block
// the core app. The caller passes a token-getter so this file stays stateless.

import { fetchWithTimeout } from '../../utils/net';
import {
  WhoopBodyMeasurement,
  WhoopCycle,
  WhoopProfile,
  WhoopRecovery,
  WhoopSleep,
  WhoopToday,
  WhoopWorkout,
} from '../../models/whoop';

const API = 'https://api.prod.whoop.com/developer/v1';

// Subset of Whoop sport ids → readable names. Unknown ids fall back gracefully.
const SPORT_NAMES: Record<number, string> = {
  0: 'Laufen',
  1: 'Radfahren',
  16: 'Fussball',
  45: 'Gewichtheben',
  48: 'Functional Fitness',
  63: 'Gehen',
  66: 'Hyrox',
  71: 'HIIT',
};

function sportName(id: number | null | undefined): string {
  if (id == null) return 'Aktivität';
  return SPORT_NAMES[id] ?? `Sport #${id}`;
}

async function whoopGet<T>(
  token: string,
  path: string,
  params: Record<string, string> = {}
): Promise<T> {
  const qs = new URLSearchParams(params).toString();
  const url = `${API}${path}${qs ? `?${qs}` : ''}`;
  const res = await fetchWithTimeout(
    url,
    { headers: { authorization: `Bearer ${token}` } },
    12_000
  );
  if (!res.ok) {
    throw new Error(`Whoop ${path} → ${res.status}`);
  }
  return (await res.json()) as T;
}

function startOfTodayIso(): string {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d.toISOString();
}

function daysAgoIso(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  d.setHours(0, 0, 0, 0);
  return d.toISOString();
}

// --- Individual fetchers (each returns null on failure) ---

interface RecordList<T> {
  records: T[];
}

async function fetchRecovery(token: string): Promise<WhoopRecovery | null> {
  try {
    const data = await whoopGet<RecordList<any>>(token, '/recovery', {
      start: daysAgoIso(1),
      limit: '5',
    });
    const rec = data.records?.[0];
    if (!rec?.score) return null;
    return {
      scorePercent: rec.score.recovery_score ?? null,
      hrvMs: rec.score.hrv_rmssd_milli ?? null,
      restingHeartRate: rec.score.resting_heart_rate ?? null,
      updatedAt: rec.updated_at ?? null,
    };
  } catch {
    return null;
  }
}

async function fetchSleep(token: string): Promise<WhoopSleep | null> {
  try {
    const data = await whoopGet<RecordList<any>>(token, '/activity/sleep', {
      start: daysAgoIso(1),
      limit: '5',
    });
    const s = data.records?.[0];
    if (!s) return null;
    const stages = s.score?.stage_summary ?? {};
    return {
      totalInBedMs: stages.total_in_bed_time_milli ?? null,
      totalSleepMs:
        stages.total_in_bed_time_milli != null && stages.total_awake_time_milli != null
          ? stages.total_in_bed_time_milli - stages.total_awake_time_milli
          : null,
      sleepScorePercent: s.score?.sleep_performance_percentage ?? null,
      stages: {
        lightMs: stages.total_light_sleep_time_milli ?? null,
        deepMs: stages.total_slow_wave_sleep_time_milli ?? null,
        remMs: stages.total_rem_sleep_time_milli ?? null,
        awakeMs: stages.total_awake_time_milli ?? null,
      },
      start: s.start ?? null,
      end: s.end ?? null,
    };
  } catch {
    return null;
  }
}

function mapCycle(c: any): WhoopCycle {
  return {
    strain: c.score?.strain ?? null,
    averageHeartRate: c.score?.average_heart_rate ?? null,
    kilojoule: c.score?.kilojoule ?? null,
    start: c.start ?? null,
    end: c.end ?? null,
  };
}

/** Returns [todayCycle, yesterdayCycle] — either may be null. */
async function fetchCycles(
  token: string
): Promise<{ today: WhoopCycle | null; yesterday: WhoopCycle | null }> {
  try {
    const data = await whoopGet<RecordList<any>>(token, '/cycle', {
      start: daysAgoIso(2),
      limit: '5',
    });
    const recs = data.records ?? [];
    return {
      today: recs[0] ? mapCycle(recs[0]) : null,
      yesterday: recs[1] ? mapCycle(recs[1]) : null,
    };
  } catch {
    return { today: null, yesterday: null };
  }
}

async function fetchWorkouts(token: string): Promise<WhoopWorkout[]> {
  try {
    const data = await whoopGet<RecordList<any>>(token, '/activity/workout', {
      start: startOfTodayIso(),
      limit: '10',
    });
    return (data.records ?? []).map((w: any) => ({
      sportName: sportName(w.sport_id),
      strain: w.score?.strain ?? null,
      durationMs:
        w.start && w.end
          ? new Date(w.end).getTime() - new Date(w.start).getTime()
          : null,
      kilojoule: w.score?.kilojoule ?? null,
      averageHeartRate: w.score?.average_heart_rate ?? null,
      maxHeartRate: w.score?.max_heart_rate ?? null,
      start: w.start ?? null,
    }));
  } catch {
    return [];
  }
}

async function fetchBody(token: string): Promise<WhoopBodyMeasurement | null> {
  try {
    const b = await whoopGet<any>(token, '/user/measurement/body');
    return {
      heightMeter: b.height_meter ?? null,
      weightKilogram: b.weight_kilogram ?? null,
      maxHeartRate: b.max_heart_rate ?? null,
    };
  } catch {
    return null;
  }
}

async function fetchProfile(token: string): Promise<WhoopProfile | null> {
  try {
    const p = await whoopGet<any>(token, '/user/profile/basic');
    return {
      firstName: p.first_name ?? null,
      lastName: p.last_name ?? null,
      email: p.email ?? null,
    };
  } catch {
    return null;
  }
}

/**
 * Assemble the full "Whoop heute" snapshot. Never throws: any part that fails
 * comes back null/empty. Returns null only if there is no access token at all.
 */
export async function fetchWhoopToday(
  getToken: () => Promise<string | null>
): Promise<WhoopToday | null> {
  const token = await getToken();
  if (!token) return null;

  const [recovery, sleep, cycles, workouts, body, profile] = await Promise.all([
    fetchRecovery(token),
    fetchSleep(token),
    fetchCycles(token),
    fetchWorkouts(token),
    fetchBody(token),
    fetchProfile(token),
  ]);

  return {
    recovery,
    sleep,
    cycle: cycles.today,
    yesterdayCycle: cycles.yesterday,
    workouts,
    body,
    profile,
    fetchedAt: new Date().toISOString(),
  };
}
