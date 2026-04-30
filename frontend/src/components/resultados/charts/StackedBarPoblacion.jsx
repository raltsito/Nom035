import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import ChartCard, { RISK_COLORS, RISK_LABELS, ChartTooltip, EmptyChart } from '../ChartCard';

const CATS = [
  { key: 'bajo',     label: RISK_LABELS.bajo     },
  { key: 'medio',    label: RISK_LABELS.medio    },
  { key: 'alto',     label: RISK_LABELS.alto     },
  { key: 'muy_alto', label: RISK_LABELS.muy_alto },
];

export default function StackedBarPoblacion({ data }) {
  if (!data?.length) {
    return <ChartCard title="Distribucion Poblacional"><EmptyChart /></ChartCard>;
  }

  return (
    <ChartCard title="Distribucion Poblacional de Riesgo" subtitle="Aplicaciones por nivel y guia">
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 8 }} barSize={52}>
          <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="guia"
            tick={{ fill: '#6E8BAA', fontSize: 12 }}
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
          {CATS.map(c => (
            <Bar
              key={c.key}
              dataKey={c.key}
              name={c.label}
              stackId="s"
              fill={RISK_COLORS[c.key]}
              radius={c.key === 'muy_alto' ? [6, 6, 0, 0] : [0, 0, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 10 }}>
        {CATS.map(c => (
          <div key={c.key} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{
              width: 10, height: 10, borderRadius: 3,
              background: RISK_COLORS[c.key], flexShrink: 0,
            }} />
            <span style={{ fontSize: 11, color: '#6E8BAA' }}>{c.label}</span>
          </div>
        ))}
      </div>
    </ChartCard>
  );
}
