import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, FileSpreadsheet, HeartPulse, Loader2 } from 'lucide-react';
import { documentosService, resultadosService } from '../../services/resultados';
// Comparte el lenguaje visual de la matriz de Guía III (columna fija, celdas
// codificadas por color, leyenda) para que ambas tablas se lean igual.
import styles from './MatrizResultados.module.css';

const PREVIEW = 10;

// Estado del criterio por sección. NO son niveles de riesgo de la NOM-035:
// la Guía I no produce niveles, solo un dictamen binario.
const ESTADO = {
  alto:  { label: 'Cumple criterio',  color: 'var(--nom-riesgo-alto)',  bg: 'rgba(239,68,68,0.16)'  },
  medio: { label: 'Con acontecimiento', color: 'var(--nom-riesgo-medio)', bg: 'rgba(245,158,11,0.16)' },
  bajo:  { label: 'Por debajo',       color: 'var(--nom-riesgo-bajo)',  bg: 'rgba(132,204,22,0.16)' },
  nulo:  { label: 'Sin afirmativas',  color: 'var(--nom-riesgo-nulo)',  bg: 'rgba(16,185,129,0.14)' },
};

const DICTAMEN = {
  requiere_atencion: { label: 'Requiere atención', color: 'var(--nom-riesgo-alto)', bg: 'rgba(239,68,68,0.16)' },
  sin_indicadores:   { label: 'Sin indicadores',   color: 'var(--nom-riesgo-nulo)', bg: 'rgba(16,185,129,0.14)' },
  sin_calificar:     { label: 'Sin calificar',     color: 'var(--nom-text-muted)',  bg: 'var(--nom-border-solid)' },
};

function CeldaSeccion({ celda, seccion }) {
  if (celda?.positivos == null) {
    return (
      <td className={`${styles.celda} ${styles.celdaNA}`} title={`${seccion.nombre} — sin dato`}>
        Sin dato
      </td>
    );
  }
  const cfg = ESTADO[celda.categoria] || ESTADO.nulo;
  return (
    <td
      className={styles.celda}
      style={{ background: cfg.bg, color: cfg.color }}
      title={`Sección ${seccion.romano} — ${seccion.nombre}: ${celda.positivos} de ${celda.total} `
           + `respuestas "Sí" (criterio ≥${celda.criterio}) — ${cfg.label}`}
    >
      <span className={styles.celdaNivel}>
        {celda.positivos} de {celda.total}{celda.cumple ? ' ✔' : ''}
      </span>
      <span className={styles.celdaPuntaje}>≥{celda.criterio}</span>
    </td>
  );
}

export default function MatrizGuiaI({ cicloId, onSelect }) {
  const [filas, setFilas]     = useState([]);
  const [meta, setMeta]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [descargando, setDescargando] = useState(false);

  const cargar = useCallback(async () => {
    if (!cicloId) return;
    setLoading(true);
    setError('');
    try {
      const res = await resultadosService.matrizGuiaI({ ciclo_id: cicloId, limite: PREVIEW });
      setFilas(res.data.data || []);
      setMeta(res.data.meta || null);
    } catch (err) {
      console.error('Error al cargar la matriz de Guía I:', err);
      setError('No se pudo cargar la matriz de Guía I.');
    } finally {
      setLoading(false);
    }
  }, [cicloId]);

  useEffect(() => { cargar(); }, [cargar]);

  const handleDescargar = async () => {
    if (!cicloId || descargando) return;
    setDescargando(true);
    try {
      const res = await documentosService.exportarMatrizGuiaI(cicloId);
      const cd  = res.headers?.['content-disposition'] || '';
      const nombreServidor = cd.match(/filename="?([^";]+)"?/)?.[1];
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = nombreServidor || `matriz_guia_i_nom035_ciclo_${cicloId}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      if (err?.response?.data instanceof Blob) {
        err.response.data.text().then(t => console.error('Error al exportar Guía I:', t.slice(0, 1000)));
      }
      alert('No se pudo descargar la matriz de Guía I.');
    } finally {
      setDescargando(false);
    }
  };

  const secciones = meta?.secciones || [];
  const total     = meta?.total ?? 0;

  // Sin Guía I aplicada en el ciclo no se muestra la tarjeta: no todos los
  // centros de trabajo la aplican.
  if (loading) return null;
  if (!error && total === 0) return null;

  return (
    <section className={`${styles.card} nom-card`}>
      <header className={styles.header}>
        <div className={styles.headerText}>
          <h3 className={styles.title}>
            <HeartPulse size={16} strokeWidth={2} />
            Guía I — Acontecimientos traumáticos severos
          </h3>
          <p className={styles.subtitle}>
            Respuestas "Sí" por sección frente a su criterio (GR.I inciso b) y dictamen final.
            {total > 0 && (
              <> Vista previa de los {Math.min(PREVIEW, total)} casos con mayor necesidad de
                 atención de {total}; descarga el Excel para ver a todos.</>
            )}
          </p>
        </div>
        <button
          className="nom-btn nom-btn-ghost"
          onClick={handleDescargar}
          disabled={!cicloId || total === 0 || descargando}
          title="Descargar la matriz de Guía I de TODOS los trabajadores (Excel)"
        >
          {descargando
            ? <Loader2 size={15} className="nom-spin" />
            : <FileSpreadsheet size={15} strokeWidth={2} />}
          Descargar Excel
        </button>
      </header>

      {error ? (
        <div className={styles.stateWrap}>
          <AlertTriangle size={20} />
          <p>{error}</p>
        </div>
      ) : (
        <>
          <div className={styles.tableWrap}>
            <table className={`${styles.table} ${styles.tableAncha}`}>
              <thead>
                <tr className={styles.grupoRow}>
                  <th className={`${styles.thTrab} ${styles.thGrupo}`} />
                  <th className={styles.thGrupo} colSpan={secciones.length}>
                    Secciones (Sí alcanzados / criterio)
                  </th>
                  <th className={styles.thGrupo}>Dictamen</th>
                </tr>
                <tr>
                  <th className={styles.thTrab}>Trabajador</th>
                  {secciones.map(s => (
                    <th key={s.clave} className={styles.thNivel} title={s.nombre}>
                      {s.romano}. {s.nombre}
                    </th>
                  ))}
                  <th className={`${styles.thNivel} ${styles.thFinal}`}>Resultado</th>
                </tr>
              </thead>
              <tbody>
                {filas.map(f => {
                  const cfg = DICTAMEN[f.final.categoria] || DICTAMEN.sin_calificar;
                  return (
                    <tr
                      key={f.resultado_id}
                      className={onSelect ? styles.trClickable : undefined}
                      onClick={onSelect ? () => onSelect(f.resultado_id) : undefined}
                    >
                      <th className={styles.tdTrab} scope="row">
                        <span className={styles.trabNombre}>{f.trabajador_nombre}</span>
                        <span className={styles.trabArea}>{f.trabajador_area}</span>
                      </th>
                      {f.secciones.map((celda, i) => (
                        <CeldaSeccion
                          key={secciones[i]?.clave || i}
                          celda={celda}
                          seccion={secciones[i] || {}}
                        />
                      ))}
                      <td
                        className={styles.celda}
                        style={{ background: cfg.bg, color: cfg.color }}
                        title={`Dictamen: ${cfg.label}`}
                      >
                        <span className={styles.celdaNivel}>{cfg.label}</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className={styles.leyenda}>
            {[ESTADO.alto, ESTADO.medio, ESTADO.bajo, ESTADO.nulo].map(cfg => (
              <span key={cfg.label} className={styles.leyendaItem}>
                <span className={styles.leyendaDot} style={{ background: cfg.color }} />
                {cfg.label}
              </span>
            ))}
          </div>
          <p className={styles.notaMetodologica}>
            Criterios GR.I inciso b: Sección I ≥1 acontecimiento y al menos uno de
            Sección II ≥1, III ≥3 o IV ≥2. Los colores indican el estado del criterio,
            no un nivel de riesgo: la Guía I no produce niveles.
          </p>
        </>
      )}
    </section>
  );
}
