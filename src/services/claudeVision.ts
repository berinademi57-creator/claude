// Food photo → ESTIMATED macros via the Claude API (Vision).
//
// Honesty is the whole point: this returns an estimate (±20-30%). The result
// is stored with method 'photo' → accuracy 'estimated', and the UI must label
// it as such. We never present these numbers as exact.
//
// SECURITY: calling the Anthropic API directly from the app means the key is
// in the bundle. For V1/local use this is acceptable with a restricted key;
// for production, route this through your own backend and drop the key from
// the client (see README "Security"). If no key is configured, this throws a
// clear error and the other two (exact) input methods still work.

import { NewFoodEntry } from '../models/types';
import { config, hasVisionConfig } from '../utils/config';
import { fetchWithTimeout } from '../utils/net';

const ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages';

export interface VisionEstimate {
  name: string;
  amount: string; // estimated portion, e.g. "~150 g Hähnchen + ~200 g Reis"
  kcal: number;
  proteinG: number;
  fatG: number;
  carbsG: number;
  /** Model's confidence note, surfaced to the user for transparency. */
  note: string;
}

const SYSTEM_PROMPT = `Du bist ein Ernährungs-Schätzer. Der Nutzer schickt ein Foto einer Mahlzeit.
Schätze die Lebensmittel, die Portionsgröße und die Nährwerte.
WICHTIG: Das ist eine SCHÄTZUNG, keine exakte Messung. Sei realistisch und eher konservativ.
Antworte AUSSCHLIESSLICH mit einem JSON-Objekt in genau diesem Format, ohne Markdown, ohne Erklärtext:
{
  "name": "kurze Beschreibung der Mahlzeit auf Deutsch",
  "amount": "geschätzte Menge, z.B. '~150 g Hähnchen, ~200 g Reis'",
  "kcal": <ganze Zahl>,
  "proteinG": <Zahl>,
  "fatG": <Zahl>,
  "carbsG": <Zahl>,
  "note": "kurzer Hinweis zur Unsicherheit auf Deutsch"
}`;

interface AnthropicResponse {
  content?: Array<{ type: string; text?: string }>;
  error?: { message?: string };
}

/**
 * @param base64Image raw base64 (no data: prefix)
 * @param mediaType   e.g. 'image/jpeg' | 'image/png'
 */
export async function estimateFromPhoto(
  base64Image: string,
  mediaType: string
): Promise<VisionEstimate> {
  if (!hasVisionConfig()) {
    throw new Error(
      'Kein Anthropic API Key konfiguriert. Foto-Schätzung ist deaktiviert — nutze Barcode oder manuelle Eingabe für exakte Werte.'
    );
  }

  const res = await fetchWithTimeout(
    ANTHROPIC_URL,
    {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': config.anthropicApiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: config.anthropicModel,
        max_tokens: 512,
        system: SYSTEM_PROMPT,
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: mediaType,
                  data: base64Image,
                },
              },
              {
                type: 'text',
                text: 'Schätze die Nährwerte dieser Mahlzeit. Nur JSON.',
              },
            ],
          },
        ],
      }),
    },
    30_000
  );

  const data = (await res.json()) as AnthropicResponse;
  if (!res.ok) {
    throw new Error(data.error?.message ?? `Vision-API Fehler (${res.status}).`);
  }

  const text = data.content?.find((c) => c.type === 'text')?.text ?? '';
  const parsed = parseEstimate(text);
  return parsed;
}

/** Extract the JSON object from the model output, tolerating stray text. */
function parseEstimate(text: string): VisionEstimate {
  const match = text.match(/\{[\s\S]*\}/);
  if (!match) {
    throw new Error('Konnte die Schätzung nicht lesen. Bitte erneut versuchen.');
  }
  const raw = JSON.parse(match[0]) as Partial<VisionEstimate>;
  const num = (v: unknown) => (typeof v === 'number' && !Number.isNaN(v) ? v : 0);
  return {
    name: typeof raw.name === 'string' ? raw.name : 'Geschätzte Mahlzeit',
    amount: typeof raw.amount === 'string' ? raw.amount : 'geschätzt',
    kcal: Math.round(num(raw.kcal)),
    proteinG: Math.round(num(raw.proteinG) * 10) / 10,
    fatG: Math.round(num(raw.fatG) * 10) / 10,
    carbsG: Math.round(num(raw.carbsG) * 10) / 10,
    note: typeof raw.note === 'string' ? raw.note : 'Schätzung, ±20-30% Unsicherheit.',
  };
}

/** Convert a confirmed estimate into a storable entry (method 'photo'). */
export function estimateToEntry(est: VisionEstimate): NewFoodEntry {
  return {
    name: est.name,
    amount: est.amount,
    kcal: est.kcal,
    proteinG: est.proteinG,
    fatG: est.fatG,
    carbsG: est.carbsG,
    method: 'photo',
    barcode: null,
  };
}
