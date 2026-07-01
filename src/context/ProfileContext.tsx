// Profile state + persistence. The profile drives base goal calculation and is
// fully editable in-app (the spec's [AUSFÜLLEN] fields are entered here). Seeded
// with sensible defaults for a heavy-training athlete so the app works on first
// launch before the user customises it.

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { getSetting, setSetting } from '../db/settingsStore';
import { DailyTargets, Profile } from '../models/types';
import { baseTargets } from '../services/goals';

const PROFILE_KEY = 'profile_v1';

// Defaults from the user's own details: 74 kg, 178 cm, 15 y, trains daily
// (Hyrox / Gym / Ironman-style / Joggen) → very high activity, goal = recomp
// ("Muskel aufbauen + shredden"). All editable in the Profile screen.
export const DEFAULT_PROFILE: Profile = {
  weightKg: 74,
  heightCm: 178,
  age: 15,
  sex: 'male',
  goal: 'recomp', // Muskelaufbau + gleichzeitig shredden
  activityMultiplier: 1.9, // tägliches intensives Training (Hyrox/Gym/Cardio)
  proteinPerKg: 2.0,
  fastingWindow: 'keins',
};

interface ProfileContextValue {
  profile: Profile;
  loading: boolean;
  updateProfile: (patch: Partial<Profile>) => Promise<void>;
  base: DailyTargets;
}

const ProfileContext = createContext<ProfileContextValue | undefined>(undefined);

export function ProfileProvider({ children }: { children: React.ReactNode }) {
  const [profile, setProfile] = useState<Profile>(DEFAULT_PROFILE);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const saved = await getSetting<Profile>(PROFILE_KEY);
      if (saved) setProfile({ ...DEFAULT_PROFILE, ...saved });
      setLoading(false);
    })();
  }, []);

  async function updateProfile(patch: Partial<Profile>) {
    const next = { ...profile, ...patch };
    setProfile(next);
    await setSetting(PROFILE_KEY, next);
  }

  const base = useMemo(() => baseTargets(profile), [profile]);

  const value = useMemo(
    () => ({ profile, loading, updateProfile, base }),
    [profile, loading, base]
  );

  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile(): ProfileContextValue {
  const ctx = useContext(ProfileContext);
  if (!ctx) throw new Error('useProfile must be used within ProfileProvider');
  return ctx;
}
