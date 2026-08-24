import React, { useEffect, useRef, useState, useMemo } from 'react';
import { BotEngine, type BotFrame } from '@/bot/engine';
import { clamp, easings } from '@/bot/math';
import { lookTarget, TURN_TIME } from '@/ui/gaze';
import { DEFAULT_EXPRESSION, EXPRESSION_BY_ID } from '@/bot/expressions';
import { DEFAULT_COLOR, DEFAULT_SHAPE, mixHex, SHAPE_BY_ID } from '@/bot/skins';
import { DEMI_VIEWBOX, RAYON } from '@/bot/repere';
import { STATE_BY_ID, type StateId } from '@/bot/states';
import { NOTIF_BLUE } from '@/bot/decor';

const SIZE = 320;

const R = RAYON;
const VB = DEMI_VIEWBOX;

export const SHAPE_ALIASES: Record<string, string> = {
  circle: 'cercle',
  cercle: 'cercle',
  pebble: 'galet',
  galet: 'galet',
  pabble: 'galet',
  squircle: 'squircle',
  capsule: 'capsule',
  triangle: 'triangle',
  hexagon: 'hexagone',
  hexagone: 'hexagone',
  cloud: 'nuage',
  nuage: 'nuage',
  droplet: 'goutte',
  goutte: 'goutte'
};

export const STATE_ALIASES: Record<string, StateId> = {
  idle: 'idle',
  thinking: 'thinking',
  wink: 'wink',
  wide: 'wide',
  'wide eyes': 'wide',
  alert: 'alert',
  notify: 'notify',
  notification: 'notify',
  exclaim: 'exclaim',
  exclamation: 'exclaim',
  sleep: 'sleep',
  egg: 'egg',
  hexagon: 'hexagon',
  play: 'play',
  orbit: 'orbit',
  burst: 'burst',
  comet: 'comet',
  swirl: 'swirl'
};

export const PROCESSING_SEQUENCE: StateId[] = ['thinking', 'orbit', 'burst', 'comet', 'swirl', 'play'];
export const EYE_ONLY_SEQUENCE: StateId[] = ['idle', 'wink', 'wide', 'alert', 'notify'];

export const DEFAULT_CHAT_SEQUENCE: StateId[] = EYE_ONLY_SEQUENCE;

export const SHAPE_SEQUENCE = ['galet', 'squircle', 'capsule', 'triangle', 'hexagone', 'nuage', 'goutte', 'cercle'];

export default function BloubBot({ 
  size = SIZE, 
  follow = true, 
  expression = 'neutre', 
  shape = 'galet', 
  state,
  autoSequence = true,
  customSequence = EYE_ONLY_SEQUENCE
}: {
  size?: number | string;
  follow?: boolean;
  expression?: string;
  shape?: string;
  state?: string;
  autoSequence?: boolean;
  customSequence?: StateId[];
}) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [shapeIndex, setShapeIndex] = useState(0);
  const [internalStateIndex, setInternalStateIndex] = useState(0);

  const activeShapeName = shape ? (SHAPE_ALIASES[shape.toLowerCase()] || shape) : SHAPE_SEQUENCE[shapeIndex % SHAPE_SEQUENCE.length]!;
  const resolvedShapeKey = useMemo(() => SHAPE_ALIASES[activeShapeName.toLowerCase()] || activeShapeName, [activeShapeName]);
  
  const seqList = customSequence || DEFAULT_CHAT_SEQUENCE;
  // If prop state is passed explicitly use it, otherwise use animated sequence rotation
  const effectiveState = state ? (STATE_ALIASES[state.toLowerCase()] || state) as StateId : seqList[internalStateIndex % seqList.length]!;

  const engine = useMemo(() => {
    const initShape = SHAPE_BY_ID.get(resolvedShapeKey)?.radii || null;
    const initExpr = EXPRESSION_BY_ID.get(expression) || null;
    return new BotEngine(R, effectiveState, initShape, initExpr);
  }, []);

  const [frame, setFrame] = useState<BotFrame | null>(() => {
    try {
      return engine.sample(0);
    } catch {
      return null;
    }
  });

  const clockRef = useRef(0);
  const stateRef = useRef(effectiveState);
  stateRef.current = effectiveState;
  
  // Sync state to engine
  useEffect(() => {
    const now = clockRef.current;
    engine.setState(effectiveState, now);
  }, [engine, effectiveState]);

  // Sync expression to engine
  useEffect(() => {
    const now = clockRef.current || (typeof performance !== 'undefined' ? performance.now() / 1000 : 0);
    const exprObj = EXPRESSION_BY_ID.get(expression) || null;
    engine.setExpression(exprObj, now);
  }, [engine, expression]);

  // Sync shape to engine with smooth easeOutQuint morphing
  useEffect(() => {
    const now = clockRef.current || (typeof performance !== 'undefined' ? performance.now() / 1000 : 0);
    const shapeObj = SHAPE_BY_ID.get(resolvedShapeKey) || null;
    if (shapeObj) {
      engine.setShape(shapeObj.radii, now);
    }
  }, [engine, resolvedShapeKey]);

  const uid = useMemo(() => Math.random().toString(36).slice(2, 8), []);
  const maskId = `bot-mask-${uid}`;

  useEffect(() => {
    let raf = 0;
    let clock = 0;
    let last = 0;
    let aiming = false;
    let turnSince = 0;
    let pointer: { x: number; y: number } | null = null;

    const onPointerMove = (e: PointerEvent) => {
      if (e.pointerType === 'touch') return;
      pointer = { x: e.clientX, y: e.clientY };
    };

    const onPointerLeave = () => {
      pointer = null;
    };

    if (follow) {
      window.addEventListener('pointermove', onPointerMove, { passive: true });
      document.addEventListener('pointerleave', onPointerLeave);
    }

    const release = () => {
      if (!aiming) return;
      engine.setLook(null, clock, TURN_TIME);
      aiming = false;
    };

    const aim = () => {
      const currentState = stateRef.current;
      const st = STATE_BY_ID.get(currentState);
      if (!st?.baseFace && !EYE_ONLY_SEQUENCE.includes(currentState)) {
        release();
        return;
      }
      
      if (!aiming) turnSince = clock;
      const demiLargeur = Math.max(1, window.innerWidth / 2);
      const demiHauteur = Math.max(1, window.innerHeight / 2);
      
      // Calculate normalized cursor position (-1 to 1) relative to screen center
      const nx = pointer ? clamp((pointer.x - demiLargeur) / demiLargeur, -1, 1) : 0;
      const ny = pointer ? clamp((pointer.y - demiHauteur) / demiHauteur, -1, 1) : 0;
      
      engine.setLook(
        lookTarget({
          nx,
          ny,
          tour: easings.easeOutQuint(clamp((clock - turnSince) / TURN_TIME)),
          pointer: pointer !== null
        }),
        clock
      );
      aiming = true;
    };

    let stateTimer = 0;
    const tick = (ms: number) => {
      raf = requestAnimationFrame(tick);
      const dt = last ? Math.min((ms - last) / 1000, 0.064) : 0;
      last = ms;
      clock += dt;
      clockRef.current = clock;

      // Auto cycle sequence if state is not manually forced
      if (autoSequence && !state) {
        stateTimer += dt;
        const currentDef = STATE_BY_ID.get(effectiveState);
        // Use the state definition's natural duration for lively animated states, or 4.5s for calm idle sequences
        const isEyeOnly = seqList.every(s => EYE_ONLY_SEQUENCE.includes(s));
        const duration = isEyeOnly ? Math.max(currentDef?.duration || 3, 4.5) : (currentDef?.duration || 2.4);
        if (stateTimer >= duration) {
          stateTimer = 0;
          setInternalStateIndex((prev) => (prev + 1) % seqList.length);
        }
      } else {
        // Auto-loop active state if it has a defined duration so it never freezes
        const activeDef = STATE_BY_ID.get(effectiveState);
        if (activeDef && activeDef.duration && effectiveState !== 'idle') {
          const elapsed = clock - (engine as any).tCur;
          if (elapsed >= activeDef.duration) {
            engine.setState(effectiveState, clock);
          }
        }
      }

      if (follow) aim();
      
      setFrame(engine.sample(clock));
    };

    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      if (follow) {
        window.removeEventListener('pointermove', onPointerMove);
        document.removeEventListener('pointerleave', onPointerLeave);
      }
    };
  }, [engine, follow]);

  if (!frame) return null;

  const isNumeric = typeof size === 'number';
  const sizeStyle = isNumeric ? { width: `${size}px`, height: `${size}px` } : { width: size, height: size, maxWidth: '100%', aspectRatio: '1 / 1' };

  return (
    <svg
      ref={svgRef}
      viewBox={`${-VB} ${-VB} ${VB * 2} ${VB * 2}`}
      style={{ cursor: 'pointer', ...sizeStyle, display: 'block' }}
      onClick={() => {
        setShapeIndex((prev) => prev + 1);
        setInternalStateIndex((prev) => (prev + 1) % seqList.length);
      }}
    >
      <defs>
        <mask id={maskId} maskUnits="userSpaceOnUse" x={-VB} y={-VB} width={VB * 2} height={VB * 2}>
          <path d={frame.bodyPath} fill="#fff" />
          {frame.notch && (
            <circle cx={frame.notch.x} cy={frame.notch.y} r={frame.notch.r} fill="#000" />
          )}
        </mask>

        {/* Siri Orb Multi-color Swirling Mesh Gradients */}
        <radialGradient id={`siri-core-${uid}`} cx="50%" cy="50%" r="50%" fx="30%" fy="30%">
          <stop offset="0%" stopColor="oklch(95% 0.12 330)" />
          <stop offset="35%" stopColor="oklch(75% 0.22 350)" />
          <stop offset="65%" stopColor="oklch(70% 0.20 285)" />
          <stop offset="100%" stopColor="oklch(65% 0.22 220)" />
        </radialGradient>

        <radialGradient id={`siri-sheen-${uid}`} cx="35%" cy="30%" r="60%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.65" />
          <stop offset="40%" stopColor="#ffffff" stopOpacity="0.15" />
          <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
        </radialGradient>

        <linearGradient id={`siri-rim-${uid}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.8" />
          <stop offset="50%" stopColor="#c084fc" stopOpacity="0.2" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.5" />
        </linearGradient>

        {/* Siri Orb Shimmer Pattern Filter */}
        <filter id={`siri-glow-${uid}`} x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="8" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>

        {frame.arcs.map(arc => (
          <linearGradient
            key={arc.id}
            id={`${uid}-${arc.id}`}
            gradientUnits="userSpaceOnUse"
            x1={arc.grad.x1} y1={arc.grad.y1} x2={arc.grad.x2} y2={arc.grad.y2}
          >
            {arc.grad.stops.map((c, i) => (
              <stop key={i} offset={i / (arc.grad.stops.length - 1)} stopColor={c} />
            ))}
          </linearGradient>
        ))}
      </defs>

      <g fill="none" strokeLinecap="round">
        {frame.arcs.map(arc => (
          <path key={`b${arc.id}`} d={arc.back} stroke={`url(#${uid}-${arc.id})`} strokeWidth={arc.width} opacity={arc.opacity} />
        ))}
      </g>

      {frame.dotsBehind && (
        <g>
          {frame.dots.map((dot, i) => {
            const fill = dot.color ?? (dot.depth === undefined ? '#c084fc' : mixHex('#f43f5e', '#38bdf8', dot.depth));
            if (dot.d) {
              return <path key={i} d={dot.d} transform={`translate(${dot.x} ${dot.y}) rotate(${dot.rot ?? 0}) scale(${R})`} fill={fill} opacity={dot.opacity} />;
            }
            return <circle key={i} cx={dot.x} cy={dot.y} r={dot.r} fill={fill} opacity={dot.opacity} />;
          })}
        </g>
      )}

      <g opacity={frame.bodyAlpha}>
        {/* Siri-Orb Multi-Layered Shader Body Texture */}
        <g filter={`url(#siri-glow-${uid})`}>
          {/* Base Siri Gradient Core */}
          <path d={frame.bodyPath} fill={`url(#siri-core-${uid})`} mask={`url(#${maskId})`} />
          {/* Glass Sheen Drift Layer */}
          <path d={frame.bodyPath} fill={`url(#siri-sheen-${uid})`} mask={`url(#${maskId})`} style={{ mixBlendMode: 'screen' }} />
          {/* Specular Depth Rim */}
          <path d={frame.bodyPath} fill="none" stroke={`url(#siri-rim-${uid})`} strokeWidth="3" opacity="0.6" />
        </g>
        
        {/* Render Eyes Directly on Top of Shader Body with Ink Cutout */}
        <g>
          {frame.eyes.map((eye, i) => (
            <path 
              key={i} 
              d={eye.d} 
              transform={eye.matrix} 
              opacity={eye.alpha} 
              fill="#0a0a0c" 
            />
          ))}
        </g>
      </g>

      {!frame.dotsBehind && (
        <g>
          {frame.dots.map((dot, i) => {
            const fill = dot.color ?? (dot.depth === undefined ? '#c084fc' : mixHex('#f43f5e', '#38bdf8', dot.depth));
            if (dot.d) {
              return <path key={i} d={dot.d} transform={`translate(${dot.x} ${dot.y}) rotate(${dot.rot ?? 0}) scale(${R})`} fill={fill} opacity={dot.opacity} />;
            }
            return <circle key={i} cx={dot.x} cy={dot.y} r={dot.r} fill={fill} opacity={dot.opacity} />;
          })}
        </g>
      )}

      {frame.notif && (
        <circle cx={frame.notif.x} cy={frame.notif.y} r={frame.notif.r} fill={NOTIF_BLUE} />
      )}

      <g fill="none" strokeLinecap="round">
        {frame.arcs.map(arc => (
          <path key={`f${arc.id}`} d={arc.front} stroke={`url(#${uid}-${arc.id})`} strokeWidth={arc.width} opacity={arc.opacity} />
        ))}
      </g>
    </svg>
  );
}
