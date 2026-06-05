import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  BarChart2, RefreshCw, Loader2, ChevronDown, X,
  ChevronRight, AlertTriangle, CheckCircle2, TrendingUp, FileDown,
  FileText, ShieldCheck, User,
} from 'lucide-react';
import { resultadosService, documentosUrls } from '../services/resultados';
import { ciclosService } from '../services/trabajadores';
import ResultadosDashboard from '../components/resultados/ResultadosDashboard';
import DashboardErrorBoundary from '../components/resultados/DashboardErrorBoundary';
import styles from './Resultados.module.css';

const CAT = {
  nulo:     { label: 'Nulo',        color: 'var(--nom-riesgo-nulo)',     bg: 'rgba(16,185,129,0.10)' },
  bajo:     { label: 'Bajo',        color: 'var(--nom-riesgo-bajo)',     bg: 'rgba(132,204,22,0.10)' },
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
  const [psicoModal, setPsicoModal]   = useState(false);
  const [psicoAnonimo, setPsicoAnonimo] = useState(false);
  const [responsable, setResponsable] = useState('');

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
    } catch (err) {
      console.error('Error al cargar resultados:', err);
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

  // Descarga un documento protegido (PDF) o abre la vista imprimible (fallback HTML local).
  const descargarDocumento = (url, fallbackName) => {
    const token = localStorage.getItem('access_token') || '';
    return fetch(url, { headers: { Authorization: `Bearer ${token}` } })
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
          a.download = cd.match(/filename="?([^";]+)"?/)?.[1] || fallbackName;
          a.click();
          URL.revokeObjectURL(burl);
        });
      })
      .catch(() => alert('Error al generar el documento. Verifica que existan resultados calculados.'));
  };

  const handleDescargar = () => {
    if (!cicloId) return;
    descargarDocumento(documentosUrls.informe(cicloId), `informe_nom035_ciclo_${cicloId}.pdf`);
  };

  const handleReportePsicologico = () => {
    if (!cicloId) return;
    const url = documentosUrls.reportePsicologico(cicloId, {
      anonimo: psicoAnonimo,
      responsable: responsable.trim(),
    });
    descargarDocumento(url, `reporte_psicologico_ciclo_${cicloId}.pdf`);
    setPsicoModal(false);
  };

  const openDetalle = async (r) => {
    if (r.dominios) { setDetalle(r); return; }
    try {
      const res = await resultadosService.get(r.id);
      setDetalle(res.data.data);
    } catch {}
  };

  // Solo cuenta Guía I y III — Guía V nunca genera resultado
  const pendienteCalculo = resumen
    ? ((resumen.guia_iii?.completadas ?? 0) - (resumen.guia_iii?.con_resultado ?? 0))
      + ((resumen.guia_i?.completadas ?? 0) - (resumen.guia_i?.con_resultado ?? 0))
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
            className="nom-btn nom-btn-ghost"
            onClick={() => setPsicoModal(true)}
            disabled={!cicloId || resultados.length === 0}
            title="Generar reporte psicológico para revisión de especialistas"
          >
            <FileText size={15} strokeWidth={2} />
            Reporte psicológico
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
      {cicloId && (
        <DashboardErrorBoundary key={dashKey}>
          <ResultadosDashboard cicloId={cicloId} />
        </DashboardErrorBoundary>
      )}

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

      {/* ---- Modal opciones reporte psicológico ---- */}
      {psicoModal && (
        <Overlay onClick={() => setPsicoModal(false)}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()} style={{ maxWidth: 460 }}>
            <div className={styles.modalHeader}>
              <div>
                <h2 className={styles.modalTitle}>Reporte psicológico</h2>
                <p className={styles.modalSub}>Documento técnico para revisión de un especialista</p>
              </div>
              <button className={styles.modalClose} onClick={() => setPsicoModal(false)}>
                <X size={18} />
              </button>
            </div>

            <div style={{ padding: '4px 2px 8px' }}>
              <label style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--nom-text)' }}>
                Responsable de la evaluación <span style={{ fontWeight: 400, color: 'var(--nom-text-muted)' }}>(opcional)</span>
              </label>
              <input
                type="text"
                value={responsable}
                onChange={e => setResponsable(e.target.value)}
                placeholder="Nombre del responsable"
                style={{
                  width: '100%', padding: '9px 12px', borderRadius: 8,
                  border: '1px solid var(--nom-border)', background: 'var(--nom-bg)',
                  color: 'var(--nom-text)', fontSize: 14, marginBottom: 16,
                }}
              />

              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, color: 'var(--nom-text)' }}>
                Identificación de los trabajadores
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <button
                  type="button"
                  onClick={() => setPsicoAnonimo(false)}
                  style={optStyle(!psicoAnonimo)}
                >
                  <User size={16} />
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontWeight: 600 }}>Incluir nombres</div>
                    <div style={{ fontSize: 12, color: 'var(--nom-text-muted)' }}>Muestra el nombre real de cada trabajador.</div>
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setPsicoAnonimo(true)}
                  style={optStyle(psicoAnonimo)}
                >
                  <ShieldCheck size={16} />
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontWeight: 600 }}>Usar claves anónimas</div>
                    <div style={{ fontSize: 12, color: 'var(--nom-text-muted)' }}>Sustituye los nombres por claves (T001, T002…).</div>
                  </div>
                </button>
              </div>

              <button
                className="nom-btn nom-btn-primary"
                onClick={handleReportePsicologico}
                style={{ width: '100%', marginTop: 18, justifyContent: 'center' }}
              >
                <FileText size={15} strokeWidth={2} />
                Generar reporte
              </button>
            </div>
          </div>
        </Overlay>
      )}
    </div>
  );
}

function optStyle(active) {
  return {
    display: 'flex', alignItems: 'center', gap: 10,
    padding: '10px 12px', borderRadius: 10, cursor: 'pointer',
    border: `1.5px solid ${active ? 'var(--nom-accent)' : 'var(--nom-border)'}`,
    background: active ? 'var(--nom-accent-subtle)' : 'transparent',
    color: 'var(--nom-text)', width: '100%', textAlign: 'left',
    transition: 'all .15s ease',
  };
}
