// src/GoalProjection.tsx
import React, { useEffect, useRef } from "react";
import chLogo from "../assets/ch-logo.png"; // put your logo here

const GoalProjection: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const logo = new Image();
    logo.src = chLogo;

    let animationFrameId: number;
    let animating = false;
    let startTime = 0;
    const DURATION = 6000; // 6s

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    const drawFrame = (timestamp: number) => {
      animationFrameId = requestAnimationFrame(drawFrame);

      const { width, height } = canvas;
      // faint trail to make it feel more alive
      ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
      ctx.fillRect(0, 0, width, height);

      if (!animating || !logo.complete) return;

      const elapsed = timestamp - startTime;
      if (elapsed > DURATION) {
        animating = false;
        ctx.fillStyle = "black";
        ctx.fillRect(0, 0, width, height);
        return;
      }

      const t = elapsed / 1000;
      const centerX = width / 2;
      const centerY = height / 2;

      // Background gradient in Habs colors
      const flash = (Math.sin(t * 6) + 1) / 2; // 0..1
      const grad = ctx.createRadialGradient(
        centerX,
        centerY,
        0,
        centerX,
        centerY,
        Math.max(width, height)
      );
      grad.addColorStop(0, `rgba(255, 255, 255, ${0.3 + 0.3 * flash})`);
      grad.addColorStop(0.4, `rgba(0, 38, 84, 0.9)`); // dark blue
      grad.addColorStop(1, `rgba(255, 0, 0, 0.9)`); // red
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // Spinning + pulsing logo
      const baseSize = Math.min(width, height) * 0.35;
      const pulse = 0.15 * Math.sin(t * 4);
      const size = baseSize * (1 + pulse);
      const angle = t * 2 * Math.PI; // one full rotation per second

      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(angle);
      ctx.drawImage(logo, -size / 2, -size / 2, size, size);
      ctx.restore();

      // GOAL! text
      const fontSize = Math.min(width, height) * 0.12;
      ctx.font = `bold ${fontSize}px system-ui, -apple-system, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.lineWidth = fontSize * 0.06;

      const text = "GOAL!";
      const textY = centerY + size * 0.6;

      ctx.strokeStyle = "black";
      ctx.strokeText(text, centerX, textY);
      ctx.fillStyle = "white";
      ctx.fillText(text, centerX, textY);
    };

    const triggerGoal = () => {
      startTime = performance.now();
      animating = true;
    };

    const onMessage = (event: MessageEvent) => {
      const data = event.data || {};
      if (data.type === "GOAL" && data.team === "MTL") {
        triggerGoal();
      }
    };

    window.addEventListener("message", onMessage);
    animationFrameId = requestAnimationFrame(drawFrame);

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("message", onMessage);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        width: "100vw",
        height: "100vh",
        display: "block",
        margin: 0,
        padding: 0,
        background: "black",
      }}
    />
  );
};

export default GoalProjection;
