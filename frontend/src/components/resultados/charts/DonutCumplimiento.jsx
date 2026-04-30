import { PieChart, Pie, Cell, Tooltip } from 'recharts';
import ChartCard, { ACCENT, MUTED, ChartTooltip, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

const COLORS = [ACCENT, '#1E304F'];

export default function DonutCumplimiento({ data, resumen }) {
  if (!data || !resumen) return <ChartCard title="Tasa de Cumplimiento"><EmptyChart /></ChartCard>;

  const total = resumen.total_aplicaciones || 0;
  const comp  = resumen.total_completadas || 0;
  const pct   = total > 0 ? Math.round((comp / total) * 100) : 0;

  return (
    <ChartCard title="Tasa de Cumplimiento" subtitle="Cuestionarios respondidos">
      <div className={styles.donutWrap}>
        <PieChart width={180} height={180}>
          <Pie
            data={data}
            cx={90}
            cy={90}
            innerRadius={54}
            outerRadius={78}
            dataKey="value"
            startAngle={90}
            endAngle={-270}
            paddingAngle={data[1].value > 0 ? 3 : 0}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i]} stroke="none" />
            ))}
          </Pie>
          <Tooltip content={<ChartTooltip />} />
        </PieChart>
        <div className={styles.donutCenter}>
          <span className={styles.donutPct}>{pct}%</span>
          <span className={styles.donutSub}>{comp} / {total}</span>
        </div>
      </div>
    </ChartCard>
  );
}
