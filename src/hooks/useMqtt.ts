import { useEffect, useRef, useState } from 'react';
import mqtt from 'mqtt';
import type { IClientOptions, MqttClient } from 'mqtt';

export type Acknowledgement = { ok: boolean; action?: string; error?: string; ts?: number; ackId?: string; [k: string]: any };

export function useMqtt(opts?: { host?: string; port?: number; cmdTopic?: string; ackTopic?: string; }) {
  const lightHost = import.meta.env.VITE_LIGHT_HOST;
  const lightPort = import.meta.env.VITE_LIGHT_PORT;
  const { host=lightHost, port=lightPort, cmdTopic='lighting/cmd', ackTopic='lighting/ack' } = opts || {};
  const [connected, setConnected] = useState(false);
  const [client, setClient] = useState<MqttClient | null>(null);
  const [acks, setAcks] = useState<Acknowledgement[]>([]);
  const clientRef = useRef<MqttClient | null>(null);

  useEffect(() => {
    // const url = `ws://${host}:${port}`;
    const url = `wss://lights.mitradev.com/mqtt`;
    const options: IClientOptions = { reconnectPeriod: 2000, clean: true };
    const c = mqtt.connect(url, options);
    clientRef.current = c;

    c.on('connect', () => {
      setConnected(true);
      c.subscribe(ackTopic, (err) => { if (err) console.error('Subscribe error:', err); });
    });
    c.on('message', (topic, payload) => {
      if (topic === ackTopic) {
        try { setAcks((prev) => [JSON.parse(payload.toString()), ...prev].slice(0, 50)); }
        catch (e) { console.warn('Bad ACK JSON:', e); }
      }
    });
    c.on('error', (err) => console.error('MQTT error:', err));
    c.on('close', () => setConnected(false));
    setClient(c);
    return () => c.end(true);
  }, [host, port, ackTopic]);

  const publish = (topic: string, payload: string) => clientRef.current?.publish(topic, payload);
  const publishJson = (topic: string, obj: any) => publish(topic, JSON.stringify(obj));
  return { connected, client, publish, publishJson, cmdTopic, ackTopic, acks };
}
