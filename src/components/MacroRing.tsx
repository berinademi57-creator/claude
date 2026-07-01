// Progress ring for a single metric (e.g. calories), drawn with react-native-svg.

import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import { colors } from '../theme';

interface Props {
  /** 0..1 (values > 1 are clamped for the arc but shown numerically). */
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  label: string;
  value: string;
  sub?: string;
}

export function MacroRing({
  progress,
  size = 160,
  strokeWidth = 14,
  color = colors.kcal,
  label,
  value,
  sub,
}: Props) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(1, progress));
  const dashoffset = circumference * (1 - clamped);
  const over = progress > 1.0001;

  return (
    <View style={{ width: size, height: size }}>
      <Svg width={size} height={size}>
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={colors.border}
          strokeWidth={strokeWidth}
          fill="none"
        />
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={over ? colors.danger : color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={dashoffset}
          strokeLinecap="round"
          rotation={-90}
          origin={`${size / 2}, ${size / 2}`}
        />
      </Svg>
      <View style={styles.center}>
        <Text style={styles.value}>{value}</Text>
        <Text style={styles.label}>{label}</Text>
        {sub ? <Text style={styles.sub}>{sub}</Text> : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  center: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
  },
  value: { color: colors.text, fontSize: 26, fontWeight: '800' },
  label: { color: colors.textMuted, fontSize: 13, marginTop: 2 },
  sub: { color: colors.textMuted, fontSize: 11, marginTop: 2 },
});
