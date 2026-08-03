import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, FileSpreadsheet, Grid3x3, Loader2 } from 'lucide-react';
import { documentosService, resultadosService } from '../../services/resultados';
import styles from './MatrizResultados.module.css';

// Cuántos trabajadores muestra la vista previa: solo los de mayor riesgo.
// El Excel siempre trae a todos (lo resuelve el backend).
const PREVIEW = 10;

// Codificación visual de la NOM-035 (la del informe DOCX y del Excel) aplicada
// con el mismo tratamiento suave que la matriz de Guía I: fondo tenue y texto
// del mismo matiz. Las variables derivadas viven en styles/variables.css.
const NIVELES = {
  nulo:          { label: 'Nulo',          color: 'var(--nom-norma-nulo-fg)',     bg: 'var(--nom-norma-nulo-bg)'     },
  bajo:          { label: 'Bajo',          color: 'var(--nom-norma-bajo-fg)',     bg: 'var(--nom-norma-bajo-bg)'     },
  medio:         { label: 'Medio',         color: 'var(--nom-norma-medio-fg)',    bg: 'var(--nom-norma-medio-bg)'    },
  alto:          { label: 'Alto',          color: 'var(--nom-norma-alto-fg)',     bg: 'var(--nom-norma-alto-bg)'     },
  muy_alto:      { label: 'Muy alto',      color: 'var(--nom-norma-muy-alto-fg)', bg: 'var(--nom-norma-muy-alto-bg)' },
  // Sin calificar no es un nivel de la norma: gris neutro, fuera de la escala.
  sin_calificar: { label: 'Sin calificar', color: 'var(--nom-text-muted)',        bg: 'var(--nom-border-solid)'      },
};

// Encabezados cortos: los nombres oficiales no caben en 16 columnas.
// El nombre completo queda en el `title` de cada celda de encabezado.
const CORTO_DOMINIO = {
  D1: 'Ambiente',       D2: 'Carga trabajo',  D3: 'Falta control',
  D4: 'Jornada',        D5: 'Trabajo-familia', D6: 'Liderazgo',
  D7: 'Relaciones',     D8: 'Violencia',      D9: 'Reconocimiento',
  D10: 'Pertenencia',
};
const CORTO_CATEGORIA = {
  1: 'Ambiente',            2: 'Actividad',   3: 'Tiempo trabajo',
  4: 'Liderazgo y relac.',  5: 'Entorno org.',
};

function Celda({ celda, titulo }) {
  const nivel = celda?.categoria;
  const cfg   = NIVELES[nivel];
  if (!cfg || celda.puntaje_max === 0 || celda.puntaje_max === null) {
    return (
      <td className={`${styles.celda} ${styles.celdaNA}`} title={`${titulo} — sin ítems aplicables`}>
        N/A
      </td>
    );
  }
  return (
    <td
      className={styles.celda}
      style={{ background: cfg.bg, color: cfg.color }}
      title={`${titulo}: ${cfg.label} (${celda.puntaje}/${celda.puntaje_max})`}
    >
      <span className={styles.celdaNivel}>{cfg.label}</span>
      <span className={styles.celdaPuntaje}>{celda.puntaje}</span>
    </td>
  );
}

export default function MatrizResultados({ cicloId, onSelect }) {
  const [filas, setFilas]       = useState([]);
  const [meta, setMeta]         = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [descargando, setDescargando] = useState(false);

  const cargar = useCallback(async () => {
    if (!cicloId) return;
    setLoading(true);
    setError('');
    try {
      const res = await resultadosService.matriz({ ciclo_id: cicloId, limite: PREVIEW });
      setFilas(res.data.data || []);
      setMeta(res.data.meta || null);
    } catch (err) {
      console.error('Error al cargar la matriz de resultados:', err);
      setError('No se pudo cargar la matriz de resultados.');
    } finally {
      setLoading(false);
    }
  }, [cicloId]);

  useEffect(() => { cargar(); }, [cargar]);

  const handleDescargar = async () => {
    if (!cicloId || descargando) return;
    setDescargando(true);
    try {
      const res = await documentosService.exportarMatriz(cicloId);
      const cd  = res.headers?.['content-disposition'] || '';
      const nombreServidor = cd.match(/filename="?([^";]+)"?/)?.[1];
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = nombreServidor || `matriz_resultados_nom035_ciclo_${cicloId}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      if (err?.response?.data instanceof Blob) {
        err.response.data.text().then(t => console.error('Error al exportar la matriz:', t.slice(0, 1000)));
      }
      alert('No se pudo descargar la matriz de resultados.');
    } finally {
      setDescargando(false);
    }
  };

  const dominios   = meta?.dominios   || [];
  const categorias = meta?.categorias || [];
  const total      = meta?.total ?? 0;

  return (
    <section className={`${styles.card} nom-card`}>
      <header className={styles.header}>
        <div className={styles.headerText}>
          <h3 className={styles.title}>
            <Grid3x3 size={16} strokeWidth={2} />
            Matriz de resultados por trabajador
          </h3>
          <p className={styles.subtitle}>
            Nivel de riesgo por dominio, categoría y resultado final (Guía III).
            {total > 0 && (
              <> Vista previa de los {Math.min(PREVIEW, total)} casos más riesgosos de {total};
                 descarga el Excel para ver a todos.</>
            )}
          </p>
        </div>
        <button
          className="nom-btn nom-btn-ghost"
          onClick={handleDescargar}
          disabled={!cicloId || total === 0 || descargando}
          title="Descargar la matriz completa de TODOS los trabajadores (Excel)"
        >
          {descargando
            ? <Loader2 size={15} className="nom-spin" />
            : <FileSpreadsheet size={15} strokeWidth={2} />}
          Descargar Excel
        </button>
      </header>

      {loading ? (
        <div className={styles.stateWrap}><Loader2 size={22} className="nom-spin" /></div>
      ) : error ? (
        <div className={styles.stateWrap}>
          <AlertTriangle size={20} />
          <p>{error}</p>
        </div>
      ) : filas.length === 0 ? (
        <div className={styles.stateWrap}>
          <Grid3x3 size={30} strokeWidth={1.25} />
          <p>No hay diagnósticos calculados de la Guía III en este ciclo.</p>
        </div>
      ) : (
        <>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr className={styles.grupoRow}>
                  <th className={`${styles.thTrab} ${styles.thGrupo}`} />
                  <th className={styles.thGrupo} colSpan={dominios.length}>Dominios</th>
                  <th className={styles.thGrupo} colSpan={categorias.length}>Categorías</th>
                  <th className={styles.thGrupo}>Final</th>
                </tr>
                <tr>
                  <th className={styles.thTrab}>Trabajador</th>
                  {dominios.map(d => (
                    <th key={d.clave} className={styles.thNivel} title={d.nombre}>
                      {CORTO_DOMINIO[d.clave] || d.nombre}
                    </th>
                  ))}
                  {categorias.map(c => (
                    <th key={c.orden} className={styles.thNivel} title={c.nombre}>
                      {CORTO_CATEGORIA[c.orden] || c.nombre}
                    </th>
                  ))}
                  <th className={`${styles.thNivel} ${styles.thFinal}`}>Final</th>
                </tr>
              </thead>
              <tbody>
                {filas.map(f => (
                  <tr
                    key={f.resultado_id}
                    className={onSelect ? styles.trClickable : undefined}
                    onClick={onSelect ? () => onSelect(f.resultado_id) : undefined}
                  >
                    <th className={styles.tdTrab} scope="row">
                      <span className={styles.trabNombre}>{f.trabajador_nombre}</span>
                      <span className={styles.trabArea}>{f.trabajador_area}</span>
                    </th>
                    {f.dominios.map((celda, i) => (
                      <Celda
                        key={dominios[i]?.clave || i}
                        celda={celda}
                        titulo={dominios[i]?.nombre || 'Dominio'}
                      />
                    ))}
                    {f.categorias.map((celda, i) => (
                      <Celda
                        key={categorias[i]?.orden || i}
                        celda={celda}
                        titulo={categorias[i]?.nombre || 'Categoría'}
                      />
                    ))}
                    <Celda celda={f.final} titulo="Resultado final" />
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className={styles.leyenda}>
            {Object.entries(NIVELES).map(([key, cfg]) => (
              <span key={key} className={styles.leyendaItem}>
                <span className={styles.leyendaDot} style={{ background: cfg.color }} />
                {cfg.label}
              </span>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
