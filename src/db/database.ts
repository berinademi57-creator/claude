// Local persistence for food logs using expo-sqlite (async API, SDK 51+).
// This is the app's source of truth for logging and works fully offline —
// it has ZERO dependency on Whoop or any network service.

import * as SQLite from 'expo-sqlite';
import {
  ACCURACY_BY_METHOD,
  FoodEntry,
  Macros,
  NewFoodEntry,
} from '../models/types';

let dbPromise: Promise<SQLite.SQLiteDatabase> | null = null;

function getDb(): Promise<SQLite.SQLiteDatabase> {
  if (!dbPromise) {
    dbPromise = SQLite.openDatabaseAsync('calorie-tracker.db').then(async (db) => {
      await db.execAsync(`
        PRAGMA journal_mode = WAL;
        CREATE TABLE IF NOT EXISTS food_entries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          amount TEXT NOT NULL,
          kcal REAL NOT NULL,
          proteinG REAL NOT NULL,
          fatG REAL NOT NULL,
          carbsG REAL NOT NULL,
          method TEXT NOT NULL,
          accuracy TEXT NOT NULL,
          barcode TEXT,
          loggedAt TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_food_logged_at ON food_entries (loggedAt);
      `);
      return db;
    });
  }
  return dbPromise;
}

/** Insert a new food entry. Accuracy is derived from the input method here. */
export async function addFoodEntry(entry: NewFoodEntry): Promise<FoodEntry> {
  const db = await getDb();
  const loggedAt = entry.loggedAt ?? new Date().toISOString();
  const accuracy = ACCURACY_BY_METHOD[entry.method];

  const result = await db.runAsync(
    `INSERT INTO food_entries
       (name, amount, kcal, proteinG, fatG, carbsG, method, accuracy, barcode, loggedAt)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    entry.name,
    entry.amount,
    entry.kcal,
    entry.proteinG,
    entry.fatG,
    entry.carbsG,
    entry.method,
    accuracy,
    entry.barcode ?? null,
    loggedAt
  );

  return {
    id: result.lastInsertRowId,
    accuracy,
    loggedAt,
    ...entry,
  };
}

export async function deleteFoodEntry(id: number): Promise<void> {
  const db = await getDb();
  await db.runAsync('DELETE FROM food_entries WHERE id = ?', id);
}

/** Local-day boundaries [start, end) as ISO strings for the given date. */
function dayBounds(date: Date): { startIso: string; endIso: string } {
  const start = new Date(date);
  start.setHours(0, 0, 0, 0);
  const end = new Date(start);
  end.setDate(end.getDate() + 1);
  return { startIso: start.toISOString(), endIso: end.toISOString() };
}

/** All entries logged on the given local day, newest first. */
export async function getEntriesForDay(date: Date): Promise<FoodEntry[]> {
  const db = await getDb();
  const { startIso, endIso } = dayBounds(date);
  const rows = await db.getAllAsync<FoodEntry>(
    `SELECT * FROM food_entries
       WHERE loggedAt >= ? AND loggedAt < ?
       ORDER BY loggedAt DESC`,
    startIso,
    endIso
  );
  return rows;
}

/** Sum of macros for a set of entries. */
export function sumMacros(entries: Macros[]): Macros {
  return entries.reduce<Macros>(
    (acc, e) => ({
      kcal: acc.kcal + e.kcal,
      proteinG: acc.proteinG + e.proteinG,
      fatG: acc.fatG + e.fatG,
      carbsG: acc.carbsG + e.carbsG,
    }),
    { kcal: 0, proteinG: 0, fatG: 0, carbsG: 0 }
  );
}
