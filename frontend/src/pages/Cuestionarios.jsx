import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  ClipboardList, Plus, Loader2, X, CheckCircle2, Clock, PlayCircle,
  Link2, Trash2, RotateCcw, ChevronDown, FileText,
} from 'lucide-react';
import { aplicacionesService } from '../services/cuestionarios';
import { ciclosService } from '../services/trabajadores';
import styles from './Cuestionarios.module.css';

const ESTADO_CONFIG = {
  pendiente:   { label: 'Pendiente',   cls: 'chip_pendiente'   },
  en_progreso: { label: 'En progreso', cls: 'chip_en_progreso' },
  completado:  { label: 'Completado',  cls: 'chip_completado'  },
};

export default function Cuestionarios() {
  const [aplicaciones, setAplicaciones] = useState([]);
  const [ciclos, setCiclos]             = useState([]);
  const [loading, setLoading]           = useState(true);
  const [cicloFilter, setCicloFilter]   = useState('');
  const [estadoFilter, setEstadoFilter] = useState('');

  const [modalMasivo, setModalMasivo]     = useState(false);
  const [selectedCiclo, setSelectedCiclo] = useState('');
  const [creating, setCreating]           = useState(false);
  const [createResult, setCreateResult]   = useState(null);
  const [createError, setCreateError]     = useState('');

  const [confirmDel, setConfirmDel]         = useState(null);
  const [confirmLimpiar, setConfirmLimpiar] = useState(null);
  const [copied, setCopied]                 = useState(null);

  const cicloMap = Object.fromEntries(ciclos.map(c => [c.id, c]));

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (cicloFilter)  params.ciclo_id = cicloFilter;
      if (estadoFilter) params.estado   = estadoFilter;
      const [aplRes, ciclosRes] = await Promise.all([
        aplicacionesService.list(params),
        ciclosService.list(),
      ]);
      setAplicaciones(aplRes.data.data);
      setCiclos(ciclosRes.data.data);
    } finally {
      setLoading(false);
    }
  }, [cicloFilter, estadoFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const stats = {
    total:      aplicaciones.length,
    pendiente:  aplicaciones.filter(a => a.estado === 'pendiente').length,
    progreso:   aplicaciones.filter(a => a.estado === 'en_progreso').length,
    completado: aplicaciones.filter(a => a.estado === 'completado').length,
  };

  const openModalMasivo = () => {
    const primer = ciclos.find(c => c.estado !== 'cerrado') || ciclos[0];
    setSelectedCiclo(primer ? String(primer.id) : '');
    setCreateResult(null);
    setCreateError('');
    setModalMasivo(true);
  };

  const handleCrearMasivo = async () => {
    if (!selectedCiclo) return;
    setCreating(true);
    setCreateError('');
    try {
      const res = await aplicacionesService.crearMasivo({ ciclo_id: Number(selectedCiclo) });
      setCreateResult(res.data.meta);
      fetchData();
    } catch (err) {
      const e = err.response?.data?.errors;
      const msg = e && typeof e === 'object'
        ? Object.values(e).flat().join(' ')
        : 'Ocurrió un error. Intenta de nuevo.';
      setCreateError(msg);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async () => {
    if (!confirmDel) return;
    try {
      await aplicacionesService.delete(confirmDel.id);
      setAplicaciones(prev => prev.filter(a => a.id !== confirmDel.id));
    } finally {
      setConfirmDel(null);
    }
  };

  const handleLimpiar = async () => {
    if (!confirmLimpiar) return;
    try {
      await aplicacionesService.limpiarRespuestas(confirmLimpiar.id);
      fetchData();
    } finally {
      setConfirmLimpiar(null);
    }
  };

  const handleCopyLink = (token) => {
    const url = `${window.location.origin}/responder/${token}`;
    navigator.clipboard.writeText(url);
    setCopied(token);
    setTimeout(() => setCopied(null), 2500);
  };

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Motor de Cuestionarios</h1>
          <p className={styles.subtitle}>Aplicaciones NOM-035-STPS-2018 — Factores de Riesgo Psicosocial</p>
        </div>
        <button className="nom-btn nom-btn-primary" onClick={openModalMasivo}>
          <Plus size={16} strokeWidth={2.5} />
          Crear aplicaciones
        </button>
      </div>

      {/* Stats */}
      <div className={styles.statsRow}>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon}><ClipboardList size={18} strokeWidth={1.75} /></div>
          <div>
            <div className={styles.statNum}>{stats.total}</div>
            <div className={styles.statLabel}>Total</div>
          </div>
        </div>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon} style={{ background: 'var(--nom-warning-subtle)', color: 'var(--nom-warning)' }}>
            <Clock size={18} strokeWidth={1.75} />
          </div>
          <div>
            <div className={styles.statNum}>{stats.pendiente}</div>
            <div className={styles.statLabel}>Pendientes</div>
          </div>
        </div>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon} style={{ background: 'var(--nom-accent-subtle)', color: 'var(--nom-accent)' }}>
            <PlayCircle size={18} strokeWidth={1.75} />
          </div>
          <div>
            <div className={styles.statNum}>{stats.progreso}</div>
            <div className={styles.statLabel}>En progreso</div>
          </div>
        </div>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon} style={{ background: 'var(--nom-success-subtle)', color: 'var(--nom-success)' }}>
            <CheckCircle2 size={18} strokeWidth={1.75} />
          </div>
          <div>
            <div className={styles.statNum}>{stats.completado}</div>
            <div className={styles.statLabel}>Completados</div>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className={styles.toolbar}>
        {ciclos.length > 0 && (
          <div className={styles.selectWrap}>
            <ChevronDown size={14} className={styles.selectIcon} />
            <select
              className={styles.select}
              value={cicloFilter}
              onChange={e => setCicloFilter(e.target.value)}
            >
              <option value="">Todos los ciclos</option>
              {ciclos.map(c => (
                <option key={c.id} value={c.id}>Ciclo {c.anio}</option>
              ))}
            </select>
          </div>
        )}
        {['', 'pendiente', 'en_progreso', 'completado'].map(est => (
          <button
            key={est}
            className={`${styles.filterChip} ${estadoFilter === est ? styles.filterChipActive : ''}`}
            onClick={() => setEstadoFilter(est)}
          >
            {est === '' ? 'Todos' : ESTADO_CONFIG[est]?.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <div className={styles.loadingWrap}><Loader2 size={28} className="nom-spin" /></div>
      ) : aplicaciones.length === 0 ? (
        <div className={styles.empty}>
          <FileText size={40} strokeWidth={1.25} />
          <p>
            {estadoFilter || cicloFilter
              ? 'No hay aplicaciones para los filtros seleccionados.'
              : 'Aún no hay aplicaciones. Crea la primera aplicación masiva.'}
          </p>
          {!estadoFilter && !cicloFilter && (
            <button className="nom-btn nom-btn-accent" onClick={openModalMasivo}>
              <Plus size={15} />
              Crear aplicaciones masivas
            </button>
          )}
        </div>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead className={styles.thead}>
              <tr>
                <th>Trabajador</th>
                <th>Guía</th>
                <th>Ciclo</th>
                <th>Estado</th>
                <th>Progreso</th>
                <th>Completado</th>
                <th></th>
              </tr>
            </thead>
            <tbody className={styles.tbody}>
              {aplicaciones.map(a => {
                const pct = a.total_preguntas
                  ? Math.round((a.total_respondidas / a.total_preguntas) * 100)
                  : 0;
                const ciclo = cicloMap[a.ciclo];
                const cfg   = ESTADO_CONFIG[a.estado];
                return (
                  <tr key={a.id}>
                    <td>
                      <div className={styles.nameCell}>{a.trabajador_nombre}</div>
                      {a.trabajador_puesto && (
                        <div className={styles.muteCell}>{a.trabajador_puesto}</div>
                      )}
                    </td>
                    <td>
                      <span className={styles.guiaChip}>{a.cuestionario_clave}</span>
                    </td>
                    <td className={styles.muteCell}>
                      {ciclo ? ciclo.anio : a.ciclo ? `#${a.ciclo}` : '—'}
                    </td>
                    <td>
                      <span className={`${styles.statusChip} ${cfg ? styles[cfg.cls] : ''}`}>
                        {a.estado === 'pendiente'   && <Clock size={11} />}
                        {a.estado === 'en_progreso' && <PlayCircle size={11} />}
                        {a.estado === 'completado'  && <CheckCircle2 size={11} />}
                        {cfg?.label}
                      </span>
                    </td>
                    <td>
                      <div className={styles.progressWrap}>
                        <div className={styles.progressBar}>
                          <div className={styles.progressFill} style={{ width: `${pct}%` }} />
                        </div>
                        <span className={styles.progressText}>
                          {a.total_respondidas}/{a.total_preguntas}
                        </span>
                      </div>
                    </td>
                    <td className={styles.muteCell}>
                      {a.fecha_completado
                        ? new Date(a.fecha_completado).toLocaleDateString('es-MX')
                        : '—'}
                    </td>
                    <td>
                      <div className={styles.actionsCell}>
                        {a.estado !== 'completado' && (
                          <button
                            className={`${styles.actionBtn} ${copied === a.token ? styles.actionCopied : ''}`}
                            onClick={() => handleCopyLink(a.token)}
                            title={copied === a.token ? 'Enlace copiado' : 'Copiar enlace para el trabajador'}
                          >
                            {copied === a.token
                              ? <CheckCircle2 size={14} strokeWidth={1.75} />
                              : <Link2 size={14} strokeWidth={1.75} />
                            }
                          </button>
                        )}
                        {a.estado !== 'pendiente' && (
                          <button
                            className={styles.actionBtn}
                            onClick={() => setConfirmLimpiar(a)}
                            title="Limpiar respuestas"
                          >
                            <RotateCcw size={14} strokeWidth={1.75} />
                          </button>
                        )}
                        <button
                          className={`${styles.actionBtn} ${styles.actionDanger}`}
                          onClick={() => setConfirmDel(a)}
                          title="Eliminar aplicación"
                        >
                          <Trash2 size={14} strokeWidth={1.75} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal: Crear masivo */}
      {modalMasivo && (
        <Overlay onClick={() => !creating && setModalMasivo(false)}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Crear aplicaciones masivas</h2>
              {!creating && (
                <button className={styles.modalClose} onClick={() => setModalMasivo(false)}>
                  <X size={18} />
                </button>
              )}
            </div>

            {createResult ? (
              <div className={styles.resultBox}>
                <div className={styles.resultIconWrap}><CheckCircle2 size={32} /></div>
                <p className={styles.resultTitle}>Aplicaciones creadas exitosamente</p>
                <p className={styles.resultSub}>
                  Se crearon <strong>{createResult.creadas}</strong> nuevas aplicaciones.
                  {createResult.ya_existian > 0 && (
                    <> {createResult.ya_existian} ya existían y se omitieron.</>
                  )}
                </p>
                <button className="nom-btn nom-btn-primary" onClick={() => setModalMasivo(false)}>
                  Ver aplicaciones
                </button>
              </div>
            ) : (
              <>
                <p className={styles.modalDesc}>
                  Se creará una aplicación por cada trabajador activo. La guía se selecciona automáticamente según el número de trabajadores del centro de trabajo.
                </p>

                <div className={styles.field}>
                  <label className={styles.label}>Ciclo NOM-035 *</label>
                  {ciclos.length === 0 ? (
                    <p className={styles.noData}>
                      No hay ciclos disponibles. Crea un ciclo en la sección de Trabajadores primero.
                    </p>
                  ) : (
                    <div className={styles.selectWrapInline}>
                      <ChevronDown size={14} className={styles.selectIconInline} />
                      <select
                        className="nom-input"
                        value={selectedCiclo}
                        onChange={e => setSelectedCiclo(e.target.value)}
                      >
                        {ciclos.map(c => (
                          <option key={c.id} value={c.id}>
                            Ciclo {c.anio} — {c.estado}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>

                {createError && <div className={styles.formError}>{createError}</div>}

                <div className={styles.modalActions}>
                  <button className="nom-btn nom-btn-ghost" onClick={() => setModalMasivo(false)}>
                    Cancelar
                  </button>
                  <button
                    className="nom-btn nom-btn-primary"
                    onClick={handleCrearMasivo}
                    disabled={creating || !selectedCiclo}
                  >
                    {creating ? <Loader2 size={15} className="nom-spin" /> : 'Crear aplicaciones'}
                  </button>
                </div>
              </>
            )}
          </div>
        </Overlay>
      )}

      {/* Modal: Confirmar eliminar */}
      {confirmDel && (
        <Overlay onClick={() => setConfirmDel(null)}>
          <div className={`${styles.modal} ${styles.modalSm} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Eliminar aplicación</h2>
              <button className={styles.modalClose} onClick={() => setConfirmDel(null)}><X size={18} /></button>
            </div>
            <p className={styles.confirmText}>
              Se eliminará la aplicación de <strong>{confirmDel.trabajador_nombre}</strong> junto con todas sus respuestas. Esta acción es irreversible.
            </p>
            <div className={styles.modalActions}>
              <button className="nom-btn nom-btn-ghost" onClick={() => setConfirmDel(null)}>Cancelar</button>
              <button className={`nom-btn ${styles.btnDanger}`} onClick={handleDelete}>Eliminar</button>
            </div>
          </div>
        </Overlay>
      )}

      {/* Modal: Confirmar limpiar */}
      {confirmLimpiar && (
        <Overlay onClick={() => setConfirmLimpiar(null)}>
          <div className={`${styles.modal} ${styles.modalSm} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Limpiar respuestas</h2>
              <button className={styles.modalClose} onClick={() => setConfirmLimpiar(null)}><X size={18} /></button>
            </div>
            <p className={styles.confirmText}>
              Se eliminarán todas las respuestas de <strong>{confirmLimpiar.trabajador_nombre}</strong> y el cuestionario volverá a estado pendiente.
            </p>
            <div className={styles.modalActions}>
              <button className="nom-btn nom-btn-ghost" onClick={() => setConfirmLimpiar(null)}>Cancelar</button>
              <button className={`nom-btn ${styles.btnDanger}`} onClick={handleLimpiar}>Limpiar</button>
            </div>
          </div>
        </Overlay>
      )}
    </div>
  );
}
