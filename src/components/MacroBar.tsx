// Horizontal progress bar for a macro (protein / fat / carbs).

import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { colors, radius } from '../theme';

export function MacroBar({
  label,
  consumed,
  target,
  color,
  unit = 'g',
}: {
  label: string;
  consumed: number;
  target: number;
  color: string;
  unit?: string;
}) {
  const pct = target > 0 ? consumed / target : 0;
  const clamped = Math.max(0, Math.min(1, pct));
  const remaining = Math.max(0, Math.round(target - consumed));
  return (
    <View style={styles.wrap}>
      <View style={styles.labelRow}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.values}>
          {Math.round(consumed)} / {Math.round(target)} {unit}
        </Text>
      </View>
      <View style={styles.track}>
        <View
          style={[
            styles.fill,
            { width: `${clamped * 100}%`, backgroundColor: color },
          ]}
        />
      </View>
      <Text style={styles.remaining}>Noch {remaining} {unit}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 4 },
  labelRow: { flexDirection: 'row', justifyContent: 'space-between' },
  label: { color: colors.text, fontSize: 14, fontWeight: '700' },
  values: { color: colors.textMuted, fontSize: 13 },
  track: {
    height: 10,
    backgroundColor: colors.border,
    borderRadius: radius.pill,
    overflow: 'hidden',
  },
  fill: { height: '100%', borderRadius: radius.pill },
  remaining: { color: colors.textMuted, fontSize: 11 },
});
