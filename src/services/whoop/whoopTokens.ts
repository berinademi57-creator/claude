// Whoop OAuth2 token storage + exchange/refresh.
//
// Tokens are stored in expo-secure-store (Keychain / Keystore), never in plain
// storage. The confidential token exchange prefers a backend PROXY (so the
// client never holds the secret); if no proxy is configured it falls back to a
// direct exchange using a local-dev secret. Either way, this module isolates
// all token concerns so the rest of the app just asks for a valid access token.

import * as SecureStore from 'expo-secure-store';
import { config } from '../../utils/config';
import { fetchWithTimeout } from '../../utils/net';

export const WHOOP_AUTH_ENDPOINT = 'https://api.prod.whoop.com/oauth/oauth2/auth';
export const WHOOP_TOKEN_ENDPOINT = 'https://api.prod.whoop.com/oauth/oauth2/token';

// `offline` is required to receive a refresh token.
export const WHOOP_SCOPES = [
  'offline',
  'read:recovery',
  'read:cycles',
  'read:sleep',
  'read:workout',
  'read:profile',
  'read:body_measurement',
];

const STORE_KEY = 'whoop_tokens_v1';

interface StoredTokens {
  accessToken: string;
  refreshToken: string | null;
  /** epoch ms when the access token expires */
  expiresAt: number;
}

interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  expires_in: number; // seconds
  error?: string;
  error_description?: string;
}

async function save(tokens: StoredTokens): Promise<void> {
  await SecureStore.setItemAsync(STORE_KEY, JSON.stringify(tokens));
}

async function load(): Promise<StoredTokens | null> {
  const raw = await SecureStore.getItemAsync(STORE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredTokens;
  } catch {
    return null;
  }
}

export async function clearTokens(): Promise<void> {
  await SecureStore.deleteItemAsync(STORE_KEY);
}

export async function isConnected(): Promise<boolean> {
  return (await load()) !== null;
}

function toStored(res: TokenResponse): StoredTokens {
  return {
    accessToken: res.access_token,
    refreshToken: res.refresh_token ?? null,
    // refresh 60s early to avoid edge-of-expiry failures
    expiresAt: Date.now() + (res.expires_in - 60) * 1000,
  };
}

/** Build the params for a token request, routed via proxy or done directly. */
async function requestToken(
  params: Record<string, string>
): Promise<TokenResponse> {
  // Preferred path: your backend proxy holds the secret and does the exchange.
  if (config.whoopTokenProxyUrl) {
    const res = await fetchWithTimeout(
      config.whoopTokenProxyUrl,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(params),
      },
      15_000
    );
    const data = (await res.json()) as TokenResponse;
    if (!res.ok || data.error) {
      throw new Error(data.error_description ?? data.error ?? `Proxy-Fehler ${res.status}`);
    }
    return data;
  }

  // Local-dev fallback: direct confidential exchange with client secret.
  if (!config.whoopClientSecret) {
    throw new Error(
      'Whoop nicht vollständig konfiguriert: weder WHOOP_TOKEN_PROXY_URL noch WHOOP_CLIENT_SECRET gesetzt.'
    );
  }
  const body = new URLSearchParams({
    ...params,
    client_id: config.whoopClientId,
    client_secret: config.whoopClientSecret,
  });
  const res = await fetchWithTimeout(
    WHOOP_TOKEN_ENDPOINT,
    {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    },
    15_000
  );
  const data = (await res.json()) as TokenResponse;
  if (!res.ok || data.error) {
    throw new Error(data.error_description ?? data.error ?? `Token-Fehler ${res.status}`);
  }
  return data;
}

/** Exchange an authorization code (from the OAuth redirect) for tokens. */
export async function exchangeCode(
  code: string,
  redirectUri: string,
  codeVerifier?: string
): Promise<void> {
  const params: Record<string, string> = {
    grant_type: 'authorization_code',
    code,
    redirect_uri: redirectUri,
  };
  if (codeVerifier) params.code_verifier = codeVerifier;
  const res = await requestToken(params);
  await save(toStored(res));
}

/** Refresh using the stored refresh token. Clears tokens if refresh fails. */
async function refresh(stored: StoredTokens): Promise<StoredTokens> {
  if (!stored.refreshToken) {
    await clearTokens();
    throw new Error('Kein Refresh-Token vorhanden — bitte Whoop neu verbinden.');
  }
  try {
    const res = await requestToken({
      grant_type: 'refresh_token',
      refresh_token: stored.refreshToken,
      scope: WHOOP_SCOPES.join(' '),
    });
    const next = toStored(res);
    // Whoop may not return a new refresh token; keep the old one if so.
    if (!next.refreshToken) next.refreshToken = stored.refreshToken;
    await save(next);
    return next;
  } catch (err) {
    await clearTokens();
    throw err;
  }
}

/**
 * Get a valid access token, refreshing if expired.
 * Returns null if not connected — callers treat null as "Whoop unavailable"
 * and continue without it.
 */
export async function getValidAccessToken(): Promise<string | null> {
  const stored = await load();
  if (!stored) return null;
  if (Date.now() < stored.expiresAt) return stored.accessToken;
  const refreshed = await refresh(stored);
  return refreshed.accessToken;
}
