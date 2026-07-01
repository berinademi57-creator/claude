// Barcode scan → Open Food Facts lookup → EXACT macros scaled to a gram amount.

import { CameraView, useCameraPermissions } from 'expo-camera';
import React, { useState } from 'react';
import { StyleSheet, Text, TextInput, View } from 'react-native';
import { AccuracyBadge } from '../components/AccuracyBadge';
import { Banner, Button, Card, Row, Screen, SectionTitle } from '../components/ui';
import { useDayLog } from '../context/DayLogContext';
import {
  BarcodeProduct,
  lookupBarcode,
  productToEntry,
} from '../services/openFoodFacts';
import { colors, radius, spacing } from '../theme';

export function BarcodeScreen({ navigation }: any) {
  const { addEntry } = useDayLog();
  const [permission, requestPermission] = useCameraPermissions();
  const [scanning, setScanning] = useState(true);
  const [loading, setLoading] = useState(false);
  const [product, setProduct] = useState<BarcodeProduct | null>(null);
  const [grams, setGrams] = useState('100');
  const [err, setErr] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function onScanned({ data }: { data: string }) {
    if (!scanning || loading) return;
    setScanning(false);
    setLoading(true);
    setErr(null);
    try {
      const p = await lookupBarcode(data);
      setProduct(p);
      if (p.servingQuantityG) setGrams(String(p.servingQuantityG));
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Fehler beim Nachschlagen.');
    } finally {
      setLoading(false);
    }
  }

  async function save() {
    if (!product) return;
    const g = parseFloat(grams);
    if (Number.isNaN(g) || g <= 0) {
      setErr('Bitte eine gültige Menge in Gramm eingeben.');
      return;
    }
    setSaving(true);
    try {
      await addEntry(productToEntry(product, g));
      navigation.navigate('Heute');
    } finally {
      setSaving(false);
    }
  }

  function rescan() {
    setProduct(null);
    setErr(null);
    setScanning(true);
  }

  if (!permission) {
    return (
      <Screen>
        <Card>
          <Text style={styles.muted}>Kamera wird initialisiert…</Text>
        </Card>
      </Screen>
    );
  }

  if (!permission.granted) {
    return (
      <Screen>
        <Card>
          <SectionTitle>Kamerazugriff nötig</SectionTitle>
          <Text style={styles.muted}>
            Zum Scannen von Barcodes wird die Kamera benötigt.
          </Text>
          <Button title="Kamera erlauben" onPress={requestPermission} />
        </Card>
      </Screen>
    );
  }

  const factor = product ? (parseFloat(grams) || 0) / 100 : 0;

  return (
    <Screen>
      <Card>
        <View style={styles.head}>
          <SectionTitle>Barcode scannen</SectionTitle>
          <AccuracyBadge accuracy="exact" />
        </View>

        {scanning ? (
          <View style={styles.cameraWrap}>
            <CameraView
              style={StyleSheet.absoluteFill}
              barcodeScannerSettings={{
                barcodeTypes: ['ean13', 'ean8', 'upc_a', 'upc_e', 'code128'],
              }}
              onBarcodeScanned={onScanned}
            />
          </View>
        ) : null}

        {loading ? <Text style={styles.muted}>Suche Produkt…</Text> : null}
        {err ? <Banner tone="error">{err}</Banner> : null}

        {product ? (
          <>
            <Text style={styles.product}>{product.name}</Text>
            <Text style={styles.muted}>Barcode: {product.barcode}</Text>

            <Text style={styles.label}>Menge (g)</Text>
            <TextInput
              style={styles.input}
              value={grams}
              onChangeText={setGrams}
              keyboardType="numeric"
            />

            <View style={styles.preview}>
              <Row
                label="Kalorien"
                value={`${Math.round(product.per100g.kcal * factor)} kcal`}
              />
              <Row
                label="Protein"
                value={`${(product.per100g.proteinG * factor).toFixed(1)} g`}
              />
              <Row
                label="Fett"
                value={`${(product.per100g.fatG * factor).toFixed(1)} g`}
              />
              <Row
                label="Kohlenhydrate"
                value={`${(product.per100g.carbsG * factor).toFixed(1)} g`}
              />
            </View>

            <Button title="Speichern" onPress={save} loading={saving} />
            <Button title="Neu scannen" variant="secondary" onPress={rescan} />
          </>
        ) : (
          !loading && (
            <Text style={styles.muted}>
              Halte den Barcode in den Kamerabereich.
            </Text>
          )
        )}
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
  cameraWrap: {
    height: 220,
    borderRadius: radius.md,
    overflow: 'hidden',
    backgroundColor: '#000',
  },
  muted: { color: colors.textMuted, fontSize: 13 },
  product: { color: colors.text, fontSize: 17, fontWeight: '800', marginTop: spacing.sm },
  label: { color: colors.textMuted, fontSize: 13, marginTop: spacing.sm },
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
  preview: {
    marginTop: spacing.sm,
    backgroundColor: colors.cardAlt,
    borderRadius: radius.md,
    padding: spacing.md,
  },
});
