import React, { forwardRef } from 'react';
import { StyleSheet, Text, View } from 'react-native';

export type Region = {
  latitude: number;
  longitude: number;
  latitudeDelta: number;
  longitudeDelta: number;
};

export const PROVIDER_GOOGLE = 'google';

export const Marker = (_props: Record<string, unknown>) => null;
export const Polygon = (_props: Record<string, unknown>) => null;
export const Overlay = (_props: Record<string, unknown>) => null;

const MapView = forwardRef<View, any>(function WebMapView(
  { style },
  ref
) {
  return (
    <View ref={ref} style={[style, styles.container]}>
      <Text style={styles.icon}>📍</Text>
      <Text style={styles.title}>Mapa disponível no aplicativo</Text>
      <Text style={styles.text}>
        Na contingência web, consulte os dados do talhão e abra a localização no aplicativo de mapas do celular.
      </Text>
    </View>
  );
});

const styles = StyleSheet.create({
  container: {
    minHeight: 220,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    backgroundColor: '#E8F5E9',
  },
  icon: { fontSize: 34, marginBottom: 8 },
  title: { color: '#1A4731', fontSize: 16, fontWeight: '800', textAlign: 'center' },
  text: { color: '#2F4F3F', fontSize: 13, lineHeight: 18, marginTop: 6, maxWidth: 320, textAlign: 'center' },
});

export default MapView;
