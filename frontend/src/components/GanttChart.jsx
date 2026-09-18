import { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine, Cell,
} from 'recharts';
import styles from './GanttChart.module.css';

const DAY_MS = 86400000;

const STATUS_COLOR = {
  done:      'var(--nom-success)',
  remaining: 'var(--nom-border-solid)',
};

function toDate(value) {
  if (!value) return null;
  return value instanceof Date ? value : new Date(`${value}T00:00:00`);
}

function fmtDate(d) {
  return d.toLocaleDateString('es-MX', { day: '2-digit', month: 'short' });
}

function GanttTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div className={styles.tooltip}>
      <div className={styles.tooltipLabel}>{row.label}</div>
      <div className={styles.tooltipRange}>{fmtDate(row.startDate)} — {fmtDate(row.endDate)}</div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipDot} style={{ background: STATUS_COLOR.done }} />
        <span>{row.completadas} de {row.total} acciones completadas</span>
      </div>
      <div className={styles.tooltipPct}>{Math.round(row.pct * 100)}% de avance</div>
    </div>
  );
}

/**
 * Gantt de fases del plan de accion.
 * `phases`: [{ label, start, end, total, completadas }]
 * start/end aceptan Date o 'YYYY-MM-DD'.
 */
export default function GanttChart({ phases }) {
  const { rows, minDate, totalDays, ticks, todayOffset } = useMemo(() => {
    const norm = phases
      .map(p => {
        const start = toDate(p.start);
        let end = toDate(p.end);
        if (!start || !end) return null;
        if (end < start) end = start;
        return { ...p, startDate: start, endDate: end };
      })
      .filter(Boolean)
      .sort((a, b) => a.startDate - b.startDate);

    if (norm.length === 0) {
      return { rows: [], minDate: null, totalDays: 0, ticks: [], todayOffset: null };
    }

    const minDate  = new Date(Math.min(...norm.map(p => p.startDate)));
    const maxDate  = new Date(Math.max(...norm.map(p => p.endDate)));
    const totalDays = Math.max(1, Math.round((maxDate - minDate) / DAY_MS));

    const rows = norm.map(p => {
      const offset   = Math.max(0, (p.startDate - minDate) / DAY_MS);
      const duration = Math.max((p.endDate - p.startDate) / DAY_MS, totalDays * 0.012, 1);
      const pct      = p.total ? p.completadas / p.total : 0;
      return {
        label: p.label,
        startDate: p.startDate,
        endDate: p.endDate,
        total: p.total,
        completadas: p.completadas,
        pct,
        offset,
        done: duration * pct,
        remaining: duration * (1 - pct),
      };
    });

    const tickCount = 6;
    const ticks = Array.from({ length: tickCount + 1 }, (_, i) =>
      Math.round((totalDays / tickCount) * i)
    );

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayOffsetRaw = (today - minDate) / DAY_MS;
    const todayOffset = todayOffsetRaw >= 0 && todayOffsetRaw <= totalDays ? todayOffsetRaw : null;

    return { rows, minDate, totalDays, ticks, todayOffset };
  }, [phases]);

  if (rows.length === 0) {
    return <div className={styles.empty}>Sin fechas suficientes para trazar el cronograma.</div>;
  }

  const height = Math.max(180, rows.length * 40 + 48);

  return (
    <div className={styles.wrap}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={rows}
          layout="vertical"
          barCategoryGap={10}
          margin={{ top: 8, right: 24, left: 8, bottom: 4 }}
        >
          <CartesianGrid horizontal={false} stroke="var(--nom-border)" />
          <XAxis
            type="number"
            domain={[0, totalDays]}
            ticks={ticks}
            tickFormatter={d => fmtDate(new Date(minDate.getTime() + d * DAY_MS))}
            tick={{ fill: 'var(--nom-text-muted)', fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: 'var(--nom-border-solid)' }}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={220}
            tick={{ fill: 'var(--nom-text)', fontSize: 12 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<GanttTooltip />} cursor={{ fill: 'var(--nom-bg-subtle)' }} />
          {todayOffset != null && (
            <ReferenceLine
              x={todayOffset}
              stroke="var(--nom-accent)"
              strokeDasharray="4 3"
              label={{ value: 'Hoy', position: 'insideTopRight', fill: 'var(--nom-accent)', fontSize: 10 }}
            />
          )}
          <Bar dataKey="offset" stackId="gantt" fill="transparent" isAnimationActive={false} />
          <Bar dataKey="done" stackId="gantt" radius={[3, 0, 0, 3]} isAnimationActive={false}>
            {rows.map((r, i) => <Cell key={i} fill={STATUS_COLOR.done} />)}
          </Bar>
          <Bar dataKey="remaining" stackId="gantt" radius={[0, 3, 3, 0]} isAnimationActive={false}>
            {rows.map((r, i) => <Cell key={i} fill={STATUS_COLOR.remaining} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className={styles.legend}>
        <span className={styles.legendItem}>
          <span className={styles.legendDot} style={{ background: STATUS_COLOR.done }} />
          Completado
        </span>
        <span className={styles.legendItem}>
          <span className={styles.legendDot} style={{ background: STATUS_COLOR.remaining }} />
          Pendiente / en progreso
        </span>
      </div>
    </div>
  );
}
