// Tagesübersicht: rings + macros + Whoop raw data + dynamic goal explanation
// + today's log. This screen composes the core (profile + log) with the
// optional Whoop layer, but renders fully even when Whoop is absent.

import React, { useMemo } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { AccuracyBadge, MethodLabel } from '../components/AccuracyBadge';
import { MacroBar } from '../components/MacroBar';
import { MacroRing } from '../components/MacroRing';
import { Banner, Card, Row, Screen, SectionTitle } from '../components/ui';
import { WhoopTodayPanel } from '../components/WhoopTodayPanel';
import { useDayLog } from '../context/DayLogContext';
import { useProfile } from '../context/ProfileContext';
import { useWhoop } from '../context/WhoopContext';
import { adjustTargetsForWhoop, GOAL_LABEL } from '../services/goals';
import { colors, spacing } from '../theme';
import { timeHm } from '../utils/format';

export function TodayScreen() {
  const { base, profile } = useProfile();
  const { consumed, entries, removeEntry } = useDayLog();
  const whoop = useWhoop();

  // Combine base (profile) targets with the optional Whoop adjustment.
  const adjusted = useMemo(
    () => adjustTargetsForWhoop(base, whoop.today),
    [base, whoop.today]
  );
  const targets = adjusted.targets;

  const kcalRemaining = Math.max(0, Math.round(targets.kcal - consumed.kcal));
  const proteinRemaining = Math.max(
    0,
    Math.round(targets.proteinG - consumed.proteinG)
  );

  return (
    <Screen>
      {/* Rings */}
      <Card style={styles.center}>
        <SectionTitle>Heute</SectionTitle>
        <MacroRing
          progress={targets.kcal > 0 ? consumed.kcal / targets.kcal : 0}
          color={colors.kcal}
          label="kcal"
          value={`${Math.round(consumed.kcal)}`}
          sub={`Ziel ${targets.kcal}`}
        />
        <Text style={styles.remainingBig}>
          Noch {kcalRemaining} kcal · {proteinRemaining} g Protein übrig
        </Text>
      </Card>

      {/* Macro bars */}
      <Card>
        <MacroBar
          label="Protein"
          consumed={consumed.proteinG}
          target={targets.proteinG}
          color={colors.protein}
        />
        <MacroBar
          label="Fett"
          consumed={consumed.fatG}
          target={targets.fatG}
          color={colors.fat}
        />
        <MacroBar
          label="Kohlenhydrate"
          consumed={consumed.carbsG}
          target={targets.carbsG}
          color={colors.carbs}
        />
      </Card>

      {/* Dynamic goal explanation */}
      <Card>
        <SectionTitle>Dein Ziel heute</SectionTitle>
        <Text style={styles.goalLine}>
          {GOAL_LABEL[profile.goal]} · {targets.kcal} kcal · {targets.proteinG} g
          Protein
        </Text>
        <Banner tone={adjusted.adjusted ? 'warn' : 'info'}>
          {whoop.today
            ? `Basierend auf deiner Recovery${
                whoop.today.recovery?.scorePercent != null
                  ? ` (${Math.round(whoop.today.recovery.scorePercent)}%)`
                  : ''
              } → heutiges Ziel: ${targets.kcal} kcal. ${adjusted.explanation}`
            : adjusted.explanation}
        </Banner>
        {adjusted.adjusted ? (
          <Text style={styles.baseNote}>
            Profil-Basisziel: {adjusted.base.kcal} kcal / {adjusted.base.proteinG} g
            Protein (ohne Whoop-Anpassung).
          </Text>
        ) : null}
      </Card>

      {/* Whoop raw data */}
      <WhoopTodayPanel
        today={whoop.today}
        status={whoop.status}
        error={whoop.error}
        connected={whoop.status === 'ready' || whoop.status === 'loading'}
        notConfigured={whoop.status === 'not_configured'}
        onConnect={whoop.connect}
        onRefresh={whoop.refresh}
        onDisconnect={whoop.disconnect}
      />

      {/* Today's log */}
      <Card>
        <SectionTitle>Einträge heute ({entries.length})</SectionTitle>
        {entries.length === 0 ? (
          <Text style={styles.muted}>
            Noch nichts geloggt. Tippe unten auf „Hinzufügen“.
          </Text>
        ) : (
          entries.map((e) => (
            <View key={e.id} style={styles.entry}>
              <View style={styles.entryHead}>
                <Text style={styles.entryName}>{e.name}</Text>
                <Text
                  style={styles.delete}
                  onPress={() => removeEntry(e.id)}
                >
                  ✕
                </Text>
              </View>
              <View style={styles.entryMeta}>
                <AccuracyBadge accuracy={e.accuracy} />
                <MethodLabel method={e.method} />
                <Text style={styles.time}>{timeHm(e.loggedAt)}</Text>
              </View>
              <Row
                label={e.amount}
                value={`${Math.round(e.kcal)} kcal · ${Math.round(
                  e.proteinG
                )}P / ${Math.round(e.fatG)}F / ${Math.round(e.carbsG)}K`}
              />
            </View>
          ))
        )}
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: { alignItems: 'center' },
  remainingBig: {
    color: colors.text,
    fontSize: 15,
    fontWeight: '700',
    marginTop: spacing.sm,
    textAlign: 'center',
  },
  goalLine: { color: colors.text, fontSize: 15, fontWeight: '700' },
  baseNote: { color: colors.textMuted, fontSize: 12 },
  muted: { color: colors.textMuted, fontSize: 13 },
  entry: {
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.sm,
    marginTop: spacing.sm,
    gap: 4,
  },
  entryHead: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  entryName: { color: colors.text, fontSize: 16, fontWeight: '700', flex: 1 },
  delete: { color: colors.danger, fontSize: 16, paddingHorizontal: spacing.sm },
  entryMeta: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  time: { color: colors.textMuted, fontSize: 12 },
});
