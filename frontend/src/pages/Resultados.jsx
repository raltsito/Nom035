import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  BarChart2, RefreshCw, Loader2, ChevronDown, X,
  ChevronRight, AlertTriangle, CheckCircle2, TrendingUp, FileDown,
} from 'lucide-react';
import { resultadosService } from '../services/resultados';
import { ciclosService } from '../services/trabajadores';
import styles from './Resultados.module.css';

const CAT = {
  bajo:     { label: 'Nulo / Bajo', color: 'var(--nom-riesgo-nulo)',     bg: 'rgba(16,185,129,0.10)' },
  medio:    { label: 'Medio',       color: 'var(--nom-riesgo-medio)',    bg: 'rgba(245,158,11,0.10)' },
  alto:     { label: 'Alto',        color: 'var(--nom-riesgo-alto)',     bg: 'rgba(239,68,68,0.10)'  },
  muy_alto: { label: 'Muy alto',    color: 'var(--nom-riesgo-muy-alto)', bg: 'rgba(124,58,237,0.10)' },
};

function CatChip({ cat }) {
  const c = CAT[cat] || CAT.bajo;
  return (
    <span
      className={styles.catChip}
      style={{ background: c.bg, color: c.color }}
    >
      {c.label}
    </span>
  );
}

function RiesgoBar({ pct, cat }) {
  const c = CAT[cat] || CAT.bajo;
  return (
    <div className={styles.riesgoBar}>
      <div
        className={styles.riesgoFill}
        style={{ width: `${pct}%`, background: c.color }}
      />
    </div>
  );
}

export default function Resultados() {
  const [ciclos, setCiclos]         = useState([]);
  const [cicloId, setCicloId]       = useState('');
  const [resultados, setResultados] = useState([]);
  const [resumen, setResumen]       = useState(null);
  const [loading, setLoading]       = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [calcError, setCalcError]   = useState('');
  const [detalle, setDetalle]       = useState(null);
  const [catFilter, setCatFilter]   = useState('');

  useEffect(() => {
    ciclosService.list().then(res => {
      const data = res.data.data;
      setCiclos(data);
      if (data.length > 0) setCicloId(String(data[0].id));
    });
  }, []);

  const fetchResultados = useCallback(async () => {
    if (!cicloId) return;
    setLoading(true);
    setCalcError('');
    try {
      const params = { ciclo_id: cicloId };
      if (catFilter) params.categoria = catFilter;
      const [rRes, sumRes] = await Promise.all([
        resultadosService.list(params),
        resultadosService.resumen({ ciclo_id: cicloId }),
      ]);
      setResultados(rRes.data.data);
      setResumen(sumRes.data.data);
    } finally {
      setLoading(false);
    }
  }, [cicloId, catFilter]);

  useEffect(() => { fetchResultados(); }, [fetchResultados]);

  const handleDescargar = () => {
    if (!cicloId) return;
    const token = localStorage.getItem('access_token') || '';
    const url = `/api/v1/documentos/informe-nom035/?ciclo_id=${cicloId}`;
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => {
        const ct = r.headers.get('content-type') || '';
        const cd = r.headers.get('content-disposition') || '';
        if (ct.includes('text/html')) {
          return r.text().then(html => {
            const win = window.open('', '_blank');
            win.document.write(html);
            win.document.close();
          });
        }
        return r.blob().then(blob => {
          const burl = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = burl;
          a.download = cd.match(/filename="?([^";]+)"?/)?.[1]
            || `informe_nom035_ciclo_${cicloId}.pdf`;
          a.click();
          URL.revokeObjectURL(burl);
        });
      })
      .catch(() => alert('Error al generar el informe. Verifica que existan resultados calculados.'));
  };

  const handleCalcular = async () => {
    if (!cicloId) return;
    setCalculating(true);
    setCalcError('');
    try {
      await resultadosService.calcular({ ciclo_id: Number(cicloId) });
      await fetchResultados();
    } catch (err) {
      const e = err.response?.data?.errors;
      const msg = e && typeof e === 'object'
        ? Object.values(e).flat().join(' ')
        : 'Ocurrió un error al calcular.';
      setCalcError(msg);
    } finally {
      setCalculating(false);
    }
  };

  const openDetalle = async (r) => {
    if (r.dominios) { setDetalle(r); return; }
    try {
      const res = await resultadosService.get(r.id);
      setDetalle(res.data.data);
    } catch {}
  };

  const pendienteCalculo = resumen
    ? resumen.total_completadas - resumen.total_resultados
    : 0;

  const dist = resumen?.distribucion || {};
  const totalDist = Object.values(dist).reduce((a, b) => a + b, 0);

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Resultados y Diagnóstico</h1>
          <p className={styles.subtitle}>Análisis de factores de riesgo psicosocial por ciclo</p>
        </div>
        <div className={styles.headerActions}>
          {ciclos.length > 0 && (
            <div className={styles.selectWrap}>
              <ChevronDown size={14} className={styles.selectIcon} />
              <select
                className={styles.select}
                value={cicloId}
                onChange={e => setCicloId(e.target.value)}
              >
                {ciclos.map(c => (
                  <option key={c.id} value={c.id}>Ciclo {c.anio}</option>
                ))}
              </select>
            </div>
          )}
          <button
            className="nom-btn nom-btn-ghost"
            onClick={handleDescargar}
            disabled={!cicloId || resultados.length === 0}
            title="Descargar informe NOM-035 en PDF"
          >
            <FileDown size={15} strokeWidth={2} />
            Descargar PDF
          </button>
          <button
            className="nom-btn nom-btn-primary"
            onClick={handleCalcular}
            disabled={calculating || !cicloId}
          >
            {calculating
              ? <Loader2 size={15} className="nom-spin" />
              : <RefreshCw size={15} strokeWidth={2} />
            }
            {calculating ? 'Calculando...' : 'Calcular diagnóstico'}
          </button>
        </div>
      </div>

      {calcError && (
        <div className={styles.errorBanner}>
          <AlertTriangle size={15} />
          {calcError}
        </div>
      )}

      {pendienteCalculo > 0 && (
        <div className={styles.warnBanner}>
          <AlertTriangle size={15} />
          Hay {pendienteCalculo} aplicación(es) completada(s) sin diagnóstico calculado. Presiona "Calcular diagnóstico".
        </div>
      )}

      {/* Stats + distribución */}
      {resumen && (
        <div className={styles.statsSection}>
          <div className={styles.statsRow}>
            <div className={`${styles.statCard} nom-card`}>
              <div className={styles.statIcon}><BarChart2 size={18} strokeWidth={1.75} /></div>
              <div>
                <div className={styles.statNum}>{resumen.total_resultados}</div>
                <div className={styles.statLabel}>Con diagnóstico</div>
              </div>
            </div>
            <div className={`${styles.statCard} nom-card`}>
              <div className={styles.statIcon} style={{ background: 'var(--nom-success-subtle)', color: 'var(--nom-success)' }}>
                <CheckCircle2 size={18} strokeWidth={1.75} />
              </div>
              <div>
                <div className={styles.statNum}>{resumen.total_completadas}</div>
                <div className={styles.statLabel}>Completadas</div>
              </div>
            </div>
            <div className={`${styles.statCard} nom-card`}>
              <div className={styles.statIcon} style={{ background: 'var(--nom-accent-subtle)', color: 'var(--nom-accent)' }}>
                <TrendingUp size={18} strokeWidth={1.75} />
              </div>
              <div>
                <div className={styles.statNum}>{resumen.total_aplicaciones}</div>
                <div className={styles.statLabel}>Total aplicaciones</div>
              </div>
            </div>
          </div>

          {/* Distribución visual */}
          {totalDist > 0 && (
            <div className={`${styles.distCard} nom-card`}>
              <h3 className={styles.distTitle}>Distribución de riesgo</h3>
              <div className={styles.distBars}>
                {Object.entries(CAT).map(([key, cfg]) => {
                  const count = dist[key] || 0;
                  const pct   = totalDist > 0 ? Math.round(count / totalDist * 100) : 0;
                  return (
                    <div
                      key={key}
                      className={`${styles.distBarItem} ${catFilter === key ? styles.distBarItemActive : ''}`}
                      onClick={() => setCatFilter(catFilter === key ? '' : key)}
                    >
                      <div className={styles.distBarLabel}>
                        <span style={{ color: cfg.color }}>{cfg.label}</span>
                        <span className={styles.distBarCount}>{count}</span>
                      </div>
                      <div className={styles.distBarTrack}>
                        <div
                          className={styles.distBarFill}
                          style={{ width: `${pct}%`, background: cfg.color }}
                        />
                      </div>
                      <span className={styles.distBarPct}>{pct}%</span>
                    </div>
                  );
                })}
              </div>
              {catFilter && (
                <button
                  className={styles.clearFilter}
                  onClick={() => setCatFilter('')}
                >
                  <X size={12} /> Ver todos
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div className={styles.loadingWrap}><Loader2 size={28} className="nom-spin" /></div>
      ) : !cicloId ? (
        <div className={styles.empty}>
          <BarChart2 size={40} strokeWidth={1.25} />
          <p>Selecciona un ciclo para ver los resultados.</p>
        </div>
      ) : resultados.length === 0 ? (
        <div className={styles.empty}>
          <BarChart2 size={40} strokeWidth={1.25} />
          <p>
            {catFilter
              ? 'No hay resultados para la categoría seleccionada.'
              : 'No hay diagnósticos calculados para este ciclo. Completa cuestionarios y presiona "Calcular diagnóstico".'}
          </p>
        </div>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead className={styles.thead}>
              <tr>
                <th>Trabajador</th>
                <th>Área</th>
                <th>Guía</th>
                <th>Puntaje</th>
                <th>Nivel de riesgo</th>
                <th>Calculado</th>
                <th></th>
              </tr>
            </thead>
            <tbody className={styles.tbody}>
              {resultados.map(r => (
                <tr key={r.id} onClick={() => openDetalle(r)} className={styles.trClickable}>
                  <td>
                    <div className={styles.nameCell}>{r.trabajador_nombre}</div>
                  </td>
                  <td className={styles.muteCell}>{r.trabajador_area}</td>
                  <td>
                    <span className={styles.guiaChip}>{r.cuestionario_clave}</span>
                  </td>
                  <td>
                    <div className={styles.scoreCell}>
                      <RiesgoBar pct={r.porcentaje} cat={r.categoria} />
                      <span className={styles.scoreNum}>
                        {r.puntaje_total}/{r.puntaje_max}
                      </span>
                    </div>
                  </td>
                  <td><CatChip cat={r.categoria} /></td>
                  <td className={styles.muteCell}>
                    {new Date(r.calculado_en).toLocaleDateString('es-MX')}
                  </td>
                  <td>
                    <ChevronRight size={14} className={styles.rowArrow} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Detalle modal */}
      {detalle && (
        <Overlay onClick={() => setDetalle(null)}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div>
                <h2 className={styles.modalTitle}>{detalle.trabajador_nombre}</h2>
                <p className={styles.modalSub}>
                  {detalle.cuestionario_clave} — {detalle.trabajador_area}
                </p>
              </div>
              <button className={styles.modalClose} onClick={() => setDetalle(null)}>
                <X size={18} />
              </button>
            </div>

            <div className={styles.modalOverall}>
              <div className={styles.overallScore}>
                <span className={styles.overallNum}>{detalle.puntaje_total}</span>
                <span className={styles.overallMax}>/{detalle.puntaje_max}</span>
              </div>
              <div>
                <div className={styles.overallLabel}>Puntaje global</div>
                <CatChip cat={detalle.categoria} />
              </div>
            </div>

            <div className={styles.dominiosList}>
              {(detalle.dominios || []).map(d => {
                const cfg = CAT[d.categoria] || CAT.bajo;
                return (
                  <div key={d.id} className={styles.dominioItem}>
                    <div className={styles.dominioHeader}>
                      <span className={styles.dominioName}>{d.dominio_nombre}</span>
                      <div className={styles.dominioRight}>
                        <span className={styles.dominioScore}>
                          {d.puntaje}/{d.puntaje_max}
                        </span>
                        <CatChip cat={d.categoria} />
                      </div>
                    </div>
                    <div className={styles.dominioBar}>
                      <div
                        className={styles.dominioFill}
                        style={{
                          width: `${d.porcentaje}%`,
                          background: cfg.color,
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
