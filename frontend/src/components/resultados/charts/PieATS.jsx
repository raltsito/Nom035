import { PieChart, Pie, Cell, Tooltip } from 'recharts';
import ChartCard, { ChartTooltip, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

const COLORS = ['#EF4444', '#1E304F'];

export default function PieATS({ data }) {
  if (!data?.length) return <ChartCard title="ATS"><EmptyChart /></ChartCard>;

  const total = data.reduce((s, d) => s + d.value, 0);
  const affected = data[0]?.value || 0;
  const pct = total > 0 ? Math.round((affected / total) * 100) : 0;

  return (
    <ChartCard title="Eventos Traumaticos Severos" subtitle="ATS — Valoracion clinica requerida">
      <div className={styles.donutWrap}>
        <PieChart width={160} height={160}>
          <Pie
            data={data}
            cx={80}
            cy={80}
            innerRadius={46}
            outerRadius={68}
            dataKey="value"
            startAngle={90}
            endAngle={-270}
            paddingAngle={data[1]?.value > 0 ? 4 : 0}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i]} stroke="none" />
            ))}
          </Pie>
          <Tooltip content={<ChartTooltip />} />
        </PieChart>
        <div className={styles.donutCenter}>
          <span className={styles.donutPct} style={{ color: '#EF4444', fontSize: '1.4rem' }}>
            {affected}
          </span>
          <span className={styles.donutSub}>{pct}% del total</span>
        </div>
      </div>
      <p className={styles.atsNote}>
        Trabajadores con riesgo muy alto requieren valoracion por clinico.
      </p>
    </ChartCard>
  );
}
