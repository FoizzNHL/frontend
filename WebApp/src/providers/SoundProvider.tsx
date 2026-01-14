// sound/SoundProvider.tsx
import React, { createContext, useMemo } from "react";

type PlayOpts = {
  volume?: number;   // 0..1
  loop?: boolean;
  restart?: boolean; // force start from 0 each play
};

export interface SoundPlayer {
  preload(map: Record<string, string>): void;
  play(key: string, opts?: PlayOpts): Promise<void>;
  stop(key: string): void;
  stopAll(): void;
  setVolume(key: string, volume: number): void; // 0..1
}

class BrowserSoundPlayer implements SoundPlayer {
  private audios = new Map<string, HTMLAudioElement>();

  preload(map: Record<string, string>) {
    Object.entries(map).forEach(([key, src]) => {
      if (!this.audios.has(key)) {
        const a = new Audio(src);
        a.preload = "auto";
        this.audios.set(key, a);
      }
    });
  }

  async play(key: string, opts?: PlayOpts) {
    const a = this.audios.get(key);
    if (!a) throw new Error(`Sound "${key}" not found. Did you preload it?`);
    if (opts?.volume != null) a.volume = Math.max(0, Math.min(1, opts.volume));
    a.loop = !!opts?.loop;
    if (opts?.restart) a.currentTime = 0;
    try {
      await a.play();
    } catch (e) {
      // Autoplay/gesture restrictions may throw—surface a helpful message.
      console.warn(`Failed to play "${key}". Possibly blocked by the browser:`, e);
      throw e;
    }
  }

  stop(key: string) {
    const a = this.audios.get(key);
    if (!a) return;
    a.pause();
    a.currentTime = 0;
    a.loop = false;
  }

  stopAll() {
    for (const a of this.audios.values()) {
      a.pause();
      a.currentTime = 0;
      a.loop = false;
    }
  }

  setVolume(key: string, volume: number) {
    const a = this.audios.get(key);
    if (!a) return;
    a.volume = Math.max(0, Math.min(1, volume));
  }
}

export const SoundCtx = createContext<SoundPlayer | null>(null);

export function SoundProvider({
  children,
  sounds,
  player,
}: {
  children: React.ReactNode;
  sounds: Record<string, string>; // { horn: "/sounds/horn.mp3", whistle: "/sounds/whistle.mp3" }
  /** for tests, you can inject a mock player */
  player?: SoundPlayer;
}) {
  const impl = useMemo(() => player ?? new BrowserSoundPlayer(), [player]);
  useMemo(() => impl.preload(sounds), [impl, sounds]);
  return <SoundCtx.Provider value={impl}>{children}</SoundCtx.Provider>;
}


