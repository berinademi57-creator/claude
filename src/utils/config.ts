// Central access to non-secret runtime config injected via app.config.js `extra`.
// Reading through one module makes it obvious what the client knows about.

import Constants from 'expo-constants';

interface AppExtra {
  whoopClientId: string;
  whoopRedirectUri: string;
  whoopTokenProxyUrl: string;
  whoopClientSecret: string;
  anthropicApiKey: string;
  anthropicModel: string;
}

const extra = (Constants.expoConfig?.extra ?? {}) as Partial<AppExtra>;

export const config = {
  whoopClientId: extra.whoopClientId ?? '',
  whoopRedirectUri: extra.whoopRedirectUri ?? 'http://localhost:8080/callback',
  whoopTokenProxyUrl: extra.whoopTokenProxyUrl ?? '',
  whoopClientSecret: extra.whoopClientSecret ?? '',
  anthropicApiKey: extra.anthropicApiKey ?? '',
  anthropicModel: extra.anthropicModel ?? 'claude-opus-4-8',
};

export const hasWhoopConfig = () => config.whoopClientId.length > 0;
export const hasVisionConfig = () => config.anthropicApiKey.length > 0;
