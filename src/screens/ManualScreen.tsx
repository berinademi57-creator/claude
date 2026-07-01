// Manual text + gram entry → EXACT values (user types the numbers).

import React, { useState } from 'react';
import { StyleSheet, Text, TextInput, View } from 'react-native';
import { AccuracyBadge } from '../components/AccuracyBadge';
import { Banner, Button, Card, Screen, SectionTitle } from '../components/ui';
import { useDayLog } from '../context/DayLogContext';
import { colors, radius, spacing } from '../theme';

function Field({
  label,
  value,
  onChange,
  keyboard = 'default',
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  keyboard?: 'default' | 'numeric';
  placeholder?: string;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={onChange}
        keyboardType={keyboard}
        placeholder={placeholder}
        placeholderTextColor={colors.textMuted}
      />
    </View>
  );
}

export function ManualScreen({ navigation }: any) {
  const { addEntry } = useDayLog();
  const [name, setName] = useState('');
  const [grams, setGrams] = useState('');
  const [kcal, setKcal] = useState('');
  const [protein, setProtein] = useState('');
  const [fat, setFat] = useState('');
  const [carbs, setCarbs] = useState('');
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function save() {
    setErr(null);
    if (!name.trim()) {
      setErr('Bitte einen Namen eingeben.');
      return;
    }
    const kcalN = parseFloat(kcal);
    if (Number.isNaN(kcalN)) {
      setErr('Bitte gültige Kalorien eingeben.');
      return;
    }
    setSaving(true);
    try {
      const gramsN = parseFloat(grams);
      await addEntry({
        name: name.trim(),
        amount: !Number.isNaN(gramsN) ? `${gramsN} g` : 'manuell',
        kcal: kcalN,
        proteinG: parseFloat(protein) || 0,
        fatG: parseFloat(fat) || 0,
        carbsG: parseFloat(carbs) || 0,
        method: 'manual',
        barcode: null,
      });
      navigation.navigate('Heute');
    } finally {
      setSaving(false);
    }
  }

  return (
    <Screen>
      <Card>
        <View style={styles.head}>
          <SectionTitle>Manuell eingeben</SectionTitle>
          <AccuracyBadge accuracy="exact" />
        </View>
        <Text style={styles.muted}>
          Du gibst die Werte selbst ein — diese gelten als exakt.
        </Text>

        <Field label="Lebensmittel" value={name} onChange={setName} placeholder="z.B. Magerquark" />
        <Field
          label="Menge (g, optional)"
          value={grams}
          onChange={setGrams}
          keyboard="numeric"
          placeholder="z.B. 250"
        />
        <Field label="Kalorien (kcal)" value={kcal} onChange={setKcal} keyboard="numeric" />
        <View style={styles.macroRow}>
          <View style={styles.macroCol}>
            <Field label="Protein (g)" value={protein} onChange={setProtein} keyboard="numeric" />
          </View>
          <View style={styles.macroCol}>
            <Field label="Fett (g)" value={fat} onChange={setFat} keyboard="numeric" />
          </View>
          <View style={styles.macroCol}>
            <Field label="KH (g)" value={carbs} onChange={setCarbs} keyboard="numeric" />
          </View>
        </View>

        {err ? <Banner tone="error">{err}</Banner> : null}
        <Button title="Speichern" onPress={save} loading={saving} />
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  head: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  muted: { color: colors.textMuted, fontSize: 13, marginBottom: spacing.sm },
  field: { gap: 4, marginBottom: spacing.sm },
  label: { color: colors.textMuted, fontSize: 13 },
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
  macroRow: { flexDirection: 'row', gap: spacing.sm },
  macroCol: { flex: 1 },
});
