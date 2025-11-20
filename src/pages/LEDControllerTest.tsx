import { useState, type MouseEventHandler } from "react";
import { useMqtt } from "../hooks/useMqtt";
import { useSound } from "../hooks/useSound";
import { hexToRgb } from "../lib/utils";
import type { LedCommand } from "../types/types";

export default function LEDControllerTest() {
  const sound = useSound();
  const { connected, publishJson, cmdTopic, acks } = useMqtt();

  const [playerNumber, setPlayerNumber] = useState("22");
  const [displayNumber, setDisplayNumber] = useState("42");
  const [brightness, setBrightness] = useState(120);
  const [selectedColor, setSelectedColor] = useState("#ff0000");

  

  const send = (cmd: LedCommand) => publishJson(cmdTopic, cmd);

  // Preset colors
  const colors = {
    red: "#ff0000",
    green: "#00ff00",
    blue: "#0000ff",
    white: "#ffffff",
    yellow: "#ffff00",
    cyan: "#00ffff",
    magenta: "#ff00ff",
    habsRed: "#af1e2d",
    habsBlue: "#002f6c",
  };

  return (
    <div
      className="
        min-h-screen relative"
    >
      {/* Ice texture overlay */}
      <div
        className="
          pointer-events-none absolute inset-0 opacity-20
          bg-[radial-gradient(1200px_600px_at_50%_-20%,rgba(255,255,255,0.20),transparent_60%),radial-gradient(600px_300px_at_20%_80%,rgba(255,255,255,0.08),transparent_60%),radial-gradient(800px_400px_at_80%_40%,rgba(255,255,255,0.06),transparent_60%)]
        "
      />

      <div className="relative max-w-6xl mx-auto px-4 py-6">
        {/* Header */}
        <div
          className="
            mb-6 rounded-2xl border border-white/10
            bg-white/5 backdrop-blur-xl p-5 shadow-xl
          "
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl md:text-4xl font-extrabold tracking-wide">
                🏒 Habs LED Control
              </h1>
              <p className="text-white/70 text-sm md:text-base">
                Trigger goal lights, numbers & animations over MQTT
              </p>
            </div>

            <div
              className={`px-4 py-2 rounded-full border ${
                connected
                  ? "bg-emerald-400/10 text-emerald-300 border-emerald-300/30"
                  : "bg-rose-400/10 text-rose-300 border-rose-300/30"
              }`}
            >
              <span
                className={`inline-block w-2 h-2 rounded-full mr-2 ${
                  connected ? "bg-emerald-400" : "bg-rose-400"
                } animate-pulse`}
              />
              {connected ? "Connected" : "Disconnected"}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Left: main controls */}
          <div className="lg:col-span-2 space-y-5">
            {/* Goal celebration */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold tracking-wide flex items-center gap-2">
                  🚨 Canadiens Goal
                </h2>
                <div className="hidden md:flex items-center gap-2">
                  <span className="h-2 w-6 rounded bg-[#af1e2d]" />
                  <span className="h-2 w-6 rounded bg-white" />
                  <span className="h-2 w-6 rounded bg-[#002f6c]" />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-white/80 mb-2">
                      Player Number
                    </label>
                    <input
                      type="number"
                      value={playerNumber}
                      onChange={(e) => setPlayerNumber(e.target.value)}
                      min="0"
                      max="99"
                      className="
                        w-full px-4 py-2 rounded-xl bg-white/10 border border-white/10
                        focus:outline-none focus:ring-2 focus:ring-[#af1e2d]/60
                      "
                      placeholder="22"
                    />
                  </div>
                  <div className="flex items-end">
                    <button
                      onClick={() =>
                        send({
                          animation: "habs_goal",
                          player_number: playerNumber,
                          duration: 6,
                        })
                      }
                      className="
                        group relative px-9 py-3 rounded-xl font-extrabold tracking-wider
                        bg-gradient-to-r from-[#af1e2d] to-[#002f6c]
                        shadow-[0_0_30px_rgba(175,30,45,0.25)]
                        hover:shadow-[0_0_40px_rgba(0,47,108,0.35)]
                        transition-all cursor-pointer
                      "
                    >
                      <span className="relative z-10">GOAL HORN</span>
                      <span className="absolute inset-0 rounded-xl ring-2 ring-white/20" />
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  <PresetButton
                    label="#22 Caufield"
                    onClick={() => {
                      setPlayerNumber("22");
                      send({
                        animation: "habs_goal",
                        player_number: "22",
                        duration: 6,
                      });
                    }}
                  />
                  <PresetButton
                    label="#14 Suzuki"
                    onClick={() => {
                      setPlayerNumber("14");
                      send({
                        animation: "habs_goal",
                        player_number: "14",
                        duration: 6,
                      });
                    }}
                  />
                  <PresetButton
                    label="#20 Slaf"
                    onClick={() => {
                      setPlayerNumber("20");
                      send({
                        animation: "habs_goal",
                        player_number: "20",
                        duration: 6,
                      });
                    }}
                  />
                </div>
              </div>
            </div>

            {/* Display number */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl">
              <h2 className="text-xl font-bold mb-4 tracking-wide">
                📟 Display Number
              </h2>
              <div className="flex flex-col sm:flex-row gap-4 items-end">
                <div className="flex-1 w-full">
                  <label className="block text-sm font-medium text-white/80 mb-2">
                    Number (0–99)
                  </label>
                  <input
                    type="number"
                    value={displayNumber}
                    onChange={(e) => setDisplayNumber(e.target.value)}
                    min="0"
                    max="99"
                    className="
                      w-full px-4 py-2 rounded-xl bg-white/10 border border-white/10
                      focus:outline-none focus:ring-2 focus:ring-[#002f6c]/60
                    "
                  />
                </div>
                <button
                  onClick={() =>
                    send({
                      number: displayNumber,
                      color: hexToRgb(selectedColor),
                      bg: [0, 0, 0],
                    } as LedCommand)
                  }
                  className="
                    px-6 py-2 rounded-xl font-semibold
                    bg-[#002f6c] hover:bg-[#06409a]
                    ring-1 ring-white/10 transition
                    cursor-pointer
                  "
                >
                  Show
                </button>
              </div>
            </div>

            {/* Emoji faces */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl">
              <h2 className="text-xl font-bold mb-4 tracking-wide">
                😊 Emoji Faces
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <FaceButton
                  title="😊 Happy"
                  ring="ring-emerald-300/40"
                  bg="bg-emerald-400/10 hover:bg-emerald-400/20"
                  onClick={() =>
                    send({
                      face: "happy",
                      color: hexToRgb(selectedColor),
                      bg: [0, 0, 64],
                    })
                  }
                />
                <FaceButton
                  title="😢 Sad"
                  ring="ring-blue-300/40"
                  bg="bg-blue-400/10 hover:bg-blue-400/20"
                  onClick={() =>
                    send({
                      face: "sad",
                      color: hexToRgb(selectedColor),
                      bg: [0, 0, 64],
                    })
                  }
                />
                <FaceButton
                  title="😰 Stressed"
                  ring="ring-rose-300/40"
                  bg="bg-rose-400/10 hover:bg-rose-400/20"
                  onClick={() =>
                    send({
                      face: "stressed",
                      color: hexToRgb(selectedColor),
                      bg: [0, 0, 64],
                    })
                  }
                />
              </div>
            </div>

            {/* Animations */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl">
              <h2 className="text-xl font-bold mb-4 tracking-wide">
                🎬 Animations
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <AnimButton
                  title="⚡ Flash"
                  classes="bg-rose-500/15 hover:bg-rose-500/25 ring-rose-300/40"
                  onClick={() =>
                    send({
                      animation: "flash",
                      color: hexToRgb(selectedColor),
                      duration: 3,
                      freq: 10,
                    })
                  }
                />
                <AnimButton
                  title="💡 Blink"
                  classes="bg-amber-500/15 hover:bg-amber-500/25 ring-amber-300/40"
                  onClick={() =>
                    send({
                      animation: "blink",
                      color: hexToRgb(selectedColor),
                      times: 6,
                      period: 0.15,
                    })
                  }
                />
                <AnimButton
                  title="🌈 Rainbow"
                  classes="bg-gradient-to-r from-rose-500/20 via-emerald-500/20 to-blue-500/20 hover:from-rose-500/30 hover:via-emerald-500/30 hover:to-blue-500/30 ring-purple-300/40"
                  onClick={() =>
                    send({ animation: "rainbow", duration: 5, speed: 0.03 })
                  }
                />
                <AnimButton
                  title="✨ Sparkle"
                  classes="bg-white/10 hover:bg-white/20 ring-white/40"
                  onClick={() =>
                    send({
                      animation: "sparkle",
                      color: hexToRgb(selectedColor),
                      count: 10,
                      duration: 3,
                    })
                  }
                />
              </div>
            </div>

            {/* LED strip */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl">
              <h2 className="text-xl font-bold mb-4 tracking-wide">
                💡 LED Strip
              </h2>
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() =>
                    send({ strip: "fill", color: hexToRgb(selectedColor) })
                  }
                  className="
                    flex-1 px-6 py-3 rounded-xl font-semibold
                    bg-fuchsia-500/15 hover:bg-fuchsia-500/25
                    ring-1 ring-fuchsia-300/40 transition
                    cursor-pointer
                  "
                >
                  Fill Color
                </button>
                <button
                  onClick={() => send({ strip: "clear" })}
                  className="
                    px-6 py-3 rounded-xl font-semibold
                    bg-white/10 hover:bg-white/20
                    ring-1 ring-white/20 transition
                    cursor-pointer
                  "
                >
                  Clear Strip
                </button>
              </div>
            </div>

            {/* System */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl">
              <h2 className="text-xl font-bold mb-4 tracking-wide">
                ⚙️ System
              </h2>
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-white/80 mb-2">
                    Brightness: {brightness}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="255"
                    value={brightness}
                    onChange={(e) => setBrightness(Number(e.target.value))}
                    className="w-full accent-[#af1e2d]"
                  />
                  <button
                    onClick={() => send({ brightness })}
                    className="
                      mt-2 px-4 py-2 rounded-xl font-semibold
                      bg-white/10 hover:bg-white/20
                      ring-1 ring-white/20 transition
                      cursor-pointer
                    "
                  >
                    Apply Brightness
                  </button>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={() => send({ clear: true })}
                    className="
                      flex-1 px-6 py-3 rounded-xl font-semibold
                      bg-rose-500/15 hover:bg-rose-500/25
                      ring-1 ring-rose-300/40 transition
                      cursor-pointer
                    "
                  >
                    Clear Display
                  </button>
                  <button
                    onClick={() => send({ stop: true })}
                    className="
                      flex-1 px-6 py-3 rounded-xl font-semibold
                      bg-amber-500/15 hover:bg-amber-500/25
                      ring-1 ring-amber-300/40 transition
                      cursor-pointer
                    "
                  >
                    Stop Animation
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right: color + log */}
          <div className="space-y-5">
            {/* Color picker */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl">
              <h2 className="text-xl font-bold mb-4 tracking-wide">
                🎨 Color Picker
              </h2>
              <input
                type="color"
                value={selectedColor}
                onChange={(e) => setSelectedColor(e.target.value)}
                className="w-full h-24 rounded-xl cursor-pointer bg-white/10 border border-white/10"
              />
              <div className="mt-4 space-y-1">
                <p className="text-sm text-white/80">
                  Selected: {selectedColor}
                </p>
                <p className="text-xs text-white/60">
                  RGB: {hexToRgb(selectedColor).join(", ")}
                </p>
              </div>
              <div className="mt-4 grid grid-cols-6 gap-2">
                {Object.entries(colors).map(([name, hex]) => (
                  <button
                    key={name}
                    onClick={() => setSelectedColor(hex)}
                    className="h-9 rounded-lg border border-white/20 hover:ring-2 hover:ring-white/30 transition"
                    style={{ backgroundColor: hex }}
                    title={name}
                  />
                ))}
              </div>
            </div>

            <div className="flex flex-wrap rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl gap-2">
              <button
                className="px-3 py-2 rounded bg-blue-600 text-white cursor-pointer"
                onClick={() =>
                  sound.play("horn", { restart: true, volume: 0.9 })
                }
              >
                Play Horn
              </button>
              <button
                className="px-3 py-2 rounded bg-gray-200 text-black cursor-pointer"
                onClick={() => sound.play("buuu", { restart: true })}
              >
                Play Whistle
              </button>
              <button
                className="px-3 py-2 rounded bg-rose-600 text-white cursor-pointer"
                onClick={() => sound.stopAll()}
              >
                Stop All
              </button>
            </div>

            {/* Activity log */}
            <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 shadow-xl">
              <h2 className="text-xl font-bold mb-4 tracking-wide">
                📜 Activity Log
              </h2>
              <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                {acks.length === 0 ? (
                  <p className="text-white/60 text-sm">No activity yet…</p>
                ) : (
                  acks.map((ack, i) => (
                    <div
                      key={i}
                      className={`p-3 rounded-xl text-sm ring-1 ${
                        ack.ok
                          ? "bg-emerald-400/10 ring-emerald-300/30"
                          : "bg-rose-400/10 ring-rose-300/30"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span
                          className={`font-semibold ${
                            ack.ok ? "text-emerald-300" : "text-rose-300"
                          }`}
                        >
                          {ack.ok ? "✓" : "✗"} {ack.action || "command"}
                        </span>
                        <span className="text-white/50 text-xs">
                          {ack.ts
                            ? new Date(ack.ts * 1000).toLocaleTimeString()
                            : ""}
                        </span>
                      </div>
                      {ack.error && (
                        <p className="text-rose-300 text-xs">{ack.error}</p>
                      )}
                      {ack.type && (
                        <p className="text-white/70 text-xs">
                          Type: {ack.type}
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* --- small UI helpers --- */
function PresetButton({ label, onClick }: {label: string, onClick: MouseEventHandler})  {
  return (
    <button
      onClick={onClick}
      className="
        px-4 py-2 rounded-xl font-semibold
        bg-white/10 hover:bg-white/20
        ring-1 ring-white/20 transition
        cursor-pointer
      "
    >
      {label}
    </button>
  );
}

function FaceButton({ title, onClick, bg, ring } : {title: string, onClick: MouseEventHandler, bg: string,  ring: string}) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 rounded-xl font-semibold ${bg} ring-1 ${ring} transition cursor-pointer`}
    >
      {title}
    </button>
  );
}

function AnimButton({ title, onClick, classes } : {title: string, onClick: MouseEventHandler, classes: string}) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 rounded-xl font-semibold ring-1 transition ${classes} cursor-pointer`}
    >
      {title}
    </button>
  );
}
