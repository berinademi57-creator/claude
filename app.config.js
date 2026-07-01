// Expo app config. Reads secrets from process.env (loaded from .env via dotenv)
// and exposes only the NON-secret, client-needed values through `extra`.
//
// SECURITY NOTE: Anything placed in `extra` ships inside the app bundle and is
// readable by anyone who unpacks the app. The Whoop CLIENT SECRET and any real
// server-side secret must NEVER go here. For production, move the Claude Vision
// call and the Whoop token exchange behind your own backend proxy. See README.
require('dotenv').config();

module.exports = {
  expo: {
    name: 'Calorie + Whoop',
    slug: 'calorie-tracker-whoop',
    version: '1.0.0',
    orientation: 'portrait',
    userInterfaceStyle: 'automatic',
    scheme: 'caltracker',
    splash: {
      backgroundColor: '#0B0F14',
      resizeMode: 'contain',
    },
    ios: {
      supportsTablet: true,
      bundleIdentifier: 'com.example.caltrackerwhoop',
      infoPlist: {
        NSCameraUsageDescription:
          'Die Kamera wird zum Scannen von Barcodes und Fotografieren von Mahlzeiten verwendet.',
      },
    },
    android: {
      package: 'com.example.caltrackerwhoop',
      permissions: ['CAMERA'],
    },
    plugins: [
      [
        'expo-camera',
        {
          cameraPermission:
            'Erlaube den Kamerazugriff zum Scannen von Barcodes und Fotografieren von Mahlzeiten.',
        },
      ],
      'expo-secure-store',
    ],
    extra: {
      // Non-secret, client-safe config.
      whoopClientId: process.env.WHOOP_CLIENT_ID ?? '',
      whoopRedirectUri:
        process.env.WHOOP_REDIRECT_URI ?? 'http://localhost:8080/callback',
      // RECOMMENDED: point this at your own backend that performs the OAuth
      // token exchange (and holds the client secret server-side). When set,
      // the client never sees the secret.
      whoopTokenProxyUrl: process.env.WHOOP_TOKEN_PROXY_URL ?? '',
      // LOCAL DEV ONLY fallback: if no proxy is configured, the app will do the
      // confidential token exchange itself using this secret. This ships the
      // secret in the bundle — acceptable only for personal/local testing.
      // Leave blank in any shared/production build. See README "Security".
      whoopClientSecret: process.env.WHOOP_CLIENT_SECRET ?? '',
      // Present for V1 convenience only — see SECURITY NOTE above. Prefer a proxy.
      anthropicApiKey: process.env.ANTHROPIC_API_KEY ?? '',
      anthropicModel: process.env.ANTHROPIC_MODEL ?? 'claude-opus-4-8',
    },
  },
};
