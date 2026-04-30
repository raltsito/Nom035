import styles from './ResultadosDashboard.module.css';

export default function ChartCard({ title, subtitle, children, className, style }) {
  return (
    <div className={`nom-card ${styles.chartCard} ${className || ''}`} style={style}>
      {(title || subtitle) && (
        <div className={styles.cardHeader}>
          {title && <span className={styles.cardTitle}>{title}</span>}
          {subtitle && <span className={styles.cardSubtitle}>{subtitle}</span>}
        </div>
      )}
      <div className={styles.cardBody}>{children}</div>
    </div>
  );
}

export function EmptyChart({ height = 160 }) {
  return (
    <div className={styles.emptyChart} style={{ height }}>
      Sin datos suficientes para este ciclo
    </div>
  );
}

export const RISK_COLORS = {
  bajo:     '#84CC16',
  medio:    '#F59E0B',
  alto:     '#EF4444',
  muy_alto: '#7C3AED',
};

export const RISK_LABELS = {
  bajo:     'Nulo / Bajo',
  medio:    'Medio',
  alto:     'Alto',
  muy_alto: 'Muy Alto',
};

export const ACCENT   = '#03C4CE';
export const SURFACE  = 'rgba(255,255,255,0.06)';
export const MUTED    = '#6E8BAA';
export const TEXT     = '#0D1526';

export function RiskChip({ cat }) {
  const color = RISK_COLORS[cat] || RISK_COLORS.bajo;
  return (
    <span
      className={styles.riskChip}
      style={{ color, background: `${color}18` }}
    >
      {RISK_LABELS[cat] || cat}
    </span>
  );
}

export function ChartTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      {label && <div className={styles.tooltipLabel}>{label}</div>}
      {payload.map((p, i) => (
        <div key={i} className={styles.tooltipRow}>
          <span className={styles.tooltipDot} style={{ background: p.fill || p.color }} />
          <span className={styles.tooltipName}>{p.name}</span>
          <span className={styles.tooltipVal}>
            {formatter ? formatter(p.value, p.name) : p.value}
          </span>
        </div>
      ))}
    </div>
  );
}
