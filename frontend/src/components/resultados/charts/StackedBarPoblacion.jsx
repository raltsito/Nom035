import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';
import ChartCard, { RISK_COLORS, RISK_LABELS, ChartTooltip, EmptyChart } from '../ChartCard';

const CATS = [
  { key: 'nulo',     label: RISK_LABELS.nulo     },
  { key: 'bajo',     label: RISK_LABELS.bajo     },
  { key: 'medio',    label: RISK_LABELS.medio    },
  { key: 'alto',     label: RISK_LABELS.alto     },
  { key: 'muy_alto', label: RISK_LABELS.muy_alto },
];

export default function StackedBarPoblacion({ data }) {
  if (!data?.length) return (
    <ChartCard title="Distribución Demográfica"><EmptyChart /></ChartCard>
  );

  return (
    <ChartCard title="Distribución por Perfil de Puesto" subtitle="Nivel de riesgo según tipo de puesto (Guía V)">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      >
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 8 }} barSize={48}>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="perfil"
              tick={{ fill: '#6E8BAA', fontSize: 11 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fill: '#6E8BAA', fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<ChartTooltip />} />
            {CATS.map((c, i) => (
              <Bar
                key={c.key}
                dataKey={c.key}
                name={c.label}
                stackId="s"
                fill={RISK_COLORS[c.key]}
                radius={i === CATS.length - 1 ? [5, 5, 0, 0] : [0, 0, 0, 0]}
                animationBegin={i * 60}
                animationDuration={650}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>

        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 10 }}>
          {CATS.map(c => (
            <div key={c.key} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 9, height: 9, borderRadius: 2, background: RISK_COLORS[c.key], flexShrink: 0 }} />
              <span style={{ fontSize: 11, color: '#6E8BAA' }}>{c.label}</span>
            </div>
          ))}
        </div>
      </motion.div>
    </ChartCard>
  );
}
