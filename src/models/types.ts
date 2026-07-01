// Shared domain types for the app.

/** How a food entry was captured. Drives the honesty/accuracy labelling. */
export type InputMethod = 'photo' | 'barcode' | 'manual';

/**
 * Accuracy class of a value.
 * - 'estimated': AI/vision guess, treat as ±20-30%. Never shown as exact.
 * - 'exact':     from a barcode database or manual gram entry.
 */
export type Accuracy = 'estimated' | 'exact';

/** Accuracy is a property of the input method, defined in one place. */
export const ACCURACY_BY_METHOD: Record<InputMethod, Accuracy> = {
  photo: 'estimated',
  barcode: 'exact',
  manual: 'exact',
};

export interface Macros {
  kcal: number;
  proteinG: number;
  fatG: number;
  carbsG: number;
}

/** A single logged food item. */
export interface FoodEntry extends Macros {
  id: number;
  name: string;
  /** Human-readable amount, e.g. "150 g", "1 Dose (330 ml)", "~1 Teller". */
  amount: string;
  method: InputMethod;
  accuracy: Accuracy;
  /** ISO 8601 timestamp of when it was logged. */
  loggedAt: string;
  /** For barcode entries: the scanned code, for traceability. */
  barcode?: string | null;
}

/** Payload used to create a new entry (id + timestamps assigned by the DB layer). */
export type NewFoodEntry = Omit<FoodEntry, 'id' | 'loggedAt' | 'accuracy'> & {
  loggedAt?: string;
};

// --- Profile ---

export type Sex = 'male' | 'female';
export type GoalType = 'muscle' | 'cut' | 'recomp';

export interface Profile {
  weightKg: number;
  heightCm: number;
  age: number;
  sex: Sex;
  goal: GoalType;
  /** TDEE activity multiplier (1.2 sedentary … 1.9 very heavy training). */
  activityMultiplier: number;
  /** Grams of protein per kg bodyweight target. */
  proteinPerKg: number;
  /** Free text, e.g. "16:8" or "keins". Informational only in V1. */
  fastingWindow: string;
}

/** Computed daily targets. */
export interface DailyTargets {
  kcal: number;
  proteinG: number;
  fatG: number;
  carbsG: number;
}
