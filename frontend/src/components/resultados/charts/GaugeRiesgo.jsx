import { PieChart, Pie, Cell } from 'recharts';
import ChartCard, { RISK_COLORS, RISK_LABELS, RiskChip, EmptyChart } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

const SEGMENTS = [
  { value: 20, cat: 'nulo' },
  { value: 20, cat: 'bajo' },
  { value: 20, cat: 'medio' },
  { value: 20, cat: 'alto' },
  { value: 20, cat: 'muy_alto' },
];

function Needle({ cx, cy, pct, innerR }) {
  const deg = 180 - (pct / 100) * 180;
  const rad = (deg * Math.PI) / 180;
  const r = innerR * 0.78;
  const x = cx + r * Math.cos(rad);
  const y = cy - r * Math.sin(rad);
  const bx = cx + 8 * Math.cos(rad + Math.PI / 2);
  const by = cy - 8 * Math.sin(rad + Math.PI / 2);
  const bx2 = cx + 8 * Math.cos(rad - Math.PI / 2);
  const by2 = cy - 8 * Math.sin(rad - Math.PI / 2);
  return (
    <g>
      <polygon points={`${x},${y} ${bx},${by} ${bx2},${by2}`} fill="#E4EDF6" opacity={0.9} />
      <circle cx={cx} cy={cy} r={9} fill="#E4EDF6" />
      <circle cx={cx} cy={cy} r={5} fill={RISK_COLORS.medio} />
    </g>
  );
}

export default function GaugeRiesgo({ data }) {
  if (!data) return <ChartCard title="Riesgo Psicosocial Global"><EmptyChart /></ChartCard>;
  const { pct, categoria } = data;

  return (
    <ChartCard title="Riesgo Psicosocial Global" subtitle="Indice ponderado del ciclo">
      <div className={styles.gaugeWrap}>
        <PieChart width={220} height={130}>
          <Pie
            data={SEGMENTS}
            cx={110}
            cy={115}
            startAngle={180}
            endAngle={0}
            innerRadius={68}
            outerRadius={100}
            dataKey="value"
            isAnimationActive={false}
            stroke="none"
          >
            {SEGMENTS.map((seg, i) => (
              <Cell key={i} fill={RISK_COLORS[seg.cat]} opacity={0.88} />
            ))}
          </Pie>
          <Needle cx={110} cy={115} pct={pct} innerR={68} />
        </PieChart>
        <div className={styles.gaugeLabel}>
          <span className={styles.gaugePct}>{pct}%</span>
          <RiskChip cat={categoria} />
        </div>
      </div>
    </ChartCard>
  );
}
