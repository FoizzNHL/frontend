// src/components/ConnectionStatusBadge.tsx
import React from "react";

type Props = {
  connected: boolean;
};

export const ConnectionStatusBadge: React.FC<Props> = ({ connected }) => {
  const bg = connected
    ? "bg-emerald-400/10 text-emerald-500 border-emerald-300/60"
    : "bg-rose-400/10 text-rose-700 border-rose-300/60";

  const dot = connected ? "bg-emerald-400" : "bg-rose-400";

  return (
    <div
      className={`inline-flex items-center px-4 py-2 rounded-full border text-xs font-medium ${bg}`}
    >
      <span className={`inline-block w-2 h-2 rounded-full mr-2 ${dot} animate-pulse`} />
      {connected ? "MQTT Connected" : "MQTT Disconnected"}
    </div>
  );
};
