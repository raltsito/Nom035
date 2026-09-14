import ChartCard, { RISK_COLORS, RISK_LABELS } from '../ChartCard';
import styles from '../ResultadosDashboard.module.css';

// Opción B: promedio de todos los trabajadores/dominios juntos (suma de
// puntos obtenidos / suma de puntos máximos posibles, ver backend
// meta.promedio_planta_pct en /resultados/dominios-agregados/).
// "Todos los trabajadores" = la MUESTRA (Guía III válida), no el headcount
// total de la planta — de ahí el n mostrado junto al %.
//
// Nivel INTERNO (Opción 2, confirmada por el usuario 2026-09-14): la
// NOM-035 PROHÍBE clasificar promedios con los cortes oficiales de la
// Tabla 6 (auditoría metodológica jul-2026 — la conclusión oficial es
// SIEMPRE la moda de niveles individuales, nunca el promedio). Este nivel
// usa cortes propios (bandas iguales de 20 puntos sobre 0-100%), NO son
// los cortes de la Tabla 6, y debe llevar el disclaimer visible siempre.
const CORTES_INTERNOS = [
  { max: 20,  nivel: 'nulo' },
  { max: 40,  nivel: 'bajo' },
  { max: 60,  nivel: 'medio' },
  { max: 80,  nivel: 'alto' },
  { max: 101, nivel: 'muy_alto' },
];

function nivelInterno(pct) {
  return (CORTES_INTERNOS.find(c => pct < c.max) ?? CORTES_INTERNOS.at(-1)).nivel;
}

export default function CardPromedioPlanta({ data }) {
  const pct      = data?.pct ?? null;
  const nMuestra = data?.nMuestra ?? null;
  const nivel    = pct !== null ? nivelInterno(pct) : null;
  const color    = nivel ? RISK_COLORS[nivel] : null;

  return (
    <ChartCard
      title="Calificación Final del Centro de Trabajo"
      subtitle="Indicador interno — no es la clasificación oficial NOM-035"
      className={styles.promedioPlantaHeroCard}
      style={color ? { '--hero-accent': color } : undefined}
    >
      {pct === null ? (
        <div className={styles.gaugeEmpty}>Sin datos calculados</div>
      ) : (
        <div className={styles.promedioPlantaHero}>
          <div className={styles.promedioPlantaDisclaimer}>
            ⚠️ Nivel de referencia <strong>interno</strong>, calculado con
            cortes propios (no los de la Tabla 6). La clasificación
            <strong> oficial</strong> de la NOM-035 es la moda de niveles
            individuales por dominio/área, mostrada abajo — esta tarjeta
            nunca la sustituye.
          </div>

          <div className={styles.promedioPlantaHeroMain}>
            <div className={styles.promedioPlantaLeft}>
              <span className={styles.promedioPlantaPct}>{pct}%</span>
              <span
                className={styles.promedioPlantaChipInterno}
                style={{ color, borderColor: color, background: `${color}18` }}
              >
                {RISK_LABELS[nivel]} <em>(interno)</em>
              </span>
              {nMuestra !== null && (
                <span className={styles.promedioPlantaMuestra}>
                  sobre la muestra de {nMuestra} trabajadores con Guía III
                  completada (no el total de la planta)
                </span>
              )}
            </div>

            <div className={styles.promedioPlantaRight}>
              <div className={styles.promedioPlantaBarTrack}>
                <div
                  className={styles.promedioPlantaBarFill}
                  style={{ width: `${Math.min(100, Math.max(0, pct))}%`, background: color }}
                />
              </div>
              <div className={styles.promedioPlantaBarLabels}>
                <span>0% — sin carga de riesgo</span>
                <span>100% — carga máxima posible</span>
              </div>

              <span className={styles.promedioPlantaNota}>
                De los puntos de riesgo psicosocial que podían obtenerse entre
                los trabajadores de la muestra y todos los dominios, el centro
                de trabajo acumuló en promedio este {pct}%.{' '}
                <strong>Entre más alto, mayor la carga de riesgo
                reportada</strong> — no equivale a "% de trabajadores en riesgo
                alto". Cortes internos: 0-19% Nulo, 20-39% Bajo, 40-59% Medio,
                60-79% Alto, 80-100% Muy Alto.
              </span>
            </div>
          </div>
        </div>
      )}
    </ChartCard>
  );
}
