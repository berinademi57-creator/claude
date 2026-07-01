// Profile editor. This is where the spec's [AUSFÜLLEN] fields live — editing
// here recomputes the base daily targets immediately. Shows the derived BMR/
// TDEE/targets so the math is transparent.

import React, { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { Banner, Button, Card, Row, Screen, SectionTitle } from '../components/ui';
import { useProfile } from '../context/ProfileContext';
import { GoalType, Sex } from '../models/types';
import { bmrMifflin, GOAL_LABEL, tdee } from '../services/goals';
import { colors, radius, spacing } from '../theme';

function NumField({
  label,
  value,
  onChange,
  unit,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  unit?: string;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>
        {label}
        {unit ? ` (${unit})` : ''}
      </Text>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={onChange}
        keyboardType="numeric"
      />
    </View>
  );
}

function Chips<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { key: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <View style={styles.chips}>
      {options.map((o) => (
        <Pressable
          key={o.key}
          onPress={() => onChange(o.key)}
          style={[styles.chip, value === o.key && styles.chipActive]}
        >
          <Text style={[styles.chipText, value === o.key && styles.chipTextActive]}>
            {o.label}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}

export function ProfileScreen() {
  const { profile, updateProfile, base } = useProfile();

  const [weightKg, setWeight] = useState(String(profile.weightKg));
  const [heightCm, setHeight] = useState(String(profile.heightCm));
  const [age, setAge] = useState(String(profile.age));
  const [proteinPerKg, setProteinPerKg] = useState(String(profile.proteinPerKg));
  const [activityMultiplier, setActivity] = useState(String(profile.activityMultiplier));
  const [sex, setSex] = useState<Sex>(profile.sex);
  const [goal, setGoal] = useState<GoalType>(profile.goal);
  const [fasting, setFasting] = useState(profile.fastingWindow);
  const [saved, setSaved] = useState(false);

  // Keep local fields in sync if profile loads from DB after mount.
  useEffect(() => {
    setWeight(String(profile.weightKg));
    setHeight(String(profile.heightCm));
    setAge(String(profile.age));
    setProteinPerKg(String(profile.proteinPerKg));
    setActivity(String(profile.activityMultiplier));
    setSex(profile.sex);
    setGoal(profile.goal);
    setFasting(profile.fastingWindow);
  }, [profile]);

  async function save() {
    await updateProfile({
      weightKg: parseFloat(weightKg) || profile.weightKg,
      heightCm: parseFloat(heightCm) || profile.heightCm,
      age: parseInt(age, 10) || profile.age,
      proteinPerKg: parseFloat(proteinPerKg) || profile.proteinPerKg,
      activityMultiplier: parseFloat(activityMultiplier) || profile.activityMultiplier,
      sex,
      goal,
      fastingWindow: fasting.trim() || 'keins',
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  }

  return (
    <Screen>
      <Card>
        <SectionTitle>Profil</SectionTitle>
        <Text style={styles.muted}>
          Diese Werte bestimmen dein Basis-Tagesziel. Whoop passt es dann
          dynamisch an.
        </Text>

        <View style={styles.rowFields}>
          <View style={styles.col}>
            <NumField label="Gewicht" unit="kg" value={weightKg} onChange={setWeight} />
          </View>
          <View style={styles.col}>
            <NumField label="Grösse" unit="cm" value={heightCm} onChange={setHeight} />
          </View>
        </View>
        <View style={styles.rowFields}>
          <View style={styles.col}>
            <NumField label="Alter" value={age} onChange={setAge} />
          </View>
          <View style={styles.col}>
            <NumField label="Protein" unit="g/kg" value={proteinPerKg} onChange={setProteinPerKg} />
          </View>
        </View>

        <Text style={styles.label}>Geschlecht</Text>
        <Chips
          value={sex}
          onChange={setSex}
          options={[
            { key: 'male', label: 'Männlich' },
            { key: 'female', label: 'Weiblich' },
          ]}
        />

        <Text style={styles.label}>Ziel</Text>
        <Chips
          value={goal}
          onChange={setGoal}
          options={[
            { key: 'muscle', label: GOAL_LABEL.muscle },
            { key: 'cut', label: GOAL_LABEL.cut },
            { key: 'recomp', label: GOAL_LABEL.recomp },
          ]}
        />

        <NumField
          label="Aktivitätsfaktor"
          value={activityMultiplier}
          onChange={setActivity}
        />
        <Text style={styles.hint}>
          1.2 = wenig · 1.55 = moderat · 1.75 = viel · 1.9 = tägl. hart
        </Text>

        <View style={styles.field}>
          <Text style={styles.label}>Fasting-Fenster</Text>
          <TextInput
            style={styles.input}
            value={fasting}
            onChangeText={setFasting}
            placeholder="z.B. 16:8 oder keins"
            placeholderTextColor={colors.textMuted}
          />
        </View>

        {saved ? <Banner tone="info">Gespeichert ✓</Banner> : null}
        <Button title="Profil speichern" onPress={save} />
      </Card>

      <Card>
        <SectionTitle>Berechnetes Basisziel</SectionTitle>
        <Row label="BMR (Mifflin-St Jeor)" value={`${Math.round(bmrMifflin(profile))} kcal`} />
        <Row label="TDEE (× Aktivität)" value={`${Math.round(tdee(profile))} kcal`} />
        <Row label="Kalorienziel" value={`${base.kcal} kcal`} valueColor={colors.kcal} />
        <Row label="Protein" value={`${base.proteinG} g`} valueColor={colors.protein} />
        <Row label="Fett" value={`${base.fatG} g`} valueColor={colors.fat} />
        <Row label="Kohlenhydrate" value={`${base.carbsG} g`} valueColor={colors.carbs} />
      </Card>

      <Card>
        <Banner tone="warn">
          Hinweis: Die Formeln sind für Erwachsene ausgelegt. Mit 15 Jahren bist
          du noch im Wachstum — nutze die Zahlen als grobe Orientierung und
          besprich Cutting/Kaloriendefizite am besten mit Eltern, Arzt oder
          Trainer. Iss genug, um Training UND Wachstum zu unterstützen.
        </Banner>
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  muted: { color: colors.textMuted, fontSize: 13, marginBottom: spacing.sm },
  rowFields: { flexDirection: 'row', gap: spacing.sm },
  col: { flex: 1 },
  field: { gap: 4, marginBottom: spacing.sm },
  label: { color: colors.textMuted, fontSize: 13, marginTop: spacing.xs },
  hint: { color: colors.textMuted, fontSize: 11, marginBottom: spacing.sm },
  input: {
    backgroundColor: colors.cardAlt,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.text,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: 16,
  },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.sm },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.cardAlt,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.text, fontSize: 14, fontWeight: '600' },
  chipTextActive: { color: '#0B0F14' },
});
