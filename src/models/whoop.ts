// Whoop domain types. These mirror the fields the app actually displays.
// Everything is optional because the Whoop module must degrade gracefully:
// any missing piece simply is not shown, and never blocks the core app.

export interface WhoopRecovery {
  scorePercent: number | null; // 0-100 recovery %
  hrvMs: number | null; // heart rate variability (rMSSD) in ms
  restingHeartRate: number | null; // bpm
  updatedAt: string | null;
}

export interface WhoopSleepStages {
  lightMs: number | null;
  deepMs: number | null;
  remMs: number | null;
  awakeMs: number | null;
}

export interface WhoopSleep {
  totalInBedMs: number | null;
  totalSleepMs: number | null;
  sleepScorePercent: number | null; // "sleep performance" %
  stages: WhoopSleepStages;
  start: string | null;
  end: string | null;
}

export interface WhoopCycle {
  strain: number | null; // 0-21 day strain
  averageHeartRate: number | null; // bpm
  kilojoule: number | null; // energy expended (Whoop reports kJ)
  start: string | null;
  end: string | null;
}

export interface WhoopWorkout {
  sportName: string | null;
  strain: number | null;
  durationMs: number | null;
  kilojoule: number | null; // energy of the workout
  averageHeartRate: number | null;
  maxHeartRate: number | null;
  start: string | null;
}

export interface WhoopBodyMeasurement {
  heightMeter: number | null;
  weightKilogram: number | null;
  maxHeartRate: number | null;
}

export interface WhoopProfile {
  firstName: string | null;
  lastName: string | null;
  email: string | null;
}

/** Aggregate of everything the "Whoop heute" panel shows. */
export interface WhoopToday {
  recovery: WhoopRecovery | null;
  sleep: WhoopSleep | null;
  cycle: WhoopCycle | null; // today's cycle (strain so far)
  yesterdayCycle: WhoopCycle | null; // used for "high strain yesterday" logic
  workouts: WhoopWorkout[];
  body: WhoopBodyMeasurement | null;
  profile: WhoopProfile | null;
  fetchedAt: string;
}

/** 1 kilojoule = 0.239006 kcal */
export function kjToKcal(kj: number | null | undefined): number | null {
  if (kj == null) return null;
  return Math.round(kj * 0.239006);
}
