import { motion } from 'framer-motion';
import ChartCard, { RISK_COLORS, RISK_LABELS } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

// ── Layout ──────────────────────────────────────────────────────────────────
const SVG_W     = 220;
const SVG_H     = 220;
const CX        = 110;
const CY        = 110;
const R         = 78;            // mid-radius of the arc ring
const TRACK_W   = 15;            // ring thickness
const CIRC      = 2 * Math.PI * R;

// 270° arc, gap of 90° at the bottom. Starts at 135° (lower-left) CW to 45° (lower-right).
const TOTAL_DEG = 270;
const START_DEG = 135;
const SEG_N     = 5;
const SEG_DEG   = TOTAL_DEG / SEG_N;   // 54° each

// Segment dash length — fits round-capped ends without overlap
const TOTAL_LEN  = (TOTAL_DEG / 360) * CIRC;
const SEG_GAP_PX = TRACK_W + 2;        // visual gap between rounded caps
const SEG_LEN    = (TOTAL_LEN - SEG_N * SEG_GAP_PX) / SEG_N;

const CATS    = ['nulo', 'bajo', 'medio', 'alto', 'muy_alto'];
const CAT_IDX = { nulo: 0, bajo: 1, medio: 2, alto: 3, muy_alto: 4 };

// Cortes de `score` (0-4) que usa scoreToCategoria() en useDashboardData.js —
// deben coincidir exactamente, si no el punto puede caer en un segmento de
// color distinto al de la categoría/etiqueta mostrada.
const SCORE_BOUNDS = [0, 0.5, 1.5, 2.5, 3.5, 4];

// ── Helpers ──────────────────────────────────────────────────────────────────
function toRad(deg) { return (deg * Math.PI) / 180; }

function arcPoint(deg) {
  return { x: CX + R * Math.cos(toRad(deg)), y: CY + R * Math.sin(toRad(deg)) };
}

// ── Segment (non-framer SVG) ──────────────────────────────────────────────
// Uses a plain <g rotate> + CSS opacity transition — avoids framer+SVG transform conflicts
function Segment({ cat, index, opacity, strokeWidth }) {
  const rotDeg = START_DEG + index * SEG_DEG;
  return (
    <g transform={`rotate(${rotDeg}, ${CX}, ${CY})`}>
      <circle
        cx={CX} cy={CY} r={R}
        fill="none"
        stroke={RISK_COLORS[cat]}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={`${SEG_LEN} ${CIRC}`}
        style={{ opacity, transition: `opacity 0.5s ease ${index * 0.07}s` }}
      />
    </g>
  );
}

// ── Component ─────────────────────────────────────────────────────────────
export default function GaugeRiesgo({ data }) {
  const score    = data?.score ?? 0;
  const categoria = data?.categoria ?? 'nulo';
  const catIdx   = CAT_IDX[categoria] ?? 0;
  const color    = RISK_COLORS[categoria] ?? RISK_COLORS.nulo;

  if (!data) return (
    <ChartCard title="Riesgo Psicosocial Global">
      <div className={styles.gaugeEmpty}>Sin datos calculados</div>
    </ChartCard>
  );

  // Posición del punto: se ubica DENTRO del segmento de su propia categoría
  // (catIdx), proporcional a dónde cae `score` en el rango de esa categoría.
  // Antes se usaba un `pct` lineal (0-100) que no coincidía con los cortes
  // reales de scoreToCategoria(), y el punto podía caer en un segmento de
  // color distinto al de la etiqueta mostrada.
  const lo   = SCORE_BOUNDS[catIdx];
  const hi   = SCORE_BOUNDS[catIdx + 1];
  const frac = hi > lo ? Math.min(1, Math.max(0, (score - lo) / (hi - lo))) : 0.5;
  const dotDeg = START_DEG + ((catIdx + frac) / SEG_N) * TOTAL_DEG;
  const dot    = arcPoint(dotDeg);

  // Etiqueta central — solo la calificación, sin porcentaje
  const nivelLabel  = RISK_LABELS[categoria] ?? categoria;
  const nivelFontSz = nivelLabel.length > 6 ? 27 : 34;

  return (
    <ChartCard title="Riesgo Psicosocial Global" subtitle="Índice ponderado Guía III">
      <div className={styles.gaugeWrap}>
        {/* No overflow:visible — SVG is self-contained, no backdrop-filter clipping issues */}
        <svg
          width={SVG_W}
          height={SVG_H}
          viewBox={`0 0 ${SVG_W} ${SVG_H}`}
          style={{ display: 'block', margin: '0 auto' }}
        >
          {/* ── Segments ─────────────────────────────────────────────── */}
          {CATS.map((cat, i) => {
            const isPast   = i < catIdx;
            const isActive = i === catIdx;
            const opacity  = isPast ? 0.55 : isActive ? 1.0 : 0.10;
            const sw       = isActive ? TRACK_W + 5 : TRACK_W;
            return (
              <Segment key={cat} cat={cat} index={i} opacity={opacity} strokeWidth={sw} />
            );
          })}

          {/* ── Tick marks at segment boundaries ─────────────────────── */}
          {Array.from({ length: SEG_N + 1 }, (_, i) => {
            const a  = toRad(START_DEG + i * SEG_DEG);
            const r1 = R + TRACK_W / 2 + 4;
            const r2 = R + TRACK_W / 2 + 11;
            return (
              <line key={i}
                x1={CX + r1 * Math.cos(a)} y1={CY + r1 * Math.sin(a)}
                x2={CX + r2 * Math.cos(a)} y2={CY + r2 * Math.sin(a)}
                stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" opacity={0.18}
              />
            );
          })}

          {/* ── NULO / MÁX labels ─────────────────────────────────────── */}
          {[
            { i: 0, label: 'NULO', anchor: 'middle' },
            { i: 5, label: 'MÁX',  anchor: 'middle' },
          ].map(({ i, label, anchor }) => {
            const a  = toRad(START_DEG + i * SEG_DEG);
            const lr = R + TRACK_W / 2 + 22;
            return (
              <text key={label}
                x={CX + lr * Math.cos(a)} y={CY + lr * Math.sin(a)}
                textAnchor={anchor} fontSize="7"
                fontFamily="var(--nom-font-mono, monospace)"
                fontWeight="600" fill="currentColor" opacity={0.30}
                letterSpacing="0.06em"
              >
                {label}
              </text>
            );
          })}

          {/* ── Position dot ──────────────────────────────────────────── */}
          {score > 0 && (
            <motion.g
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7, duration: 0.4 }}
            >
              <circle cx={dot.x} cy={dot.y} r={13} fill={color} opacity={0.13} />
              <circle cx={dot.x} cy={dot.y} r={8}  fill={color} opacity={0.28} />
              <circle cx={dot.x} cy={dot.y} r={4.5} fill={color} />
              <circle cx={dot.x} cy={dot.y} r={2}  fill="white" opacity={0.92} />
            </motion.g>
          )}

          {/* ── Calificación central (sin porcentaje) ─────────────────── */}
          <motion.text
            x={CX} y={CY + 6}
            textAnchor="middle"
            fontSize={nivelFontSz} fontWeight="800"
            fontFamily="var(--nom-font-display, 'Plus Jakarta Sans', sans-serif)"
            fill={color}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.38, duration: 0.42 }}
          >
            {nivelLabel}
          </motion.text>
          <motion.text
            x={CX} y={CY + 30}
            textAnchor="middle"
            fontSize="10" fontWeight="600"
            fontFamily="var(--nom-font-body, Inter, sans-serif)"
            fill="currentColor" opacity={0.45}
            letterSpacing="0.04em"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.45 }}
            transition={{ delay: 0.62, duration: 0.35 }}
          >
            Nivel de riesgo
          </motion.text>
        </svg>
      </div>
    </ChartCard>
  );
}
