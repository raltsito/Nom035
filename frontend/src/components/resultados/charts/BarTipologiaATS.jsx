import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';
import ChartCard, { ChartTooltip, EmptyChart } from '../ChartCard';

const PALETTE = ['#EF4444', '#F97316', '#FBBF24', '#A78BFA', '#60A5FA'];

export default function BarTipologiaATS({ data }) {
  if (!data?.length || (data.length === 1 && data[0].n === 0)) {
    return <ChartCard title="Tipologia ATS"><EmptyChart /></ChartCard>;
  }

  return (
    <ChartCard title="Tipologia de Eventos" subtitle="Categoria del acontecimiento traumatico severo">
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 40 }} barSize={28}>
          <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="tipo"
            tick={{ fill: '#6E8BAA', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            angle={-32}
            textAnchor="end"
            interval={0}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fill: '#6E8BAA', fontSize: 10 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<ChartTooltip />} />
          <Bar dataKey="n" name="Trabajadores" radius={[6, 6, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
