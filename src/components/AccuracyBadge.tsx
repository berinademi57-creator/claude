// Honest accuracy label. This is the app's core promise: photo = estimate,
// barcode/manual = exact. Rendered anywhere an entry or input method is shown.

import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Accuracy, InputMethod } from '../models/types';
import { colors, radius, spacing } from '../theme';

export function AccuracyBadge({ accuracy }: { accuracy: Accuracy }) {
  const estimated = accuracy === 'estimated';
  return (
    <View
      style={[
        styles.badge,
        { backgroundColor: estimated ? '#3A2E12' : '#12332A' },
      ]}
    >
      <Text
        style={[
          styles.text,
          { color: estimated ? colors.estimated : colors.exact },
        ]}
      >
        {estimated ? '≈ geschätzt' : '✓ exakt'}
      </Text>
    </View>
  );
}

const METHOD_LABEL: Record<InputMethod, string> = {
  photo: 'Foto',
  barcode: 'Barcode',
  manual: 'Manuell',
};

export function MethodLabel({ method }: { method: InputMethod }) {
  return <Text style={styles.method}>{METHOD_LABEL[method]}</Text>;
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: radius.pill,
    alignSelf: 'flex-start',
  },
  text: { fontSize: 12, fontWeight: '700' },
  method: { color: colors.textMuted, fontSize: 12 },
});
