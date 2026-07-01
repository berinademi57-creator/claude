// Foto → Claude Vision → ESTIMATE. Everything here is framed as a guess:
// prominent "geschätzt" labels, the model's uncertainty note, and editable
// fields so the user can correct before saving. Values are stored as 'photo'
// → accuracy 'estimated'.

import * as ImagePicker from 'expo-image-picker';
import React, { useState } from 'react';
import { Image, StyleSheet, Text, TextInput, View } from 'react-native';
import { AccuracyBadge } from '../components/AccuracyBadge';
import { Banner, Button, Card, Screen, SectionTitle } from '../components/ui';
import { useDayLog } from '../context/DayLogContext';
import {
  estimateFromPhoto,
  estimateToEntry,
  VisionEstimate,
} from '../services/claudeVision';
import { hasVisionConfig } from '../utils/config';
import { colors, radius, spacing } from '../theme';

export function PhotoScreen({ navigation }: any) {
  const { addEntry } = useDayLog();
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [est, setEst] = useState<VisionEstimate | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function pick(fromCamera: boolean) {
    setErr(null);
    setEst(null);
    const perm = fromCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      setErr('Zugriff auf Kamera/Galerie wurde nicht erlaubt.');
      return;
    }
    const result = fromCamera
      ? await ImagePicker.launchCameraAsync({ base64: true, quality: 0.5 })
      : await ImagePicker.launchImageLibraryAsync({ base64: true, quality: 0.5 });

    if (result.canceled || !result.assets?.[0]) return;
    const asset = result.assets[0];
    setImageUri(asset.uri);
    if (!asset.base64) {
      setErr('Bild konnte nicht gelesen werden.');
      return;
    }
    const mediaType = asset.mimeType ?? 'image/jpeg';
    await runEstimate(asset.base64, mediaType);
  }

  async function runEstimate(base64: string, mediaType: string) {
    setLoading(true);
    setErr(null);
    try {
      const e = await estimateFromPhoto(base64, mediaType);
      setEst(e);
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Schätzung fehlgeschlagen.');
    } finally {
      setLoading(false);
    }
  }

  function patch(field: keyof VisionEstimate, value: string) {
    if (!est) return;
    const isNum = ['kcal', 'proteinG', 'fatG', 'carbsG'].includes(field);
    setEst({ ...est, [field]: isNum ? parseFloat(value) || 0 : value });
  }

  async function save() {
    if (!est) return;
    setSaving(true);
    try {
      await addEntry(estimateToEntry(est));
      navigation.navigate('Heute');
    } finally {
      setSaving(false);
    }
  }

  return (
    <Screen>
      <Card>
        <View style={styles.head}>
          <SectionTitle>Foto schätzen</SectionTitle>
          <AccuracyBadge accuracy="estimated" />
        </View>

        <Banner tone="warn">
          Foto-Schätzung ist KEINE exakte Messung (±20-30%). Für exakte Werte
          nutze Barcode oder manuelle Eingabe. Du kannst die geschätzten Werte
          unten anpassen.
        </Banner>

        {!hasVisionConfig() ? (
          <Banner tone="info">
            Kein Anthropic API Key konfiguriert — Foto-Schätzung ist deaktiviert.
            Trage ANTHROPIC_API_KEY in .env ein (siehe README).
          </Banner>
        ) : null}

        <View style={styles.btnRow}>
          <View style={styles.btnCol}>
            <Button title="Kamera" onPress={() => pick(true)} />
          </View>
          <View style={styles.btnCol}>
            <Button title="Galerie" variant="secondary" onPress={() => pick(false)} />
          </View>
        </View>

        {imageUri ? <Image source={{ uri: imageUri }} style={styles.image} /> : null}
        {loading ? <Text style={styles.muted}>Claude schätzt die Mahlzeit…</Text> : null}
        {err ? <Banner tone="error">{err}</Banner> : null}

        {est ? (
          <>
            <Text style={styles.estTitle}>Geschätzt:</Text>
            <Field label="Mahlzeit" value={est.name} onChange={(v) => patch('name', v)} />
            <Field label="Menge (geschätzt)" value={est.amount} onChange={(v) => patch('amount', v)} />
            <Field
              label="Kalorien (kcal, geschätzt)"
              value={String(est.kcal)}
              onChange={(v) => patch('kcal', v)}
              numeric
            />
            <View style={styles.macroRow}>
              <View style={styles.macroCol}>
                <Field label="Protein" value={String(est.proteinG)} onChange={(v) => patch('proteinG', v)} numeric />
              </View>
              <View style={styles.macroCol}>
                <Field label="Fett" value={String(est.fatG)} onChange={(v) => patch('fatG', v)} numeric />
              </View>
              <View style={styles.macroCol}>
                <Field label="KH" value={String(est.carbsG)} onChange={(v) => patch('carbsG', v)} numeric />
              </View>
            </View>
            <Text style={styles.note}>ℹ︎ {est.note}</Text>
            <Button title="Als Schätzung speichern" onPress={save} loading={saving} />
          </>
        ) : null}
      </Card>
    </Screen>
  );
}

function Field({
  label,
  value,
  onChange,
  numeric,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  numeric?: boolean;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={onChange}
        keyboardType={numeric ? 'numeric' : 'default'}
        placeholderTextColor={colors.textMuted}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  head: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  muted: { color: colors.textMuted, fontSize: 13 },
  btnRow: { flexDirection: 'row', gap: spacing.sm, marginTop: spacing.sm },
  btnCol: { flex: 1 },
  image: {
    width: '100%',
    height: 200,
    borderRadius: radius.md,
    marginTop: spacing.sm,
    backgroundColor: colors.cardAlt,
  },
  estTitle: {
    color: colors.estimated,
    fontSize: 15,
    fontWeight: '800',
    marginTop: spacing.sm,
  },
  note: { color: colors.textMuted, fontSize: 12, fontStyle: 'italic' },
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
