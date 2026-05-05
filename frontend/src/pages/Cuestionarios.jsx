import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  ClipboardList, Loader2, X, CheckCircle2, Clock, PlayCircle,
  Link2, Trash2, RotateCcw, ChevronDown, FileText, RefreshCw,
} from 'lucide-react';
import { aplicacionesService, guiaLinksService } from '../services/cuestionarios';
import { ciclosService } from '../services/trabajadores';
import styles from './Cuestionarios.module.css';

const ESTADO_CONFIG = {
  pendiente:   { label: 'Pendiente',   cls: 'chip_pendiente'   },
  en_progreso: { label: 'En progreso', cls: 'chip_en_progreso' },
  completado:  { label: 'Completado',  cls: 'chip_completado'  },
};

const GUIA_INFO = {
  V:   { label: 'Guía V',   desc: 'Más de 50 trabajadores',  color: 'var(--nom-accent)'  },
  III: { label: 'Guía III', desc: '16 a 50 trabajadores',    color: 'var(--nom-info)'    },
  I:   { label: 'Guía I',   desc: 'Hasta 15 trabajadores',   color: 'var(--nom-success)' },
};

export default function Cuestionarios() {
  const [aplicaciones, setAplicaciones] = useState([]);
  const [ciclos, setCiclos]             = useState([]);
  const [guiaLinks, setGuiaLinks]       = useState([]);
  const [loading, setLoading]           = useState(true);
  const [cicloFilter, setCicloFilter]   = useState('');
  const [estadoFilter, setEstadoFilter] = useState('');
  const [generando, setGenerando]       = useState(false);
  const [genError, setGenError]         = useState('');
  const [copied, setCopied]             = useState(null);

  const [confirmDel, setConfirmDel]         = useState(null);
  const [confirmLimpiar, setConfirmLimpiar] = useState(null);

  const cicloMap = Object.fromEntries(ciclos.map(c => [c.id, c]));

  const cicloActivo = ciclos.find(c => c.estado !== 'cerrado') || ciclos[0];

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
      const fetchedCiclos = ciclosRes.data.data;
      setCiclos(fetchedCiclos);

      const cicloForLinks = cicloFilter
        || fetchedCiclos.find(c => c.estado !== 'cerrado')?.id
        || fetchedCiclos[0]?.id;

      if (cicloForLinks) {
        const linksRes = await guiaLinksService.list({ ciclo_id: cicloForLinks });
        setGuiaLinks(linksRes.data.data);
      }
    } finally {
      setLoading(false);
    }
  }, [cicloFilter, estadoFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleGenerarLinks = async () => {
    const cicloId = cicloFilter || (cicloActivo ? cicloActivo.id : null);
    if (!cicloId) return;
    setGenerando(true);
    setGenError('');
    try {
      const res = await guiaLinksService.crearLinks({ ciclo_id: Number(cicloId) });
      setGuiaLinks(res.data.data);
    } catch (err) {
      const e = err.response?.data?.errors;
      setGenError(e && typeof e === 'object' ? Object.values(e).flat().join(' ') : 'Error al generar links.');
    } finally {
      setGenerando(false);
    }
  };

  const handleCopyGuiaLink = (token) => {
    const url = `${window.location.origin}/guia/${token}`;
    navigator.clipboard.writeText(url);
    setCopied(token);
    setTimeout(() => setCopied(null), 2500);
  };

  const stats = {
    total:      aplicaciones.length,
    pendiente:  aplicaciones.filter(a => a.estado === 'pendiente').length,
    progreso:   aplicaciones.filter(a => a.estado === 'en_progreso').length,
    completado: aplicaciones.filter(a => a.estado === 'completado').length,
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
      </div>

      {/* Links de Guías */}
      <div className={`${styles.linksSection} nom-card`}>
        <div className={styles.linksSectionHeader}>
          <div>
            <h2 className={styles.linksSectionTitle}>Links de Guías</h2>
            <p className={styles.linksSectionDesc}>
              Comparte el link correspondiente con todos los trabajadores de cada guía.
            </p>
          </div>
          <button
            className="nom-btn nom-btn-primary"
            onClick={handleGenerarLinks}
            disabled={generando || !cicloActivo}
          >
            {generando
              ? <Loader2 size={15} className="nom-spin" />
              : <RefreshCw size={15} strokeWidth={2} />
            }
            {guiaLinks.length > 0 ? 'Regenerar links' : 'Generar links'}
          </button>
        </div>

        {genError && <div className={styles.formError}>{genError}</div>}

        {guiaLinks.length === 0 ? (
          <div className={styles.linksEmpty}>
            <Link2 size={28} strokeWidth={1.25} />
            <p>
              {cicloActivo
                ? 'Genera los links para compartir los cuestionarios con los trabajadores.'
                : 'No hay ciclos disponibles. Crea un ciclo primero.'}
            </p>
          </div>
        ) : (
          <div className={styles.linksGrid}>
            {['V', 'III', 'I'].map(clave => {
              const link = guiaLinks.find(l => l.cuestionario_clave === clave);
              if (!link) return null;
              const info = GUIA_INFO[clave];
              const url  = `${window.location.origin}/guia/${link.token}`;
              const isCopied = copied === link.token;
              return (
                <div key={clave} className={styles.linkCard}>
                  <div className={styles.linkCardBadge} style={{ background: info.color }}>
                    {info.label}
                  </div>
                  <div className={styles.linkCardDesc}>{info.desc}</div>
                  <div className={styles.linkUrlRow}>
                    <span className={styles.linkUrl}>{url}</span>
                    <button
                      className={`${styles.copyBtn} ${isCopied ? styles.copyBtnDone : ''}`}
                      onClick={() => handleCopyGuiaLink(link.token)}
                      title="Copiar link"
                    >
                      {isCopied
                        ? <CheckCircle2 size={15} strokeWidth={2} />
                        : <Link2 size={15} strokeWidth={2} />
                      }
                      {isCopied ? 'Copiado' : 'Copiar'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
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
              : 'Aún no hay respuestas. Los trabajadores aparecerán aquí al identificarse con su número de empleado.'}
          </p>
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
                            title={copied === a.token ? 'Enlace copiado' : 'Copiar enlace'}
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
