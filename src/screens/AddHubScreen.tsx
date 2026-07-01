// Hub for the three input methods, each labelled by accuracy up front so the
// honesty is visible before the user even picks a method.

import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { AccuracyBadge } from '../components/AccuracyBadge';
import { Screen, SectionTitle } from '../components/ui';
import { Accuracy } from '../models/types';
import { colors, radius, spacing } from '../theme';

function MethodCard({
  title,
  desc,
  emoji,
  accuracy,
  onPress,
}: {
  title: string;
  desc: string;
  emoji: string;
  accuracy: Accuracy;
  onPress: () => void;
}) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.card, { opacity: pressed ? 0.85 : 1 }]}
    >
      <Text style={styles.emoji}>{emoji}</Text>
      <View style={styles.cardBody}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.desc}>{desc}</Text>
        <AccuracyBadge accuracy={accuracy} />
      </View>
      <Text style={styles.chevron}>›</Text>
    </Pressable>
  );
}

export function AddHubScreen({ navigation }: any) {
  return (
    <Screen>
      <SectionTitle>Wie möchtest du loggen?</SectionTitle>
      <MethodCard
        title="Foto"
        desc="Mahlzeit fotografieren – Claude schätzt die Nährwerte. Schnell, aber ungenau."
        emoji="📷"
        accuracy="estimated"
        onPress={() => navigation.navigate('Foto')}
      />
      <MethodCard
        title="Barcode"
        desc="Produkt-Barcode scannen – exakte Werte aus Open Food Facts."
        emoji="🏷️"
        accuracy="exact"
        onPress={() => navigation.navigate('Barcode')}
      />
      <MethodCard
        title="Text + Gramm"
        desc="Werte selbst eintippen – exakt, wenn du sie kennst."
        emoji="⌨️"
        accuracy="exact"
        onPress={() => navigation.navigate('Manuell')}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.md,
  },
  emoji: { fontSize: 30 },
  cardBody: { flex: 1, gap: 4 },
  title: { color: colors.text, fontSize: 17, fontWeight: '800' },
  desc: { color: colors.textMuted, fontSize: 13, lineHeight: 18 },
  chevron: { color: colors.textMuted, fontSize: 28 },
});
