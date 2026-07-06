import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip,
} from 'recharts';
import { motion } from 'framer-motion';
import ChartCard, { ACCENT, EmptyChart, RISK_COLORS, RISK_LABELS } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

function AxisTick({ payload, x, y, textAnchor }) {
  const lines = payload.value.split('\n');
  return (
    <text x={x} y={y} textAnchor={textAnchor} fill="#6E8BAA" fontSize={11} fontFamily="Inter, system-ui, sans-serif">
      {lines.map((l, i) => (
        <tspan key={i} x={x} dy={i === 0 ? 0 : 14}>{l}</tspan>
      ))}
    </text>
  );
}

function CustomDot(props) {
  const { cx, cy } = props;
  return (
    <motion.circle
      cx={cx} cy={cy} r={5}
      fill={ACCENT}
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ duration: 0.4, delay: 0.8 }}
      style={{ transformOrigin: `${cx}px ${cy}px` }}
    />
  );
}

// Tooltip con la calificación (nivel de riesgo) en lugar del porcentaje
function RadarTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  const color = RISK_COLORS[d.categoria] || ACCENT;
  return (
    <div className={styles.tooltip}>
      <div className={styles.tooltipLabel}>{d.subject.replace('\n', ' ')}</div>
      <div className={styles.tooltipRow}>
        <span className={styles.tooltipDot} style={{ background: color }} />
        <span className={styles.tooltipName}>Nivel de riesgo</span>
        <span className={styles.tooltipVal} style={{ color }}>
          {RISK_LABELS[d.categoria] || d.categoria}
        </span>
      </div>
    </div>
  );
}

export default function RadarCategorias({ data }) {
  if (!data?.length) return <ChartCard title="Perfil de Riesgo por Dimensión"><EmptyChart /></ChartCard>;

  return (
    <ChartCard title="Perfil de Riesgo por Dimensión" subtitle="5 macro-dimensiones NOM-035-STPS-2018">
      <ResponsiveContainer width="100%" height={270}>
        <RadarChart data={data} margin={{ top: 18, right: 44, bottom: 18, left: 44 }}>
          <defs>
            <radialGradient id="radarGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%"   stopColor={ACCENT} stopOpacity={0.35} />
              <stop offset="100%" stopColor={ACCENT} stopOpacity={0.05} />
            </radialGradient>
          </defs>
          <PolarGrid stroke="rgba(255,255,255,0.07)" />
          <PolarAngleAxis dataKey="subject" tick={<AxisTick />} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar
            name="Nivel de riesgo"
            dataKey="valor"
            stroke={ACCENT}
            fill="url(#radarGrad)"
            strokeWidth={2}
            dot={<CustomDot />}
            animationBegin={100}
            animationDuration={1100}
          />
          <Tooltip content={<RadarTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
