import { useDashboardData } from './useDashboardData';
import styles from './ResultadosDashboard.module.css';

import GaugeRiesgo         from './charts/GaugeRiesgo';
import DonutCumplimiento   from './charts/DonutCumplimiento';
import DonutViolencia      from './charts/DonutViolencia';
import RadarCategorias     from './charts/RadarCategorias';
import BarDominios         from './charts/BarDominios';
import StackedBarPoblacion from './charts/StackedBarPoblacion';
import BarDepartamentos    from './charts/BarDepartamentos';
import PieATS              from './charts/PieATS';
import BarTipologiaATS     from './charts/BarTipologiaATS';
import LineHistorica       from './charts/LineHistorica';

function Skeleton() {
  const cells = [
    ['span 4', 180], ['span 4', 180], ['span 4', 180],
    ['span 5', 300], ['span 7', 300],
    ['span 6', 260], ['span 6', 260],
    ['span 3', 280], ['span 4', 280], ['span 5', 280],
  ];
  return (
    <div className={styles.skeleton}>
      {cells.map(([col, h], i) => (
        <div
          key={i}
          className={styles.skeletonCell}
          style={{ gridColumn: col, height: h }}
        />
      ))}
    </div>
  );
}

export default function ResultadosDashboard({ cicloId }) {
  const { loading, data } = useDashboardData(cicloId);

  if (!cicloId) return null;
  if (loading) return <Skeleton />;
  if (!data) return null;

  return (
    <div className={styles.bento}>
      {/* ---- Fila 1: KPIs ---- */}
      <div className={styles.cellGauge}>
        <GaugeRiesgo data={data.riesgoGlobal} />
      </div>
      <div className={styles.cellCumplimiento}>
        <DonutCumplimiento data={data.cumplimiento} resumen={data.resumen} />
      </div>
      <div className={styles.cellViolencia}>
        <DonutViolencia data={data.violencia} />
      </div>

      {/* ---- Fila 2: Analisis normativo ---- */}
      <div className={styles.cellRadar}>
        <RadarCategorias data={data.radar} />
      </div>
      <div className={styles.cellDominios}>
        <BarDominios data={data.dominios} />
      </div>

      {/* ---- Fila 3: Demografico ---- */}
      <div className={styles.cellStacked}>
        <StackedBarPoblacion data={data.distData} />
      </div>
      <div className={styles.cellAreas}>
        <BarDepartamentos data={data.areas} />
      </div>

      {/* ---- Fila 4: ATS + Historica ---- */}
      <div className={styles.cellPieATS}>
        <PieATS data={data.ats?.data} />
      </div>
      <div className={styles.cellTipologia}>
        <BarTipologiaATS data={data.ats?.types} />
      </div>
      <div className={styles.cellHistorica}>
        <LineHistorica data={data.historica} />
      </div>
    </div>
  );
}
