// Navigation: bottom tabs (Heute · Hinzufügen · Profil). The "Hinzufügen" tab
// is itself a stack (hub → Foto/Barcode/Manuell).

import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import React from 'react';
import { Text } from 'react-native';
import { AddHubScreen } from '../screens/AddHubScreen';
import { BarcodeScreen } from '../screens/BarcodeScreen';
import { ManualScreen } from '../screens/ManualScreen';
import { PhotoScreen } from '../screens/PhotoScreen';
import { ProfileScreen } from '../screens/ProfileScreen';
import { TodayScreen } from '../screens/TodayScreen';
import { colors } from '../theme';

const Tab = createBottomTabNavigator();
const AddStack = createNativeStackNavigator();

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: colors.bg,
    card: colors.card,
    text: colors.text,
    border: colors.border,
    primary: colors.primary,
  },
};

const screenHeader = {
  headerStyle: { backgroundColor: colors.card },
  headerTintColor: colors.text,
  contentStyle: { backgroundColor: colors.bg },
};

function AddStackNavigator() {
  return (
    <AddStack.Navigator screenOptions={screenHeader}>
      <AddStack.Screen
        name="AddHub"
        component={AddHubScreen}
        options={{ title: 'Hinzufügen' }}
      />
      <AddStack.Screen name="Foto" component={PhotoScreen} options={{ title: 'Foto (geschätzt)' }} />
      <AddStack.Screen name="Barcode" component={BarcodeScreen} options={{ title: 'Barcode (exakt)' }} />
      <AddStack.Screen name="Manuell" component={ManualScreen} options={{ title: 'Manuell (exakt)' }} />
    </AddStack.Navigator>
  );
}

function tabIcon(icon: string) {
  return ({ color }: { color: string }) => (
    <Text style={{ fontSize: 20, color }}>{icon}</Text>
  );
}

export function RootNavigator() {
  return (
    <NavigationContainer theme={navTheme}>
      <Tab.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: colors.card },
          headerTintColor: colors.text,
          tabBarStyle: { backgroundColor: colors.card, borderTopColor: colors.border },
          tabBarActiveTintColor: colors.primary,
          tabBarInactiveTintColor: colors.textMuted,
        }}
      >
        <Tab.Screen
          name="Heute"
          component={TodayScreen}
          options={{ tabBarIcon: tabIcon('◎') }}
        />
        <Tab.Screen
          name="Hinzufügen"
          component={AddStackNavigator}
          options={{ headerShown: false, tabBarIcon: tabIcon('＋') }}
        />
        <Tab.Screen
          name="Profil"
          component={ProfileScreen}
          options={{ tabBarIcon: tabIcon('☰') }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
