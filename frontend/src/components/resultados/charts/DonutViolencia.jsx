import { PieChart, Pie, Cell, Tooltip } from 'recharts';
import ChartCard, { RISK_COLORS, RiskChip, ChartTooltip, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

export default function DonutViolencia({ data }) {
  if (!data) return <ChartCard title="Violencia Laboral"><EmptyChart /></ChartCard>;

  const { data: pieData, categoria, pct } = data;
  const fillColor = RISK_COLORS[categoria] || RISK_COLORS.bajo;

  return (
    <ChartCard title="Violencia Laboral" subtitle="Tolerancia cero — Dominios D4 / D5">
      <div className={styles.violenciaWrap}>
        <div className={styles.violenciaAlert}>
          <span className={styles.violenciaAlertLine} style={{ background: fillColor }} />
          <span className={styles.violenciaAlertText}>
            Indice de relaciones laborales y liderazgo
          </span>
        </div>
        <div className={styles.donutWrap}>
          <PieChart width={180} height={180}>
            <Pie
              data={pieData}
              cx={90}
              cy={90}
              innerRadius={54}
              outerRadius={78}
              dataKey="value"
              startAngle={90}
              endAngle={-270}
              paddingAngle={pieData[1]?.value > 0 ? 3 : 0}
            >
              <Cell fill={fillColor} stroke="none" />
              <Cell fill="#1E304F" stroke="none" />
            </Pie>
            <Tooltip content={<ChartTooltip formatter={v => `${v}%`} />} />
          </PieChart>
          <div className={styles.donutCenter}>
            <span className={styles.donutPct} style={{ color: fillColor }}>{pct}%</span>
            <RiskChip cat={categoria} />
          </div>
        </div>
      </div>
    </ChartCard>
  );
}
