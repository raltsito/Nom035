import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip,
} from 'recharts';
import ChartCard, { ACCENT, ChartTooltip, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

function AxisTick({ payload, x, y, textAnchor }) {
  const lines = payload.value.split('\n');
  return (
    <text
      x={x}
      y={y}
      textAnchor={textAnchor}
      fill="#6E8BAA"
      fontSize={11}
      fontFamily="Inter, system-ui, sans-serif"
    >
      {lines.map((l, i) => (
        <tspan key={i} x={x} dy={i === 0 ? 0 : 14}>{l}</tspan>
      ))}
    </text>
  );
}

export default function RadarCategorias({ data }) {
  if (!data?.length) return <ChartCard title="Analisis Normativo"><EmptyChart /></ChartCard>;

  return (
    <ChartCard title="Perfil de Riesgo por Dimension" subtitle="5 macro-dimensiones NOM-035-STPS-2018">
      <ResponsiveContainer width="100%" height={260}>
        <RadarChart data={data} margin={{ top: 16, right: 40, bottom: 16, left: 40 }}>
          <PolarGrid stroke="rgba(255,255,255,0.07)" />
          <PolarAngleAxis dataKey="subject" tick={<AxisTick />} />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={false}
            axisLine={false}
          />
          <Radar
            name="Nivel de riesgo"
            dataKey="valor"
            stroke={ACCENT}
            fill={ACCENT}
            fillOpacity={0.18}
            strokeWidth={2}
            dot={{ r: 4, fill: ACCENT, strokeWidth: 0 }}
          />
          <Tooltip
            content={<ChartTooltip formatter={v => `${v}%`} />}
          />
        </RadarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
