import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  BarChart2, RefreshCw, Loader2, ChevronDown, X,
  ChevronRight, AlertTriangle, CheckCircle2, TrendingUp, FileDown,
} from 'lucide-react';
import { resultadosService } from '../services/resultados';
import { ciclosService } from '../services/trabajadores';
import ResultadosDashboard from '../components/resultados/ResultadosDashboard';
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
    <span className={styles.catChip} style={{ background: c.bg, color: c.color }}>
      {c.label}
    </span>
  );
}

function RiesgoBar({ pct, cat }) {
  const c = CAT[cat] || CAT.bajo;
  return (
    <div className={styles.riesgoBar}>
      <div className={styles.riesgoFill} style={{ width: `${pct}%`, background: c.color }} />
    </div>
  );
}

export default function Resultados() {
  const [ciclos, setCiclos]           = useState([]);
  const [cicloId, setCicloId]         = useState('');
  const [resultados, setResultados]   = useState([]);
  const [resumen, setResumen]         = useState(null);
  const [loading, setLoading]         = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [calcError, setCalcError]     = useState('');
  const [detalle, setDetalle]         = useState(null);
  const [catFilter, setCatFilter]     = useState('');
  const [dashKey, setDashKey]         = useState(0);
  const [tablaAbierta, setTablaAbierta] = useState(false);

  useEffect(() => {
    ciclosService.list().then(res => {
      const data = res.data.data || [];
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

  const handleCalcular = async () => {
    if (!cicloId) return;
    setCalculating(true);
    setCalcError('');
    try {
      await resultadosService.calcular({ ciclo_id: Number(cicloId) });
      setDashKey(k => k + 1);
      await fetchResultados();
    } catch (err) {
      const e = err.response?.data?.errors;
      const msg = e && typeof e === 'object'
        ? Object.values(e).flat().join(' ')
        : 'Ocurrio un error al calcular.';
      setCalcError(msg);
    } finally {
      setCalculating(false);
    }
  };

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

  const dist      = resumen?.distribucion || {};
  const totalDist = Object.values(dist).reduce((a, b) => a + b, 0);

  return (
    <div className={styles.page}>

      {/* ---- Header ---- */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Resultados y Diagnostico</h1>
          <p className={styles.subtitle}>Dashboard analitico NOM-035-STPS-2018</p>
        </div>
        <div className={styles.headerActions}>
          {ciclos.length > 0 && (
            <div className={styles.selectWrap}>
              <ChevronDown size={14} className={styles.selectIcon} />
              <select
                className={styles.select}
                value={cicloId}
                onChange={e => { setCicloId(e.target.value); setCatFilter(''); }}
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
            {calculating ? 'Calculando...' : 'Calcular diagnostico'}
          </button>
        </div>
      </div>

      {/* ---- Banners ---- */}
      {calcError && (
        <div className={styles.errorBanner}>
          <AlertTriangle size={15} />
          {calcError}
        </div>
      )}
      {pendienteCalculo > 0 && (
        <div className={styles.warnBanner}>
          <AlertTriangle size={15} />
          Hay {pendienteCalculo} aplicacion(es) completada(s) sin diagnostico calculado. Presiona "Calcular diagnostico".
        </div>
      )}

      {/* ---- Stats + distribucion ---- */}
      {resumen && (
        <div className={styles.statsSection}>
          <div className={styles.statsRow}>
            <div className={`${styles.statCard} nom-card`}>
              <div className={styles.statIcon}><BarChart2 size={18} strokeWidth={1.75} /></div>
              <div>
                <div className={styles.statNum}>{resumen.total_resultados}</div>
                <div className={styles.statLabel}>Con diagnostico</div>
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

          {totalDist > 0 && (
            <div className={`${styles.distCard} nom-card`}>
              <h3 className={styles.distTitle}>Distribucion de riesgo</h3>
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
                <button className={styles.clearFilter} onClick={() => setCatFilter('')}>
                  <X size={12} /> Ver todos
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* ---- Tabla colapsable de resultados individuales ---- */}
      {cicloId && (
        <div className={styles.tablaSection}>
          <button
            className={styles.tablaToggle}
            onClick={() => setTablaAbierta(v => !v)}
          >
            <span className={styles.tablaToggleLeft}>
              <ChevronRight
                size={16}
                className={`${styles.tablaToggleIcon} ${tablaAbierta ? styles.tablaToggleIconOpen : ''}`}
              />
              Detalle por trabajador
              {resultados.length > 0 && (
                <span className={styles.tablaCount}>{resultados.length} registros</span>
              )}
            </span>
            {catFilter && (
              <span className={styles.tablaFilterBadge}>
                Filtrando: {CAT[catFilter]?.label}
                <button
                  className={styles.tablaFilterClear}
                  onClick={e => { e.stopPropagation(); setCatFilter(''); }}
                >
                  <X size={11} />
                </button>
              </span>
            )}
          </button>

          {tablaAbierta && (
            <div className={styles.tablaBody}>
              {loading ? (
                <div className={styles.loadingWrap}><Loader2 size={24} className="nom-spin" /></div>
              ) : resultados.length === 0 ? (
                <div className={styles.empty}>
                  <BarChart2 size={36} strokeWidth={1.25} />
                  <p>
                    {catFilter
                      ? 'No hay resultados para la categoria seleccionada.'
                      : 'No hay diagnosticos calculados. Completa cuestionarios y presiona "Calcular diagnostico".'}
                  </p>
                </div>
              ) : (
                <div className={styles.tableWrap}>
                  <table className={styles.table}>
                    <thead className={styles.thead}>
                      <tr>
                        <th>Trabajador</th>
                        <th>Area</th>
                        <th>Guia</th>
                        <th>Puntaje</th>
                        <th>Nivel de riesgo</th>
                        <th>Calculado</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody className={styles.tbody}>
                      {resultados.map(r => (
                        <tr key={r.id} onClick={() => openDetalle(r)} className={styles.trClickable}>
                          <td><div className={styles.nameCell}>{r.trabajador_nombre}</div></td>
                          <td className={styles.muteCell}>{r.trabajador_area}</td>
                          <td><span className={styles.guiaChip}>{r.cuestionario_clave}</span></td>
                          <td>
                            <div className={styles.scoreCell}>
                              <RiesgoBar pct={r.porcentaje} cat={r.categoria} />
                              <span className={styles.scoreNum}>{r.puntaje_total}/{r.puntaje_max}</span>
                            </div>
                          </td>
                          <td><CatChip cat={r.categoria} /></td>
                          <td className={styles.muteCell}>
                            {new Date(r.calculado_en).toLocaleDateString('es-MX')}
                          </td>
                          <td><ChevronRight size={14} className={styles.rowArrow} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ---- Separador ---- */}
      {cicloId && resumen && <div className={styles.sectionDivider} />}

      {/* ---- Dashboard analitico (Bento Grid) ---- */}
      {cicloId && <ResultadosDashboard key={dashKey} cicloId={cicloId} />}

      {/* ---- Modal detalle por trabajador ---- */}
      {detalle && (
        <Overlay onClick={() => setDetalle(null)}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div>
                <h2 className={styles.modalTitle}>{detalle.trabajador_nombre}</h2>
                <p className={styles.modalSub}>
                  Guia {detalle.cuestionario_clave} — {detalle.trabajador_area}
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
                        <span className={styles.dominioScore}>{d.puntaje}/{d.puntaje_max}</span>
                        <CatChip cat={d.categoria} />
                      </div>
                    </div>
                    <div className={styles.dominioBar}>
                      <div
                        className={styles.dominioFill}
                        style={{ width: `${d.porcentaje}%`, background: cfg.color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </Overlay>
      )}
    </div>
  );
}
