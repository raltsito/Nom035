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

// Peso para ordenar las áreas de mayor a menor riesgo
const PESO = { nulo: 0, bajo: 1, medio: 2, alto: 3, muy_alto: 4 };

function severidad(area) {
  const total = CATS.reduce((s, c) => s + (area[c.key] ?? 0), 0);
  if (!total) return 0;
  return CATS.reduce((s, c) => s + PESO[c.key] * (area[c.key] ?? 0), 0) / total;
}

// Alto por fila para que las barras nunca se empalmen aunque haya muchas áreas
const ROW_H  = 34;
const MIN_H  = 230;

export default function BarDepartamentos({ data }) {
  if (!data?.length) return <ChartCard title="Áreas Críticas"><EmptyChart /></ChartCard>;

  const ordenadas = [...data].sort((a, b) => severidad(b) - severidad(a));
  const height    = Math.max(MIN_H, ordenadas.length * ROW_H + 30);

  return (
    <ChartCard title="Riesgo por Departamento" subtitle="Distribución de niveles por área — ordenado de mayor a menor riesgo">
      <motion.div
        initial={{ opacity: 0, x: 16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      >
        <ResponsiveContainer width="100%" height={height}>
          <BarChart
            layout="vertical"
            data={ordenadas}
            margin={{ top: 4, right: 8, left: 8, bottom: 4 }}
            barSize={12}
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
              width={110}
              interval={0}
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
