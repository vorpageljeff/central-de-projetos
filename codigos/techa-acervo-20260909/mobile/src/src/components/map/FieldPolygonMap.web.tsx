import React, { RefObject, useState } from 'react';
import { LayoutChangeEvent, Pressable, StyleSheet, Text, View } from 'react-native';

type Region = {
  latitude: number;
  longitude: number;
  latitudeDelta: number;
  longitudeDelta: number;
};

type Coordinate = { latitude: number; longitude: number };

type Props = {
  mapRef: RefObject<any>;
  region: Region;
  coordinates: Coordinate[];
  onAddCoordinate: (coordinate: Coordinate) => void;
  onMoveCoordinate?: (index: number, coordinate: Coordinate) => void;
  onInsertCoordinate?: (index: number, coordinate: Coordinate) => void;
  pointLabel: string;
  midpointLabel?: string;
};

export function FieldPolygonMap({ region, coordinates, onAddCoordinate, pointLabel }: Props) {
  const [size, setSize] = useState({ width: 1, height: 1 });

  const onLayout = (event: LayoutChangeEvent) => {
    const { width, height } = event.nativeEvent.layout;
    setSize({ width: Math.max(width, 1), height: Math.max(height, 1) });
  };

  return (
    <Pressable
      style={styles.container}
      onLayout={onLayout}
      onPress={(event) => {
        const { locationX, locationY } = event.nativeEvent;
        onAddCoordinate({
          latitude: region.latitude - (locationY / size.height - 0.5) * region.latitudeDelta,
          longitude: region.longitude + (locationX / size.width - 0.5) * region.longitudeDelta,
        });
      }}
    >
      <Text style={styles.title}>Marcação simplificada na web</Text>
      <Text style={styles.text}>Toque na área para adicionar os vértices. O mapa de satélite continua disponível no app.</Text>
      {coordinates.map((coordinate, index) => {
        const left = ((coordinate.longitude - region.longitude) / region.longitudeDelta + 0.5) * size.width;
        const top = ((region.latitude - coordinate.latitude) / region.latitudeDelta + 0.5) * size.height;
        return (
          <View key={`${coordinate.latitude}-${coordinate.longitude}-${index}`} style={[styles.point, { left, top }]}> 
            <Text style={styles.pointText}>{pointLabel} {index + 1}</Text>
          </View>
        );
      })}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, minHeight: 300, overflow: 'hidden', alignItems: 'center', justifyContent: 'center', padding: 24, backgroundColor: '#E8F5E9' },
  title: { color: '#1A4731', fontSize: 16, fontWeight: '800', textAlign: 'center' },
  text: { color: '#2F4F3F', fontSize: 13, lineHeight: 18, marginTop: 6, maxWidth: 300, textAlign: 'center' },
  point: { position: 'absolute', transform: [{ translateX: -12 }, { translateY: -12 }], minWidth: 24, height: 24, borderRadius: 12, paddingHorizontal: 6, backgroundColor: '#16A34A', alignItems: 'center', justifyContent: 'center', borderWidth: 2, borderColor: '#FFF' },
  pointText: { color: '#FFF', fontSize: 10, fontWeight: '800' },
});
