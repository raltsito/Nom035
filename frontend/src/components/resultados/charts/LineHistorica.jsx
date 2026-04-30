import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import ChartCard, { ACCENT, ChartTooltip, EmptyChart } from '../ChartCard';

export default function LineHistorica({ data }) {
  if (!data?.length) return <ChartCard title="Comparativa Historica"><EmptyChart /></ChartCard>;

  return (
    <ChartCard title="Comparativa Historica" subtitle="Ciclo actual vs. ciclo anterior por dominio">
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 16, left: -16, bottom: 8 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="dominio"
            tick={{ fill: '#6E8BAA', fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: '#6E8BAA', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={v => `${v}%`}
          />
          <Tooltip content={<ChartTooltip formatter={v => `${v}%`} />} />
          <Legend
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: 11, color: '#6E8BAA' }}
          />
          <Line
            type="monotone"
            dataKey="anterior"
            name="Ciclo anterior"
            stroke="#4A6A8A"
            strokeWidth={2}
            strokeDasharray="5 3"
            dot={{ r: 4, fill: '#4A6A8A', strokeWidth: 0 }}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="actual"
            name="Ciclo actual"
            stroke={ACCENT}
            strokeWidth={2.5}
            dot={{ r: 4, fill: ACCENT, strokeWidth: 0 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
