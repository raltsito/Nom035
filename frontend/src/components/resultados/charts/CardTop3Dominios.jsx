import { motion } from 'framer-motion';
import ChartCard, { RISK_COLORS, RISK_LABELS } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

const MEDAL = ['🥇', '🥈', '🥉'];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
};
const card = {
  hidden: { opacity: 0, y: 16 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
};

function TopCard({ dominio, rank }) {
  const color = RISK_COLORS[dominio.categoria_modal] ?? RISK_COLORS.bajo;
  const label = RISK_LABELS[dominio.categoria_modal] ?? dominio.categoria_modal;
  const pct   = dominio.pct_promedio ?? 0;
  const isHigh = dominio.categoria_modal === 'alto' || dominio.categoria_modal === 'muy_alto';

  return (
    <motion.div
      variants={card}
      className={styles.top3Card}
      style={{
        borderColor:     `${color}40`,
        boxShadow:       isHigh ? `0 0 18px 0 ${color}30` : undefined,
      }}
    >
      <div className={styles.top3Header}>
        <span className={styles.top3Rank}>{MEDAL[rank]}</span>
        <span className={styles.top3Clave}>{dominio.dominio_clave}</span>
        <span
          className={styles.top3Chip}
          style={{ color, background: `${color}18` }}
        >
          {label}
        </span>
      </div>

      <p className={styles.top3Nombre}>{dominio.dominio_nombre}</p>

      <div className={styles.top3BarWrap}>
        <div className={styles.top3BarTrack}>
          <motion.div
            className={styles.top3BarFill}
            style={{ background: `linear-gradient(90deg, ${color}99, ${color})` }}
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ delay: 0.2 + rank * 0.12, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          />
        </div>
        <span className={styles.top3Pct} style={{ color }}>{pct}%</span>
      </div>
    </motion.div>
  );
}

export default function CardTop3Dominios({ data }) {
  const list = data?.slice(0, 3) ?? [];

  return (
    <ChartCard
      title="Dominios Críticos"
      subtitle="3 dominios con mayor nivel de riesgo"
    >
      {!list.length ? (
        <div className={styles.top3Empty}>Sin dominios calculados</div>
      ) : (
        <motion.div
          className={styles.top3Grid}
          variants={container}
          initial="hidden"
          animate="show"
        >
          {list.map((d, i) => (
            <TopCard key={d.dominio_clave} dominio={d} rank={i} />
          ))}
        </motion.div>
      )}
    </ChartCard>
  );
}
