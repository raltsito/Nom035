import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, AlertTriangle, ChevronDown, ChevronUp, UserX } from 'lucide-react';
import ChartCard from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

function CheckmarkSVG() {
  return (
    <svg width={40} height={40} viewBox="0 0 40 40" fill="none">
      <circle cx={20} cy={20} r={19} stroke="#10B981" strokeWidth={2} strokeOpacity={0.3} />
      <motion.path
        d="M 10 20 L 17 27 L 30 13"
        stroke="#10B981"
        strokeWidth={2.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.6, delay: 0.2, ease: 'easeOut' }}
      />
    </svg>
  );
}

function PulseDot() {
  return (
    <span className={styles.atsPulseDot}>
      <span className={styles.atsPulseRing} />
    </span>
  );
}

function CasoRow({ caso, index }) {
  const [open, setOpen] = useState(false);
  const d1  = caso.dominios?.find(d => d.seccion === 'D1');
  const sym = caso.dominios?.filter(d => d.seccion !== 'D1' && d.positivos > 0) ?? [];

  return (
    <motion.div
      className={styles.atsCasoWrap}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
    >
      <button className={styles.atsCasoRow} onClick={() => setOpen(o => !o)}>
        <PulseDot />
        <div className={styles.atsCasoInfo}>
          <span className={styles.atsCasoNombre}>{caso.trabajador_nombre}</span>
          <span className={styles.atsCasoArea}>{caso.trabajador_area}</span>
        </div>
        <div className={styles.atsCasoMeta}>
          {d1?.positivos > 0 && (
            <span className={styles.atsCasoTag}>
              {d1.positivos} acontecimiento{d1.positivos > 1 ? 's' : ''}
            </span>
          )}
          <span className={styles.atsCasoTag} style={{ background: 'rgba(239,68,68,0.12)', color: '#EF4444' }}>
            {sym.reduce((s, d) => s + d.positivos, 0)} síntomas
          </span>
        </div>
        {open ? <ChevronUp size={14} className={styles.atsCasoArrow} /> : <ChevronDown size={14} className={styles.atsCasoArrow} />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            className={styles.atsCasoDetail}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            {caso.dominios?.map(d => d.positivos > 0 && (
              <div key={d.seccion} className={styles.atsCasoDetailRow}>
                <span className={styles.atsCasoDetailKey}>{d.seccion}</span>
                <span className={styles.atsCasoDetailNombre}>{d.nombre}</span>
                <span className={styles.atsCasoDetailN}>{d.positivos}/{d.total}</span>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function TablaAtencionClinica({ data }) {
  const casos = data ?? [];

  return (
    <ChartCard
      title="Guía I — Atención Clínica Requerida"
      subtitle="Trabajadores con acontecimiento traumático severo y síntomas positivos"
    >
      {casos.length === 0 ? (
        <motion.div
          className={styles.atsEmpty}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <CheckmarkSVG />
          <div>
            <p className={styles.atsEmptyTitle}>Sin casos detectados</p>
            <p className={styles.atsEmptySub}>
              Ningún trabajador cumple el criterio de atención clínica en este ciclo.
            </p>
          </div>
        </motion.div>
      ) : (
        <div className={styles.atsList}>
          <div className={styles.atsAlertBanner}>
            <AlertTriangle size={15} />
            <span>
              <strong>{casos.length}</strong> trabajador{casos.length > 1 ? 'es requieren' : ' requiere'} evaluación clínica
              individual por psicólogo o psiquiatra — Numeral 7.1 NOM-035-STPS-2018.
            </span>
          </div>
          {casos.map((c, i) => (
            <CasoRow key={c.resultado_id} caso={c} index={i} />
          ))}
        </div>
      )}
    </ChartCard>
  );
}
