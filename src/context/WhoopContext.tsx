// Whoop connection + data as an ISOLATED module. Design rule: nothing here can
// block the core app. All fetches are guarded and non-fatal; if Whoop is
// unavailable, `today` is simply null and the app runs on profile-based goals.

import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { WhoopToday } from '../models/whoop';
import { fetchWhoopToday } from '../services/whoop/whoopApi';
import {
  clearTokens,
  exchangeCode,
  getValidAccessToken,
  isConnected,
  WHOOP_AUTH_ENDPOINT,
  WHOOP_SCOPES,
  WHOOP_TOKEN_ENDPOINT,
} from '../services/whoop/whoopTokens';
import { config, hasWhoopConfig } from '../utils/config';

// Required for the auth session to close the in-app browser on redirect.
WebBrowser.maybeCompleteAuthSession();

const discovery: AuthSession.DiscoveryDocument = {
  authorizationEndpoint: WHOOP_AUTH_ENDPOINT,
  tokenEndpoint: WHOOP_TOKEN_ENDPOINT,
};

export type WhoopStatus =
  | 'not_configured'
  | 'disconnected'
  | 'connecting'
  | 'loading'
  | 'ready'
  | 'error';

interface WhoopContextValue {
  status: WhoopStatus;
  today: WhoopToday | null;
  error: string | null;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  refresh: () => Promise<void>;
}

const WhoopContext = createContext<WhoopContextValue | undefined>(undefined);

export function WhoopProvider({ children }: { children: React.ReactNode }) {
  const configured = hasWhoopConfig();
  const [status, setStatus] = useState<WhoopStatus>(
    configured ? 'disconnected' : 'not_configured'
  );
  const [today, setToday] = useState<WhoopToday | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [request, response, promptAsync] = AuthSession.useAuthRequest(
    {
      clientId: config.whoopClientId,
      scopes: WHOOP_SCOPES,
      redirectUri: config.whoopRedirectUri,
      responseType: AuthSession.ResponseType.Code,
      usePKCE: true,
    },
    discovery
  );

  // On first mount, if we already have tokens, load data.
  useEffect(() => {
    if (!configured) return;
    (async () => {
      if (await isConnected()) {
        await refresh();
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [configured]);

  // Handle the OAuth redirect result.
  useEffect(() => {
    if (!response) return;
    (async () => {
      if (response.type === 'success' && response.params.code) {
        try {
          setStatus('connecting');
          await exchangeCode(
            response.params.code,
            config.whoopRedirectUri,
            request?.codeVerifier
          );
          await refresh();
        } catch (e) {
          setError(errMsg(e));
          setStatus('error');
        }
      } else if (response.type === 'error') {
        setError(response.error?.message ?? 'Whoop-Anmeldung fehlgeschlagen.');
        setStatus('error');
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [response]);

  async function connect() {
    if (!configured) {
      setError('Whoop ist nicht konfiguriert (WHOOP_CLIENT_ID fehlt in .env).');
      return;
    }
    setError(null);
    await promptAsync();
  }

  async function disconnect() {
    await clearTokens();
    setToday(null);
    setError(null);
    setStatus('disconnected');
  }

  /** Fetch today's Whoop data. Non-fatal: errors set status but never throw. */
  async function refresh() {
    if (!configured) return;
    setStatus('loading');
    setError(null);
    try {
      if (!(await isConnected())) {
        setStatus('disconnected');
        return;
      }
      const data = await fetchWhoopToday(getValidAccessToken);
      if (!data) {
        setStatus('disconnected');
        return;
      }
      setToday(data);
      setStatus('ready');
    } catch (e) {
      // Keep any previously loaded data visible; just surface the error.
      setError(errMsg(e));
      setStatus('error');
    }
  }

  const value = useMemo(
    () => ({ status, today, error, connect, disconnect, refresh }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [status, today, error, request]
  );

  return <WhoopContext.Provider value={value}>{children}</WhoopContext.Provider>;
}

function errMsg(e: unknown): string {
  return e instanceof Error ? e.message : 'Unbekannter Whoop-Fehler.';
}

export function useWhoop(): WhoopContextValue {
  const ctx = useContext(WhoopContext);
  if (!ctx) throw new Error('useWhoop must be used within WhoopProvider');
  return ctx;
}
