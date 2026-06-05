import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChartCard, { RISK_COLORS, RISK_LABELS, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

const CATS = ['nulo', 'bajo', 'medio', 'alto', 'muy_alto'];

function MiniDist({ distribucion }) {
  const total = CATS.reduce((s, c) => s + (distribucion?.[c] ?? 0), 0);
  if (!total) return null;
  return (
    <div className={styles.dominioMiniDist}>
      {CATS.map(c => {
        const n   = distribucion?.[c] ?? 0;
        const pct = total > 0 ? (n / total) * 100 : 0;
        if (pct < 1) return null;
        return (
          <div
            key={c}
            className={styles.dominioMiniSeg}
            style={{ width: `${pct}%`, background: RISK_COLORS[c] }}
          />
        );
      })}
    </div>
  );
}

function DistTooltip({ dominio, pos }) {
  if (!dominio) return null;
  const dist  = dominio.distribucion ?? {};
  const total = CATS.reduce((s, c) => s + (dist[c] ?? 0), 0);
  return (
    <AnimatePresence>
      <motion.div
        className={styles.domTooltip}
        style={{ left: pos.x, top: pos.y }}
        initial={{ opacity: 0, scale: 0.93, y: 5 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.93 }}
        transition={{ duration: 0.14 }}
      >
        <div className={styles.domTooltipTitle}>{dominio.dominio_nombre}</div>
        {total > 0 && (
          <div className={styles.domTooltipTotal}>{total} trabajadores evaluados</div>
        )}
        <div className={styles.domTooltipDivider} />
        {CATS.map(c => {
          const n = dist[c] ?? 0;
          if (!n) return null;
          const pct = Math.round((n / total) * 100);
          return (
            <div key={c} className={styles.domTooltipRow}>
              <span className={styles.domTooltipDot} style={{ background: RISK_COLORS[c] }} />
              <span className={styles.domTooltipCat}>{RISK_LABELS[c]}</span>
              <span className={styles.domTooltipPct}>{pct}%</span>
              <span className={styles.domTooltipN}>{n}</span>
            </div>
          );
        })}
      </motion.div>
    </AnimatePresence>
  );
}

function DominioBar({ item, index }) {
  const [hovered, setHovered] = useState(false);
  const [pos, setPos]         = useState({ x: 0, y: 0 });

  const cat    = item.categoria_modal ?? 'nulo';
  const color  = RISK_COLORS[cat];
  const pct    = item.pct_promedio ?? 0;
  const isHigh = cat === 'alto' || cat === 'muy_alto';

  const handleMove = (e) => {
    const rect = e.currentTarget.closest('[data-barwrap]').getBoundingClientRect();
    setPos({ x: e.clientX - rect.left + 14, y: e.clientY - rect.top - 52 });
  };

  return (
    <motion.div
      className={`${styles.dominioRow} ${isHigh ? styles.dominioRowHigh : ''}`}
      style={isHigh ? { '--row-accent': color } : undefined}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.035, duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onMouseMove={handleMove}
    >
      {/* Left: key + name */}
      <div className={styles.dominioMeta}>
        <span className={styles.dominioKey}>{item.dominio_clave}</span>
        <span className={styles.dominioNombre}>{item.dominio_nombre ?? ''}</span>
      </div>

      {/* Bar + mini dist */}
      <div className={styles.dominioBarCol}>
        <div className={styles.dominioTrack}>
          <motion.div
            className={styles.dominioFill}
            style={{
              background: `linear-gradient(90deg, ${color}99, ${color}ee)`,
              boxShadow: isHigh ? `0 0 12px 0 ${color}44` : undefined,
            }}
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ delay: index * 0.035 + 0.1, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className={styles.dominioFillShine} />
          </motion.div>
          {hovered && <DistTooltip dominio={item} pos={pos} />}
        </div>
        <MiniDist distribucion={item.distribucion} />
      </div>

      {/* Right: pct + chip */}
      <span className={styles.dominioPct}>{pct}%</span>
      <span
        className={styles.dominioNivel}
        style={{ color, background: `${color}18`, borderColor: `${color}28` }}
      >
        {RISK_LABELS[cat]}
      </span>
    </motion.div>
  );
}

export default function BarDominios({ data }) {
  if (!data?.length) return (
    <ChartCard title="Nivel de Riesgo por Dominio"><EmptyChart height={220} /></ChartCard>
  );

  return (
    <ChartCard
      title="Nivel de Riesgo por Dominio"
      subtitle="% promedio de puntaje — hover para distribución completa"
    >
      <div className={styles.dominioList} data-barwrap="">
        {data.map((item, i) => (
          <DominioBar key={item.dominio_clave} item={item} index={i} />
        ))}
      </div>
    </ChartCard>
  );
}
