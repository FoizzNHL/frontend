import { useContext } from "react";
import { SoundCtx } from "../providers/SoundProvider";

export function useSound() {
  const ctx = useContext(SoundCtx);
  if (!ctx) throw new Error("useSound must be used inside <SoundProvider>");
  return ctx;
}