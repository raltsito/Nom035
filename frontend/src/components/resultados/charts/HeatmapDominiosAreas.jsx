import { useState, useMemo, useRef, Fragment } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChartCard, { RISK_COLORS, RISK_LABELS, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return [r, g, b];
}

function lerpColor(pct) {
  const stops = [
    [0,   hexToRgb(RISK_COLORS.nulo)],
    [25,  hexToRgb(RISK_COLORS.bajo)],
    [50,  hexToRgb(RISK_COLORS.medio)],
    [75,  hexToRgb(RISK_COLORS.alto)],
    [100, hexToRgb(RISK_COLORS.muy_alto)],
  ];
  for (let i = 0; i < stops.length - 1; i++) {
    const [p0, c0] = stops[i];
    const [p1, c1] = stops[i + 1];
    if (pct <= p1) {
      const t = (pct - p0) / (p1 - p0);
      return c0.map((v, j) => Math.round(v + (c1[j] - v) * t));
    }
  }
  return hexToRgb(RISK_COLORS.muy_alto);
}

function cellBg(pct, alpha = 1) {
  const [r, g, b] = lerpColor(pct);
  return `rgba(${r},${g},${b},${alpha})`;
}

export default function HeatmapDominiosAreas({ data }) {
  const [hovered, setHovered]       = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const wrapRef                     = useRef(null);

  const { dominios, areas, grid } = useMemo(() => {
    if (!data?.length) return { dominios: [], areas: [], grid: {} };
    const doms    = data.map(d => ({ clave: d.dominio_clave, nombre: d.dominio_nombre }));
    const areaSet = new Set();
    data.forEach(d => Object.keys(d.por_area ?? {}).forEach(a => areaSet.add(a)));
    const areaList = [...areaSet].sort();
    const g = {};
    data.forEach(d => {
      g[d.dominio_clave] = {};
      areaList.forEach(a => { g[d.dominio_clave][a] = d.por_area?.[a] ?? null; });
    });
    return { dominios: doms, areas: areaList, grid: g };
  }, [data]);

  if (!dominios.length || !areas.length) return (
    <ChartCard title="Mapa de Calor Dominios × Áreas"><EmptyChart /></ChartCard>
  );

  const gridCols = `56px repeat(${areas.length}, minmax(56px, 1fr))`;

  const handleCellEnter = (e, cellData) => {
    if (!wrapRef.current) return;
    const wr = wrapRef.current.getBoundingClientRect();
    const cr = e.currentTarget.getBoundingClientRect();
    setTooltipPos({
      x: cr.left - wr.left + cr.width / 2,
      y: cr.top  - wr.top  - 10,
    });
    setHovered(cellData);
  };

  return (
    <ChartCard title="Mapa de Calor Dominios × Áreas" subtitle="Nivel de riesgo promedio por área">
      <div className={styles.hmScrollContainer} ref={wrapRef}>
        <div className={styles.hmGrid} style={{ gridTemplateColumns: gridCols }}>

          {/* Corner */}
          <div className={styles.hmCorner} />

          {/* Area column headers */}
          {areas.map((area, ci) => (
            <motion.div
              key={area}
              className={styles.hmColHeader}
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: ci * 0.03, duration: 0.3 }}
            >
              <span className={styles.hmColHeaderText} title={area}>
                {area.length > 14 ? area.slice(0, 13) + '…' : area}
              </span>
            </motion.div>
          ))}

          {/* Data rows */}
          {dominios.map((dom, ri) => (
            <Fragment key={dom.clave}>
              <motion.div
                className={styles.hmRowLabel}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: ri * 0.025, duration: 0.3 }}
                title={dom.nombre}
              >
                {dom.clave}
              </motion.div>

              {areas.map((area, ci) => {
                const cell  = grid[dom.clave]?.[area];
                const delay = (ri * areas.length + ci) * 0.006;

                if (!cell) {
                  return (
                    <motion.div
                      key={area}
                      className={styles.hmCellEmpty}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay, duration: 0.25 }}
                    />
                  );
                }

                const { pct, n, categoria } = cell;
                const isHov = hovered?.dominio === dom.clave && hovered?.area === area;

                return (
                  <motion.div
                    key={area}
                    className={`${styles.hmCell} ${isHov ? styles.hmCellHov : ''}`}
                    style={{ background: cellBg(pct, isHov ? 1 : 0.86) }}
                    initial={{ opacity: 0, scale: 0.72 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay, duration: 0.3, ease: 'easeOut' }}
                    onMouseEnter={(e) =>
                      handleCellEnter(e, { dominio: dom.clave, area, pct, n, categoria })
                    }
                    onMouseLeave={() => setHovered(null)}
                  >
                    <span className={styles.hmCellVal}>{pct}</span>
                  </motion.div>
                );
              })}
            </Fragment>
          ))}
        </div>

        {/* Floating tooltip */}
        <AnimatePresence>
          {hovered && (
            <motion.div
              className={styles.hmTooltip}
              style={{
                left:      tooltipPos.x,
                top:       tooltipPos.y,
                transform: 'translate(-50%, -100%)',
              }}
              initial={{ opacity: 0, y: 6, scale: 0.93 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.93 }}
              transition={{ duration: 0.13 }}
            >
              <div className={styles.hmTooltipTitle}>
                {hovered.dominio} × {hovered.area}
              </div>
              <div className={styles.hmTooltipRow}>
                <span
                  className={styles.hmTooltipDot}
                  style={{ background: cellBg(hovered.pct, 1) }}
                />
                <span>
                  {hovered.pct}% — {RISK_LABELS[hovered.categoria] ?? hovered.categoria}
                </span>
              </div>
              <div className={styles.hmTooltipSub}>{hovered.n} trabajadores</div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Color scale legend */}
        <div className={styles.hmLegend}>
          <span className={styles.hmLegendLabel}>Nulo</span>
          <div className={styles.hmLegendBar} />
          <span className={styles.hmLegendLabel}>Muy alto</span>
        </div>
      </div>
    </ChartCard>
  );
}
