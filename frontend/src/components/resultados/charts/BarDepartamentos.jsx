import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';
import { motion } from 'framer-motion';
import ChartCard, { RISK_COLORS, RISK_LABELS, ChartTooltip, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

const CATS = [
  { key: 'nulo',     name: RISK_LABELS.nulo     },
  { key: 'bajo',     name: RISK_LABELS.bajo     },
  { key: 'medio',    name: RISK_LABELS.medio    },
  { key: 'alto',     name: RISK_LABELS.alto     },
  { key: 'muy_alto', name: RISK_LABELS.muy_alto },
];

export default function BarDepartamentos({ data }) {
  if (!data?.length) return <ChartCard title="Áreas Críticas"><EmptyChart /></ChartCard>;

  return (
    <ChartCard title="Riesgo por Departamento" subtitle="Distribución de niveles por área">
      <motion.div
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      >
        <ResponsiveContainer width="100%" height={230}>
          <BarChart
            layout="vertical"
            data={data}
            margin={{ top: 4, right: 8, left: 8, bottom: 4 }}
            barSize={10}
            barCategoryGap="30%"
          >
            <CartesianGrid horizontal={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis
              type="number"
              allowDecimals={false}
              tick={{ fill: '#6E8BAA', fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              type="category"
              dataKey="area"
              width={90}
              tick={{ fill: '#6E8BAA', fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<ChartTooltip />} />
            {CATS.map((c, i) => (
              <Bar
                key={c.key}
                dataKey={c.key}
                name={c.name}
                fill={RISK_COLORS[c.key]}
                radius={i === CATS.length - 1 ? [0, 4, 4, 0] : [0, 0, 0, 0]}
                stackId="a"
                animationBegin={i * 80}
                animationDuration={700}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </ChartCard>
  );
}
