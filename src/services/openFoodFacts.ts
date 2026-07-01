// Barcode lookup via Open Food Facts (free, no key). Returns EXACT per-portion
// macros scaled from the product's per-100g values. Network failures throw a
// friendly error; the caller shows it and the rest of the app keeps working.

import { NewFoodEntry } from '../models/types';
import { fetchWithTimeout } from '../utils/net';

const BASE = 'https://world.openfoodfacts.org/api/v2/product';

interface OffNutriments {
  ['energy-kcal_100g']?: number;
  ['proteins_100g']?: number;
  ['fat_100g']?: number;
  ['carbohydrates_100g']?: number;
}

interface OffResponse {
  status: number; // 1 = found, 0 = not found
  product?: {
    product_name?: string;
    brands?: string;
    nutriments?: OffNutriments;
    serving_quantity?: number | string;
  };
}

export interface BarcodeProduct {
  name: string;
  per100g: { kcal: number; proteinG: number; fatG: number; carbsG: number };
  servingQuantityG: number | null;
  barcode: string;
}

/** Look up a scanned barcode. Throws if not found or on network error. */
export async function lookupBarcode(barcode: string): Promise<BarcodeProduct> {
  const url = `${BASE}/${encodeURIComponent(barcode)}?fields=product_name,brands,nutriments,serving_quantity`;
  const res = await fetchWithTimeout(url, {}, 10_000);
  if (!res.ok) {
    throw new Error(`Open Food Facts antwortete mit ${res.status}.`);
  }
  const data = (await res.json()) as OffResponse;
  if (data.status !== 1 || !data.product) {
    throw new Error('Produkt nicht in der Open-Food-Facts-Datenbank gefunden.');
  }

  const n = data.product.nutriments ?? {};
  const name =
    [data.product.brands, data.product.product_name]
      .filter(Boolean)
      .join(' – ') || 'Unbekanntes Produkt';

  const serving =
    typeof data.product.serving_quantity === 'string'
      ? parseFloat(data.product.serving_quantity)
      : data.product.serving_quantity;

  return {
    name,
    per100g: {
      kcal: n['energy-kcal_100g'] ?? 0,
      proteinG: n['proteins_100g'] ?? 0,
      fatG: n['fat_100g'] ?? 0,
      carbsG: n['carbohydrates_100g'] ?? 0,
    },
    servingQuantityG: serving && !Number.isNaN(serving) ? serving : null,
    barcode,
  };
}

/** Scale a product's per-100g macros to a concrete gram amount → EXACT entry. */
export function productToEntry(
  product: BarcodeProduct,
  grams: number
): NewFoodEntry {
  const factor = grams / 100;
  const round = (v: number) => Math.round(v * factor * 10) / 10;
  return {
    name: product.name,
    amount: `${grams} g`,
    kcal: Math.round(product.per100g.kcal * factor),
    proteinG: round(product.per100g.proteinG),
    fatG: round(product.per100g.fatG),
    carbsG: round(product.per100g.carbsG),
    method: 'barcode',
    barcode: product.barcode,
  };
}
