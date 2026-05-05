import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';
import ChartCard, { RISK_COLORS, ChartTooltip, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

function categoriaFromPct(pct) {
  if (pct <= 20) return 'nulo';
  if (pct <= 40) return 'bajo';
  if (pct <= 60) return 'medio';
  if (pct <= 80) return 'alto';
  return 'muy_alto';
}

export default function BarDominios({ data }) {
  if (!data?.length) return <ChartCard title="Dominios NOM-035"><EmptyChart height={220} /></ChartCard>;

  return (
    <ChartCard title="Nivel de Riesgo por Dominio" subtitle="Porcentaje promedio de puntaje">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 4, right: 52, left: 8, bottom: 4 }}
          barSize={14}
        >
          <CartesianGrid horizontal={false} stroke="rgba(255,255,255,0.05)" />
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fill: '#6E8BAA', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={v => `${v}%`}
          />
          <YAxis
            type="category"
            dataKey="clave"
            width={28}
            tick={{ fill: '#6E8BAA', fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            content={
              <ChartTooltip
                formatter={(v, name, props) => {
                  const d = props?.payload;
                  return `${v}% — ${d?.nombre || ''}`;
                }}
              />
            }
          />
          <Bar dataKey="pct" radius={[0, 6, 6, 0]} name="Riesgo">
            {data.map((d, i) => (
              <Cell key={i} fill={RISK_COLORS[categoriaFromPct(d.pct)]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
