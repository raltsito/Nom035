import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  ClipboardList, Loader2, X, CheckCircle2, Clock, PlayCircle,
  Link2, RotateCcw, ChevronDown, FileText, RefreshCw, Minus,
} from 'lucide-react';
import { aplicacionesService, guiaLinksService } from '../services/cuestionarios';
import { ciclosService } from '../services/trabajadores';
import styles from './Cuestionarios.module.css';

const ESTADO_CONFIG = {
  pendiente:   { label: 'Pendiente',   cls: 'chip_pendiente',   Icon: Clock        },
  en_progreso: { label: 'En progreso', cls: 'chip_en_progreso', Icon: PlayCircle   },
  completado:  { label: 'Completado',  cls: 'chip_completado',  Icon: CheckCircle2 },
};

const GUIA_INFO = {
  V:   { label: 'Guía V',   color: 'var(--nom-accent)'  },
  III: { label: 'Guía III', color: 'var(--nom-info)'    },
  I:   { label: 'Guía I',   color: 'var(--nom-success)' },
};

function EstadoChip({ estado }) {
  if (!estado) return <span className={styles.chipNull}><Minus size={11} />—</span>;
  const cfg = ESTADO_CONFIG[estado];
  if (!cfg) return null;
  const { Icon } = cfg;
  return (
    <span className={`${styles.statusChip} ${styles[cfg.cls]}`}>
      <Icon size={11} />
      {cfg.label}
    </span>
  );
}

export default function Cuestionarios() {
  const [progreso,    setProgreso]   = useState([]);
  const [ciclos,      setCiclos]     = useState([]);
  const [guiaLinks,   setGuiaLinks]  = useState([]);
  const [loading,     setLoading]    = useState(true);
  const [cicloFilter, setCicloFilter]= useState('');
  const [generando,   setGenerando]  = useState(false);
  const [genError,    setGenError]   = useState('');
  const [copied,      setCopied]     = useState(null);
  const [confirmLimpiar, setConfirmLimpiar] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const ciclosRes = await ciclosService.list();
      const fetchedCiclos = ciclosRes.data.data;
      setCiclos(fetchedCiclos);

      const cicloId = cicloFilter
        || fetchedCiclos.find(c => c.estado !== 'cerrado')?.id
        || fetchedCiclos[0]?.id;

      if (!cicloId) { setLoading(false); return; }

      const [progRes, linksRes] = await Promise.all([
        aplicacionesService.progreso({ ciclo_id: cicloId }),
        guiaLinksService.list({ ciclo_id: cicloId }),
      ]);
      setProgreso(progRes.data.data);
      setGuiaLinks(linksRes.data.data);
    } finally {
      setLoading(false);
    }
  }, [cicloFilter]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const cicloActivo = ciclos.find(c => c.estado !== 'cerrado') || ciclos[0];

  const stats = {
    total:      progreso.length,
    completado: progreso.filter(r => r.guia_V === 'completado' && r.guia_III === 'completado' && r.guia_I === 'completado').length,
    parcial:    progreso.filter(r => (r.guia_V || r.guia_III || r.guia_I) && !(r.guia_V === 'completado' && r.guia_III === 'completado' && r.guia_I === 'completado')).length,
    sinIniciar: progreso.filter(r => !r.guia_V && !r.guia_III && !r.guia_I).length,
  };

  const handleGenerarLinks = async () => {
    const cicloId = cicloFilter || cicloActivo?.id;
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
    navigator.clipboard.writeText(`${window.location.origin}/guia/${token}`);
    setCopied(token);
    setTimeout(() => setCopied(null), 2500);
  };

  const handleLimpiar = async () => {
    if (!confirmLimpiar) return;
    try {
      const cicloId = cicloFilter || cicloActivo?.id;
      const aplRes  = await aplicacionesService.list({ ciclo_id: cicloId });
      const apls    = aplRes.data.data.filter(a => a.trabajador === confirmLimpiar.trabajador_id);
      await Promise.all(apls.map(a => aplicacionesService.limpiarRespuestas(a.id)));
      fetchData();
    } finally {
      setConfirmLimpiar(null);
    }
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
            <p className={styles.linksSectionDesc}>Comparte el link con los trabajadores de cada guía.</p>
          </div>
          <button className="nom-btn nom-btn-primary" onClick={handleGenerarLinks} disabled={generando || !cicloActivo}>
            {generando ? <Loader2 size={15} className="nom-spin" /> : <RefreshCw size={15} strokeWidth={2} />}
            {guiaLinks.length > 0 ? 'Regenerar links' : 'Generar links'}
          </button>
        </div>
        {genError && <div className={styles.formError}>{genError}</div>}
        {guiaLinks.length === 0 ? (
          <div className={styles.linksEmpty}>
            <Link2 size={28} strokeWidth={1.25} />
            <p>{cicloActivo ? 'Genera los links para compartir los cuestionarios.' : 'No hay ciclos disponibles.'}</p>
          </div>
        ) : (
          <div className={styles.linksGrid}>
            {['V', 'III', 'I'].map(clave => {
              const link = guiaLinks.find(l => l.cuestionario_clave === clave);
              if (!link) return null;
              const info    = GUIA_INFO[clave];
              const url     = `${window.location.origin}/guia/${link.token}`;
              const isCopied = copied === link.token;
              return (
                <div key={clave} className={styles.linkCard}>
                  <div className={styles.linkCardBadge} style={{ background: info.color }}>{info.label}</div>
                  <div className={styles.linkUrlRow}>
                    <span className={styles.linkUrl}>{url}</span>
                    <button
                      className={`${styles.copyBtn} ${isCopied ? styles.copyBtnDone : ''}`}
                      onClick={() => handleCopyGuiaLink(link.token)}
                    >
                      {isCopied ? <CheckCircle2 size={15} /> : <Link2 size={15} />}
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
          <div><div className={styles.statNum}>{stats.total}</div><div className={styles.statLabel}>Trabajadores</div></div>
        </div>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon} style={{ background: 'var(--nom-success-subtle)', color: 'var(--nom-success)' }}>
            <CheckCircle2 size={18} strokeWidth={1.75} />
          </div>
          <div><div className={styles.statNum}>{stats.completado}</div><div className={styles.statLabel}>Completos</div></div>
        </div>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon} style={{ background: 'var(--nom-accent-subtle)', color: 'var(--nom-accent)' }}>
            <PlayCircle size={18} strokeWidth={1.75} />
          </div>
          <div><div className={styles.statNum}>{stats.parcial}</div><div className={styles.statLabel}>En progreso</div></div>
        </div>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon} style={{ background: 'var(--nom-warning-subtle)', color: 'var(--nom-warning)' }}>
            <Clock size={18} strokeWidth={1.75} />
          </div>
          <div><div className={styles.statNum}>{stats.sinIniciar}</div><div className={styles.statLabel}>Sin iniciar</div></div>
        </div>
      </div>

      {/* Toolbar */}
      {ciclos.length > 0 && (
        <div className={styles.toolbar}>
          <div className={styles.selectWrap}>
            <ChevronDown size={14} className={styles.selectIcon} />
            <select className={styles.select} value={cicloFilter} onChange={e => setCicloFilter(e.target.value)}>
              <option value="">Ciclo activo</option>
              {ciclos.map(c => <option key={c.id} value={c.id}>Ciclo {c.anio}</option>)}
            </select>
          </div>
        </div>
      )}

      {/* Tabla de progreso */}
      {loading ? (
        <div className={styles.loadingWrap}><Loader2 size={28} className="nom-spin" /></div>
      ) : progreso.length === 0 ? (
        <div className={styles.empty}>
          <FileText size={40} strokeWidth={1.25} />
          <p>No hay trabajadores registrados en este ciclo.</p>
        </div>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead className={styles.thead}>
              <tr>
                <th>Trabajador</th>
                <th>No. Empleado</th>
                <th style={{ color: 'var(--nom-accent)' }}>Guía V</th>
                <th style={{ color: 'var(--nom-info)' }}>Guía III</th>
                <th style={{ color: 'var(--nom-success)' }}>Guía I</th>
                <th></th>
              </tr>
            </thead>
            <tbody className={styles.tbody}>
              {progreso.map(r => (
                <tr key={r.trabajador_id}>
                  <td>
                    <div className={styles.nameCell}>{r.trabajador_nombre}</div>
                    {r.trabajador_puesto && <div className={styles.muteCell}>{r.trabajador_puesto}</div>}
                  </td>
                  <td className={styles.muteCell}>{r.num_empleado || '—'}</td>
                  <td><EstadoChip estado={r.guia_V} /></td>
                  <td><EstadoChip estado={r.guia_III} /></td>
                  <td><EstadoChip estado={r.guia_I} /></td>
                  <td>
                    <div className={styles.actionsCell}>
                      {(r.guia_V || r.guia_III || r.guia_I) && (
                        <button
                          className={styles.actionBtn}
                          onClick={() => setConfirmLimpiar(r)}
                          title="Limpiar respuestas"
                        >
                          <RotateCcw size={14} strokeWidth={1.75} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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
              Se eliminarán todas las respuestas de <strong>{confirmLimpiar.trabajador_nombre}</strong> en todas las guías. Esta acción es irreversible.
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
