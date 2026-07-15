/*
 * ParticleSphere.tsx
 *
 * Standalone React + Three.js reference component for the OpsKnowledge main chat screen.
 * Provide to OpenDesign as an attached asset alongside opendesign-prompt.md.
 *
 * Expected dependencies (NOT bundled here; consumer installs):
 *   - react (>=18)
 *   - three (>=0.160)
 *
 * Default preview props (for OpenDesign / Storybook preview):
 *   <ParticleSphere particleScale={2} speed={5} cursorRadiusUI={50} />
 *
 * Brand color defaults:
 *   - light theme: "#24445C" (ink-blue)
 *   - dark theme: "#7FA6BE" (ink-blue-bright)
 *
 * Adapted from the user-provided Originkit Particle Sphere reference.
 * The component is a decorative visual signature only: aria-hidden, non-interactive for AT,
 * pointer interaction is decorative and touch-safe (never blocks scrolling).
 */

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

export interface ParticleSphereProps {
  /**
   * Brand particle color. Defaults to ink-blue.
   * For dark theme, pass "#7FA6BE" (ink-blue-bright) or use theme="dark".
   */
  color?: string;

  /** Visual theme shortcut that picks the brand default color if `color` is omitted. */
  theme?: "light" | "dark";

  /**
   * Base point count on the Fibonacci sphere. Lowered automatically on mobile/low-power.
   * Default: 1500. Mobile default: 800.
   */
  count?: number;

  /** Overall particle scale multiplier. Preview default: 2. */
  particleScale?: number;

  /** Rotation / drift speed 0..10. Preview default: 5. */
  speed?: number;

  /** Pointer repulsion radius in screen pixels. Preview default: 50. */
  cursorRadiusUI?: number;

  /** Repulsion strength. Subtle by default. */
  repulsion?: number;

  /** Click/tap scatter strength. Subtle by default. */
  scatter?: number;

  /** Force reduced-motion behavior (useful for tests). If omitted, reads the media query. */
  reducedMotion?: boolean;

  /** Force the lower-power fallback (useful for tests). If omitted, detected at runtime. */
  forceLowerPower?: boolean;
}

const BRAND_LIGHT = "#24445C";
const BRAND_DARK = "#7FA6BE";

// Practical upper bound for particle count. Prevents excessive allocation
// (Float32Array of count*3 floats) and per-frame iteration cost while
// preserving visual density well beyond the defaults (1500 / 800 low-power).
// 20,000 points produce a dense, smooth sphere without GPU pressure on
// mainstream hardware; higher values offer diminishing visual returns.
const MAX_PARTICLES = 20000;

function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function isLowerPowerDevice(): boolean {
  if (typeof navigator === "undefined") return false;
  const ua = navigator.userAgent || "";
  const isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(ua);
  // Coarse pointer is a good proxy for touch/low-power.
  const coarse =
    typeof window !== "undefined" && window.matchMedia
      ? window.matchMedia("(pointer: coarse)").matches
      : false;
  const lowMem =
    // @ts-expect-error deviceMemory is non-standard but informative
    typeof navigator !== "undefined" && (navigator as any).deviceMemory
      ? // @ts-expect-error deviceMemory is non-standard but informative
        (navigator as any).deviceMemory <= 4
      : false;
  return isMobile || coarse || lowMem;
}

function isWebGLAvailable(): boolean {
  if (typeof window === "undefined") return false;
  try {
    const canvas = document.createElement("canvas");
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
    );
  } catch {
    return false;
  }
}

/**
 * Build a Fibonacci-distributed point cloud on a unit sphere.
 * Returns Float32Array of length count*3.
 * `count` is sanitized: non-finite or non-positive values clamp to 1,
 * values above MAX_PARTICLES clamp to MAX_PARTICLES.
 * count=1 places a single point at the sphere's north pole (0, 1, 0).
 */
function fibonacciSphere(count: number): Float32Array {
  const n = Number.isFinite(count) && count > 0 ? Math.floor(count) : 1;
  const clamped = Math.min(n, MAX_PARTICLES);
  const positions = new Float32Array(clamped * 3);
  if (clamped === 1) {
    // Single point: place at the north pole to avoid division by zero.
    positions[0] = 0;
    positions[1] = 1;
    positions[2] = 0;
    return positions;
  }
  const goldenAngle = Math.PI * (3 - Math.sqrt(5)); // ~2.39996
  for (let i = 0; i < clamped; i++) {
    const y = 1 - (i / (clamped - 1)) * 2; // 1..-1
    const radius = Math.sqrt(1 - y * y);
    const theta = goldenAngle * i;
    const x = Math.cos(theta) * radius;
    const z = Math.sin(theta) * radius;
    positions[i * 3] = x;
    positions[i * 3 + 1] = y;
    positions[i * 3 + 2] = z;
  }
  return positions;
}

export function ParticleSphere({
  color,
  theme = "light",
  count,
  particleScale = 2,
  speed = 5,
  cursorRadiusUI = 50,
  repulsion = 0.18,
  scatter = 0.25,
  reducedMotion,
  forceLowerPower,
}: ParticleSphereProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [useFallback, setUseFallback] = useState(false);
  // Distinct readiness signal for zero-size recovery. When the parent starts at
  // 0x0, a ResizeObserver waits for usable dimensions, then increments this
  // counter to re-trigger the effect. This is separate from `useFallback` so
  // that `useFallback` can stay OUT of the effect deps (avoiding renderer
  // recreation after webglcontextlost) while `readySignal` drives deterministic
  // retry on dimension availability.
  const [readySignal, setReadySignal] = useState(0);
  // Guards against state updates after unmount.
  const mountedRef = useRef(true);
  // Live reduced-motion state so the component updates when the media query changes
  // without requiring an unrelated prop render.
  const [reducedMotionState, setReducedMotionState] = useState<boolean>(() =>
    reducedMotion ?? prefersReducedMotion()
  );

  const resolvedColor = color ?? (theme === "dark" ? BRAND_DARK : BRAND_LIGHT);
  // `reducedMotion` prop wins if explicitly provided; otherwise follow live media query.
  const shouldReduce = reducedMotion ?? reducedMotionState;
  const lowerPower = forceLowerPower ?? (typeof window !== "undefined" ? isLowerPowerDevice() : false);
  // Sanitize count: non-finite, negative, or zero values clamp to 1;
  // values above MAX_PARTICLES clamp to MAX_PARTICLES to bound allocation
  // and per-frame iteration cost. The loop in the effect iterates
  // `resolvedCount` times, so it must be a finite positive integer within
  // the safe cap. fibonacciSphere() also sanitizes defensively.
  const rawCount = count ?? (lowerPower ? 800 : 1500);
  const sanitizedCount = Number.isFinite(rawCount) && rawCount > 0 ? Math.floor(rawCount) : 1;
  const resolvedCount = Math.min(sanitizedCount, MAX_PARTICLES);

  // Track mount status so observers/handlers never call setState after unmount.
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Subscribe to prefers-reduced-motion changes so motion behavior updates live.
  useEffect(() => {
    if (reducedMotion !== undefined) return; // prop override: do not subscribe
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handler = (e: MediaQueryListEvent) => setReducedMotionState(e.matches);
    // addEventListener is standard; older Safari used addListener.
    if (mq.addEventListener) {
      mq.addEventListener("change", handler);
      return () => mq.removeEventListener("change", handler);
    }
    // @ts-expect-error legacy addListener for old Safari
    mq.addListener(handler);
    return () => {
      // @ts-expect-error legacy removeListener for old Safari
      mq.removeListener(handler);
    };
  }, [reducedMotion]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // When lowerPower is true, never initialize Three.js, WebGLRenderer,
    // listeners, ResizeObserver for WebGL, or animation frames. The render
    // return already shows the static fallback. A prop change from lowerPower
    // true to false re-runs this effect (lowerPower is in the deps) and
    // initializes normally; false to true runs the effect cleanup (disposing
    // everything) then this early return.
    if (lowerPower) return;

    // If WebGL is unavailable, render the lower-power fallback.
    if (!isWebGLAvailable()) {
      if (mountedRef.current) setUseFallback(true);
      return;
    }

    let width = container.clientWidth;
    let height = container.clientHeight;
    if (width === 0 || height === 0) {
      // Parent hasn't laid out yet. Show the static fallback immediately so the
      // sphere is never blank, and observe until the parent reports usable
      // dimensions. On the first usable report, increment `readySignal` (which
      // IS in the effect deps) to deterministically re-trigger the effect,
      // which will find usable dimensions and initialize the renderer.
      // `useFallback` stays out of the effect deps so this retry mechanism
      // cannot accidentally recreate a renderer after webglcontextlost.
      const ro = new ResizeObserver((entries) => {
        if (!mountedRef.current) {
          ro.disconnect();
          return;
        }
        for (const entry of entries) {
          const w = entry.contentRect.width;
          const h = entry.contentRect.height;
          if (w > 0 && h > 0) {
            ro.disconnect();
            // Increment the readiness signal to re-run the effect. Also clear
            // useFallback so the WebGL path (not the fallback) runs on retry.
            setUseFallback(false);
            setReadySignal((s) => s + 1);
            return;
          }
        }
      });
      ro.observe(container);
      // While waiting, show the static fallback so the sphere is never blank.
      setUseFallback(true);
      return () => ro.disconnect();
    }

    // --- Scene setup (guarded) ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.z = 3.2;

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: !lowerPower,
        alpha: true,
        powerPreference: "high-performance",
      });
    } catch (err) {
      // Constructor failure (e.g. GPU blacklist, context limit): deterministic fallback.
      if (mountedRef.current) setUseFallback(true);
      return;
    }

    // Forward-declare resources so the context-lost handler and cleanup can
    // reference them safely regardless of when they fire.
    let frameId = 0;
    let resizeObserver: ResizeObserver | null = null;
    let disposed = false;

    // --- Geometry: Points on a Fibonacci sphere ---
    const basePositions = fibonacciSphere(resolvedCount);
    const geometry = new THREE.BufferGeometry();
    const currentPositions = basePositions.slice();
    geometry.setAttribute("position", new THREE.BufferAttribute(currentPositions, 3));

    const material = new THREE.PointsMaterial({
      color: new THREE.Color(resolvedColor),
      size: particleScale * 0.018,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.92,
      depthWrite: false,
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    // --- Pointer state (decorative, touch-safe) ---
    const pointer = new THREE.Vector2(9999, 9999);
    let scatterPulse = 0;

    const updatePointerFromEvent = (clientX: number, clientY: number) => {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.set(clientX - rect.left, clientY - rect.top);
    };

    const onPointerMove = (e: PointerEvent) => {
      updatePointerFromEvent(e.clientX, e.clientY);
    };
    const onPointerDown = (e: PointerEvent) => {
      if (e.button !== undefined && e.button !== 0) return;
      scatterPulse = 1;
      updatePointerFromEvent(e.clientX, e.clientY);
    };
    const onPointerLeave = () => {
      pointer.set(9999, 9999);
    };

    // --- Visibility: pause when hidden ---
    let documentHidden = typeof document !== "undefined" ? document.hidden : false;
    const onVisibility = () => {
      documentHidden = typeof document !== "undefined" ? document.hidden : false;
    };

    // --- Idempotent disposal ---
    // Called both from the webglcontextlost handler (synchronously, before
    // activating the fallback) and from the effect cleanup return. The
    // `disposed` flag prevents double-dispose; Three.js dispose() calls are
    // also safe to call repeatedly, but this avoids redundant DOM removal.
    const dispose = () => {
      if (disposed) return;
      disposed = true;
      cancelAnimationFrame(frameId);
      if (resizeObserver) resizeObserver.disconnect();
      renderer.domElement.removeEventListener("pointermove", onPointerMove);
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      renderer.domElement.removeEventListener("pointerleave", onPointerLeave);
      renderer.domElement.removeEventListener("webglcontextlost", onContextLost);
      if (typeof document !== "undefined") {
        document.removeEventListener("visibilitychange", onVisibility);
      }
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      if (renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
    };

    // Handle runtime context loss deterministically: cancel the rAF loop,
    // dispose the renderer, geometry, material, canvas, and all listeners
    // synchronously BEFORE activating the fallback. This avoids leaking GPU
    // resources and avoids a dependency loop that would recreate a broken
    // context (useFallback is intentionally NOT in the effect deps).
    const onContextLost = (e: Event) => {
      e.preventDefault();
      dispose();
      if (mountedRef.current) setUseFallback(true);
    };

    // --- Attach canvas and listeners ---
    const dprCap = lowerPower ? 1.5 : 2;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, dprCap));
    renderer.setSize(width, height, false);
    container.appendChild(renderer.domElement);
    renderer.domElement.setAttribute("aria-hidden", "true");
    renderer.domElement.style.width = "100%";
    renderer.domElement.style.height = "100%";
    renderer.domElement.style.display = "block";
    renderer.domElement.style.touchAction = "pan-x pan-y";
    renderer.domElement.addEventListener("webglcontextlost", onContextLost);
    renderer.domElement.addEventListener("pointermove", onPointerMove, { passive: true });
    renderer.domElement.addEventListener("pointerdown", onPointerDown, { passive: true });
    renderer.domElement.addEventListener("pointerleave", onPointerLeave, { passive: true });
    if (typeof document !== "undefined") {
      document.addEventListener("visibilitychange", onVisibility);
    }

    // --- Resize handling ---
    const onResize = () => {
      width = container.clientWidth;
      height = container.clientHeight;
      if (width === 0 || height === 0) return;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
    };
    resizeObserver = new ResizeObserver(onResize);
    resizeObserver.observe(container);

    // --- Animation loop ---
    const baseSpeed = (speed / 10) * 0.0025;
    const repulsionRadiusPx = cursorRadiusUI;
    const posAttr = geometry.getAttribute("position") as THREE.BufferAttribute;

    const tick = () => {
      frameId = requestAnimationFrame(tick);
      if (documentHidden) return;

      if (!shouldReduce) {
        points.rotation.y += baseSpeed;
        points.rotation.x += baseSpeed * 0.35;
      }

      if (scatterPulse > 0) {
        scatterPulse *= 0.92;
        if (scatterPulse < 0.001) scatterPulse = 0;
      }

      const rect = renderer.domElement.getBoundingClientRect();
      const cx = rect.width / 2;
      const cy = rect.height / 2;

      const arr = posAttr.array as Float32Array;
      const hasPointer = pointer.x < 9000;
      for (let i = 0; i < resolvedCount; i++) {
        const ix = i * 3;
        const bx = basePositions[ix];
        const by = basePositions[ix + 1];
        const bz = basePositions[ix + 2];

        let dispFactor = 0;
        if (hasPointer) {
          const sx = cx + bx * cx * 0.9;
          const sy = cy - by * cy * 0.9;
          const dx = sx - pointer.x;
          const dy = sy - pointer.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < repulsionRadiusPx) {
            const falloff = 1 - dist / repulsionRadiusPx;
            dispFactor += falloff * repulsion;
          }
        }
        if (scatterPulse > 0) {
          dispFactor += scatterPulse * scatter;
        }

        const target = 1 + dispFactor;
        arr[ix] = bx * target;
        arr[ix + 1] = by * target;
        arr[ix + 2] = bz * target;
      }
      posAttr.needsUpdate = true;

      renderer.render(scene, camera);
    };

    if (shouldReduce) {
      renderer.render(scene, camera);
    } else {
      frameId = requestAnimationFrame(tick);
    }

    // --- Cleanup (idempotent; also used by onContextLost) ---
    return dispose;
  }, [
    resolvedColor,
    resolvedCount,
    particleScale,
    speed,
    cursorRadiusUI,
    repulsion,
    scatter,
    shouldReduce,
    lowerPower,
    readySignal,
  ]);

  // --- Lower-power / no-WebGL fallback: a static, structural, non-gradient silhouette.
  // The brand guide bans decorative gradients, so this uses a solid translucent disc
  // with a hairline border and an inset shadow instead of any radial/linear gradient.
  if (useFallback || lowerPower) {
    return (
      <div
        ref={containerRef}
        aria-hidden="true"
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: "70%",
            height: "70%",
            borderRadius: "50%",
            // Solid translucent fill, no gradient.
            backgroundColor: `${resolvedColor}14`,
            border: `1px solid ${resolvedColor}33`,
            boxShadow: `inset 0 0 40px ${resolvedColor}22`,
          }}
        />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      aria-hidden="true"
      style={{ width: "100%", height: "100%" }}
    />
  );
}

export default ParticleSphere;