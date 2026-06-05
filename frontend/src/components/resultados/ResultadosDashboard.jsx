import { useDashboardData } from './useDashboardData';
import styles from './ResultadosDashboard.module.css';

import GaugeRiesgo          from './charts/GaugeRiesgo';
import CardTop3Dominios     from './charts/CardTop3Dominios';
import RadarCategorias      from './charts/RadarCategorias';
import BarDominios          from './charts/BarDominios';
import HeatmapDominiosAreas from './charts/HeatmapDominiosAreas';
import BarDepartamentos     from './charts/BarDepartamentos';
import StackedBarPoblacion  from './charts/StackedBarPoblacion';
import TablaAtencionClinica from './charts/TablaAtencionClinica';

function Skeleton() {
  const cells = [
    ['span 4', 200], ['span 4', 200], ['span 4', 200],
    ['span 12', 380],
    ['span 7', 300], ['span 5', 300],
    ['span 12', 240],
    ['span 12', 200],
  ];
  return (
    <div className={styles.skeleton}>
      {cells.map(([col, h], i) => (
        <div key={i} className={styles.skeletonCell} style={{ gridColumn: col, height: h }} />
      ))}
    </div>
  );
}

export default function ResultadosDashboard({ cicloId }) {
  const { loading, data, error } = useDashboardData(cicloId);

  if (!cicloId) return null;
  if (loading)  return <Skeleton />;
  if (error)    return (
    <div style={{ padding: 20, color: 'var(--nom-text-muted)', fontSize: 13 }}>
      No se pudo cargar el dashboard: {error.message || 'Error de red'}
    </div>
  );
  if (!data)    return null;

  return (
    <div className={styles.bento}>
      {/* ── Fila 1: KPI global | Top3 dominios | Radar ── */}
      <div className={styles.cellGauge}>
        <GaugeRiesgo data={data.riesgoGlobal} />
      </div>
      <div className={styles.cellTop3}>
        <CardTop3Dominios data={data.top3} />
      </div>
      <div className={styles.cellRadar}>
        <RadarCategorias data={data.radar} />
      </div>

      {/* ── Fila 2: 14 dominios full-width ── */}
      <div className={styles.cellDominios}>
        <BarDominios data={data.dominios} />
      </div>

      {/* ── Fila 3: Heatmap | Departamentos ── */}
      <div className={styles.cellHeatmap}>
        <HeatmapDominiosAreas data={data.dominios} />
      </div>
      <div className={styles.cellAreas}>
        <BarDepartamentos data={data.areas} />
      </div>

      {/* ── Fila 4: Distribución demográfica full-width ── */}
      <div className={styles.cellStacked}>
        <StackedBarPoblacion data={data.distData} />
      </div>

      {/* ── Fila 5: Tabla de atención clínica full-width ── */}
      <div className={styles.cellAts}>
        <TablaAtencionClinica data={data.atencionClinica} />
      </div>
    </div>
  );
}
