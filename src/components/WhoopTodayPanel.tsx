// "Whoop heute" — shows ALL of today's raw Whoop data (not just a score), per
// the spec. Renders whatever is available; missing pieces are simply omitted.
// This component never triggers fetches itself and tolerates partial data.

import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { kjToKcal, WhoopToday } from '../models/whoop';
import { colors, spacing } from '../theme';
import { msToHhMm, num, timeHm } from '../utils/format';
import { Banner, Button, Card, Row, SectionTitle } from './ui';

function recoveryColor(pct: number | null): string {
  if (pct == null) return colors.textMuted;
  if (pct < 34) return colors.recoveryRed;
  if (pct < 67) return colors.recoveryYellow;
  return colors.recoveryGreen;
}

interface Props {
  today: WhoopToday | null;
  status: string;
  error: string | null;
  connected: boolean;
  onConnect: () => void;
  onRefresh: () => void;
  onDisconnect: () => void;
  notConfigured: boolean;
}

export function WhoopTodayPanel({
  today,
  status,
  error,
  connected,
  onConnect,
  onRefresh,
  onDisconnect,
  notConfigured,
}: Props) {
  return (
    <Card>
      <View style={styles.header}>
        <SectionTitle>Whoop heute</SectionTitle>
        {connected ? (
          <Text style={styles.refresh} onPress={onRefresh}>
            ↻ Aktualisieren
          </Text>
        ) : null}
      </View>

      {notConfigured ? (
        <Banner tone="info">
          Whoop ist optional und aktuell nicht konfiguriert. Die App funktioniert
          voll ohne Whoop. Trage WHOOP_CLIENT_ID/SECRET in .env ein, um zu
          verbinden.
        </Banner>
      ) : null}

      {!notConfigured && !connected ? (
        <>
          <Text style={styles.muted}>
            Verbinde dein Whoop-Konto, um Recovery, Schlaf, Strain und Workouts
            von heute zu sehen und dein Kalorienziel dynamisch anzupassen.
          </Text>
          <Button title="Mit Whoop verbinden" onPress={onConnect} />
        </>
      ) : null}

      {error ? <Banner tone="error">Whoop-Fehler: {error}</Banner> : null}

      {status === 'loading' ? (
        <Text style={styles.muted}>Lade Whoop-Daten…</Text>
      ) : null}

      {connected && today ? (
        <>
          {/* Recovery */}
          <View style={styles.block}>
            <Text style={styles.blockTitle}>Recovery</Text>
            <Row
              label="Score"
              value={num(today.recovery?.scorePercent, 0, '%')}
              valueColor={recoveryColor(today.recovery?.scorePercent ?? null)}
            />
            <Row label="HRV" value={num(today.recovery?.hrvMs, 0, 'ms')} />
            <Row
              label="Ruhepuls"
              value={num(today.recovery?.restingHeartRate, 0, 'bpm')}
            />
          </View>

          {/* Sleep */}
          <View style={styles.block}>
            <Text style={styles.blockTitle}>Schlaf</Text>
            <Row label="Dauer" value={msToHhMm(today.sleep?.totalSleepMs)} />
            <Row
              label="Schlaf-Score"
              value={num(today.sleep?.sleepScorePercent, 0, '%')}
            />
            <Row label="Tief" value={msToHhMm(today.sleep?.stages.deepMs)} />
            <Row label="REM" value={msToHhMm(today.sleep?.stages.remMs)} />
            <Row label="Leicht" value={msToHhMm(today.sleep?.stages.lightMs)} />
            <Row label="Wach" value={msToHhMm(today.sleep?.stages.awakeMs)} />
          </View>

          {/* Cycle / Strain */}
          <View style={styles.block}>
            <Text style={styles.blockTitle}>Tag / Strain</Text>
            <Row label="Strain heute" value={num(today.cycle?.strain, 1)} />
            <Row
              label="Ø Puls"
              value={num(today.cycle?.averageHeartRate, 0, 'bpm')}
            />
            <Row
              label="Verbrauch"
              value={num(kjToKcal(today.cycle?.kilojoule), 0, 'kcal')}
            />
            <Row
              label="Strain gestern"
              value={num(today.yesterdayCycle?.strain, 1)}
            />
          </View>

          {/* Workouts */}
          <View style={styles.block}>
            <Text style={styles.blockTitle}>
              Workouts heute ({today.workouts.length})
            </Text>
            {today.workouts.length === 0 ? (
              <Text style={styles.muted}>Noch kein Workout aufgezeichnet.</Text>
            ) : (
              today.workouts.map((w, i) => (
                <View key={i} style={styles.workout}>
                  <Text style={styles.workoutTitle}>
                    {w.sportName} · {timeHm(w.start)}
                  </Text>
                  <Row label="Dauer" value={msToHhMm(w.durationMs)} />
                  <Row label="Strain" value={num(w.strain, 1)} />
                  <Row
                    label="Kalorien"
                    value={num(kjToKcal(w.kilojoule), 0, 'kcal')}
                  />
                  <Row label="Ø Puls" value={num(w.averageHeartRate, 0, 'bpm')} />
                  <Row label="Max Puls" value={num(w.maxHeartRate, 0, 'bpm')} />
                </View>
              ))
            )}
          </View>

          {/* Body measurement */}
          {today.body ? (
            <View style={styles.block}>
              <Text style={styles.blockTitle}>Körperdaten (Whoop)</Text>
              <Row
                label="Gewicht"
                value={num(today.body.weightKilogram, 1, 'kg')}
              />
              <Row
                label="Grösse"
                value={num(
                  today.body.heightMeter != null
                    ? today.body.heightMeter * 100
                    : null,
                  0,
                  'cm'
                )}
              />
              <Row label="Max Puls" value={num(today.body.maxHeartRate, 0, 'bpm')} />
            </View>
          ) : null}

          <Text style={styles.fetched}>
            Stand: {timeHm(today.fetchedAt)} · Whoop-Modul läuft unabhängig vom
            Logging.
          </Text>
          <Button
            title="Whoop trennen"
            variant="secondary"
            onPress={onDisconnect}
          />
        </>
      ) : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  refresh: { color: colors.primary, fontSize: 13, fontWeight: '700' },
  muted: { color: colors.textMuted, fontSize: 13, lineHeight: 19 },
  block: {
    marginTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    paddingTop: spacing.sm,
    gap: 2,
  },
  blockTitle: {
    color: colors.text,
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 2,
  },
  workout: {
    marginTop: spacing.xs,
    backgroundColor: colors.cardAlt,
    borderRadius: 10,
    padding: spacing.sm,
    gap: 2,
  },
  workoutTitle: {
    color: colors.text,
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 2,
  },
  fetched: {
    color: colors.textMuted,
    fontSize: 11,
    marginTop: spacing.sm,
    fontStyle: 'italic',
  },
});
