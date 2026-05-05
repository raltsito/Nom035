import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';
import ChartCard, { RISK_COLORS, RISK_LABELS, ChartTooltip, EmptyChart } from '../ChartCard';

const CATS = [
  { key: 'nulo',     name: RISK_LABELS.nulo     },
  { key: 'bajo',     name: RISK_LABELS.bajo     },
  { key: 'medio',    name: RISK_LABELS.medio    },
  { key: 'alto',     name: RISK_LABELS.alto     },
  { key: 'muy_alto', name: RISK_LABELS.muy_alto },
];

export default function BarDepartamentos({ data }) {
  if (!data?.length) return <ChartCard title="Areas Criticas"><EmptyChart /></ChartCard>;

  return (
    <ChartCard title="Departamentos vs Nivel de Riesgo" subtitle="Distribucion por area">
      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          layout="vertical"
          data={data}
          margin={{ top: 4, right: 8, left: 8, bottom: 4 }}
          barSize={10}
          barCategoryGap="32%"
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
          {CATS.map(c => (
            <Bar
              key={c.key}
              dataKey={c.key}
              name={c.name}
              fill={RISK_COLORS[c.key]}
              radius={[0, 4, 4, 0]}
              stackId="a"
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
