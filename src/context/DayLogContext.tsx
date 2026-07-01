// Today's food log state, shared across screens. Pure local SQLite — the core
// logging loop that must always work, Whoop or not.

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  addFoodEntry,
  deleteFoodEntry,
  getEntriesForDay,
  sumMacros,
} from '../db/database';
import { FoodEntry, Macros, NewFoodEntry } from '../models/types';

interface DayLogContextValue {
  entries: FoodEntry[];
  consumed: Macros;
  loading: boolean;
  reload: () => Promise<void>;
  addEntry: (entry: NewFoodEntry) => Promise<void>;
  removeEntry: (id: number) => Promise<void>;
}

const DayLogContext = createContext<DayLogContextValue | undefined>(undefined);

export function DayLogProvider({ children }: { children: React.ReactNode }) {
  const [entries, setEntries] = useState<FoodEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const rows = await getEntriesForDay(new Date());
      setEntries(rows);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const addEntry = useCallback(
    async (entry: NewFoodEntry) => {
      await addFoodEntry(entry);
      await reload();
    },
    [reload]
  );

  const removeEntry = useCallback(
    async (id: number) => {
      await deleteFoodEntry(id);
      await reload();
    },
    [reload]
  );

  const consumed = useMemo(() => sumMacros(entries), [entries]);

  const value = useMemo(
    () => ({ entries, consumed, loading, reload, addEntry, removeEntry }),
    [entries, consumed, loading, reload, addEntry, removeEntry]
  );

  return <DayLogContext.Provider value={value}>{children}</DayLogContext.Provider>;
}

export function useDayLog(): DayLogContextValue {
  const ctx = useContext(DayLogContext);
  if (!ctx) throw new Error('useDayLog must be used within DayLogProvider');
  return ctx;
}
