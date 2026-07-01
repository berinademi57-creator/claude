// App root: wires providers and the navigator. Provider order matters only in
// that Whoop/DayLog/Profile are independent — the app renders even if Whoop
// never connects.

import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { DayLogProvider } from './src/context/DayLogContext';
import { ProfileProvider } from './src/context/ProfileContext';
import { WhoopProvider } from './src/context/WhoopContext';
import { RootNavigator } from './src/navigation';

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <ProfileProvider>
        <DayLogProvider>
          <WhoopProvider>
            <RootNavigator />
          </WhoopProvider>
        </DayLogProvider>
      </ProfileProvider>
    </SafeAreaProvider>
  );
}
