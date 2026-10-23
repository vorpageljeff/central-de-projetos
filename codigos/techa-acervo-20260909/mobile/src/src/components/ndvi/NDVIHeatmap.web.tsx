import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Image, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { API_URL } from '@/services/api';
import { getItemAsync } from '@/services/secureStorage';
import { Anomaly } from '@/types';

type Props = {
  fieldId: string;
  tilesPath: string | null;
  anomalies: Anomaly[];
  onAnomalyPress: (anomaly: Anomaly) => void;
  height?: number;
};

export function NDVIHeatmap({ fieldId, anomalies, onAnomalyPress, height = 300 }: Props) {
  const [tileUri, setTileUri] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  const loadTile = useCallback(async () => {
    setLoading(true);
    setMessage(null);
    let objectUrl: string | null = null;

    try {
      const token = await getItemAsync('techa_auth_token');
      const headers: Record<string, string> = token
        ? { Authorization: `Bearer ${token}` }
        : {};
      const latestResponse = await fetch(`${API_URL}/fields/${fieldId}/analyses/latest`, { headers });
      if (!latestResponse.ok) throw new Error('Imagem NDVI ainda não disponível.');

      const analysis = await latestResponse.json() as { tile_url?: string | null };
      if (!analysis.tile_url) throw new Error('Imagem NDVI ainda não disponível.');

      const url = analysis.tile_url.startsWith('http')
        ? analysis.tile_url
        : `${API_URL}/fields/${fieldId}/ndvi-tile`;
      const tileResponse = await fetch(url, { headers });
      if (!tileResponse.ok) throw new Error('Não foi possível carregar a imagem NDVI.');

      objectUrl = URL.createObjectURL(await tileResponse.blob());
      setTileUri((previous) => {
        if (previous) URL.revokeObjectURL(previous);
        return objectUrl;
      });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Mapa indisponível na contingência web.');
    } finally {
      setLoading(false);
    }
  }, [fieldId]);

  useEffect(() => {
    loadTile();
  }, [loadTile]);

  useEffect(() => {
    return () => {
      if (tileUri) URL.revokeObjectURL(tileUri);
    };
  }, [tileUri]);

  return (
    <View style={[styles.container, { minHeight: height }]}>
      {loading && <ActivityIndicator size="large" color="#16A34A" />}
      {!loading && tileUri && <Image source={{ uri: tileUri }} resizeMode="contain" style={styles.image} />}
      {!loading && !tileUri && <Text style={styles.message}>{message}</Text>}
      {!loading && !tileUri && <TouchableOpacity style={styles.retry} onPress={loadTile}><Text style={styles.retryText}>Tentar novamente</Text></TouchableOpacity>}
      {anomalies.length > 0 && (
        <View style={styles.anomalies}>
          <Text style={styles.anomalyTitle}>{anomalies.length} anomalia(s) ativa(s)</Text>
          {anomalies.slice(0, 3).map((anomaly) => (
            <TouchableOpacity key={anomaly.id} onPress={() => onAnomalyPress(anomaly)}>
              <Text style={styles.anomalyLink}>Ver anomalia • queda de {anomaly.ndvi_drop_pct.toFixed(0)}%</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { overflow: 'hidden', alignItems: 'center', justifyContent: 'center', padding: 16, backgroundColor: '#0D1F0D' },
  image: { width: '100%', minHeight: 240 },
  message: { color: '#FFF', fontSize: 14, textAlign: 'center' },
  retry: { marginTop: 12, borderRadius: 8, paddingHorizontal: 18, paddingVertical: 9, backgroundColor: '#16A34A' },
  retryText: { color: '#FFF', fontWeight: '700' },
  anomalies: { width: '100%', marginTop: 12, borderRadius: 8, padding: 10, backgroundColor: 'rgba(0,0,0,0.45)' },
  anomalyTitle: { color: '#FFF', fontSize: 12, fontWeight: '700', marginBottom: 4 },
  anomalyLink: { color: '#86EFAC', fontSize: 12, paddingVertical: 4 },
});
