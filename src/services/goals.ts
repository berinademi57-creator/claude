// Pure functions for goal calculation and dynamic Whoop adjustment.
// No I/O here — easy to reason about and unit-test. The core app depends on
// this module; the Whoop adjustment is an OPTIONAL layer on top.

import { DailyTargets, GoalType, Profile } from '../models/types';
import { WhoopToday } from '../models/whoop';

/** Mifflin-St Jeor basal metabolic rate (kcal/day). */
export function bmrMifflin(p: Profile): number {
  const base = 10 * p.weightKg + 6.25 * p.heightCm - 5 * p.age;
  return p.sex === 'male' ? base + 5 : base - 161;
}

/** Total daily energy expenditure = BMR × activity multiplier. */
export function tdee(p: Profile): number {
  return bmrMifflin(p) * p.activityMultiplier;
}

/** Calorie delta applied for the training goal. */
const GOAL_ADJUSTMENT: Record<GoalType, number> = {
  muscle: 0.12, // lean surplus +12%
  cut: -0.18, // deficit -18%
  recomp: 0, // maintenance
};

export const GOAL_LABEL: Record<GoalType, string> = {
  muscle: 'Muskelaufbau',
  cut: 'Cutting',
  recomp: 'Recomp',
};

/**
 * Base daily targets from the profile alone (no Whoop).
 * This is what the core app uses when Whoop is unavailable.
 */
export function baseTargets(p: Profile): DailyTargets {
  const maintenance = tdee(p);
  const kcal = Math.round(maintenance * (1 + GOAL_ADJUSTMENT[p.goal]));

  const proteinG = Math.round(p.weightKg * p.proteinPerKg);
  // Fat floor ~0.8 g/kg for hormonal health; rest of energy from carbs.
  const fatG = Math.round(p.weightKg * 0.9);
  const kcalFromProtein = proteinG * 4;
  const kcalFromFat = fatG * 9;
  const carbsG = Math.max(0, Math.round((kcal - kcalFromProtein - kcalFromFat) / 4));

  return { kcal, proteinG, fatG, carbsG };
}

// --- Whoop-driven dynamic adjustment ---

export interface AdjustedTargets {
  targets: DailyTargets;
  base: DailyTargets;
  /** Human-readable German explanation shown on the Today screen. */
  explanation: string;
  /** True when Whoop meaningfully changed the numbers. */
  adjusted: boolean;
}

// Whoop recovery colour bands.
const RECOVERY_RED = 34; // < 34 = red
const RECOVERY_GREEN = 67; // >= 67 = green
// Strain 0-21 scale; ~14+ is a hard day.
const HIGH_STRAIN = 14;

/**
 * Adjust the base targets using today's Whoop data.
 *
 * Rules (from the spec):
 *  - Low recovery + high strain yesterday  → raise calories slightly (recover).
 *  - High recovery + hard training likely   → emphasise protein.
 *
 * If `whoop` is null or has no recovery score, we return the base unchanged
 * with a neutral explanation — the app keeps working without Whoop.
 */
export function adjustTargetsForWhoop(
  base: DailyTargets,
  whoop: WhoopToday | null
): AdjustedTargets {
  const recovery = whoop?.recovery?.scorePercent ?? null;

  if (recovery == null) {
    return {
      targets: base,
      base,
      adjusted: false,
      explanation:
        'Keine Whoop-Daten für heute — es gilt dein normales Tagesziel aus dem Profil.',
    };
  }

  const yesterdayStrain = whoop?.yesterdayCycle?.strain ?? null;
  const hadHardDay = yesterdayStrain != null && yesterdayStrain >= HIGH_STRAIN;

  let kcal = base.kcal;
  let proteinG = base.proteinG;
  let reason: string;

  if (recovery < RECOVERY_RED || (recovery < RECOVERY_GREEN && hadHardDay)) {
    // Body needs to recover → eat a bit more, keep protein high.
    kcal = Math.round(base.kcal * 1.08);
    proteinG = Math.round(base.proteinG * 1.05);
    reason =
      `Recovery ist niedrig (${Math.round(recovery)} %)` +
      (hadHardDay ? ` nach hohem Strain gestern (${yesterdayStrain?.toFixed(1)})` : '') +
      '. Heute leicht mehr essen und Protein hochhalten, damit dein Körper regeneriert.';
  } else if (recovery >= RECOVERY_GREEN) {
    // Green: good day to train hard → push protein for muscle building.
    proteinG = Math.round(base.proteinG * 1.1);
    reason =
      `Recovery ist hoch (${Math.round(recovery)} %). Guter Tag für intensives Training — ` +
      'Fokus heute auf dein Protein-Ziel, um den Reiz optimal zu nutzen.';
  } else {
    reason =
      `Recovery ist im mittleren Bereich (${Math.round(recovery)} %). ` +
      'Dein normales Tagesziel passt gut.';
  }

  const changed = kcal !== base.kcal || proteinG !== base.proteinG;

  // Recompute carbs to keep the macro split consistent with adjusted kcal.
  const fatG = base.fatG;
  const carbsG = Math.max(0, Math.round((kcal - proteinG * 4 - fatG * 9) / 4));

  return {
    targets: { kcal, proteinG, fatG, carbsG },
    base,
    adjusted: changed,
    explanation: reason,
  };
}
