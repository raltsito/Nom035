import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  ClipboardList, Plus, FileDown, Loader2, X,
  ChevronDown, Pencil, Trash2, AlertTriangle,
  CheckCircle2, Clock, CircleDot, Ban,
} from 'lucide-react';
import { planAccionService, accionesService } from '../services/planAccion';
import { ciclosService } from '../services/trabajadores';
import styles from './PlanAccion.module.css';

// --- Config chips ---
const TIPO_CFG = {
  preventiva: { label: 'Preventiva',      color: 'var(--nom-accent)',   bg: 'var(--nom-accent-subtle)' },
  correctiva: { label: 'Correctiva',      color: 'var(--nom-danger)',   bg: 'var(--nom-danger-subtle)' },
  mejora:     { label: 'Mejora continua', color: '#7c3aed',             bg: 'rgba(124,58,237,0.10)' },
};
const PRIO_CFG = {
  alta:  { label: 'Alta',  color: 'var(--nom-danger)',   bg: 'var(--nom-danger-subtle)' },
  media: { label: 'Media', color: '#d97706',             bg: 'rgba(245,158,11,0.10)' },
  baja:  { label: 'Baja',  color: 'var(--nom-text-muted)', bg: 'var(--nom-bg-subtle)' },
};
const ESTADO_CFG = {
  pendiente:   { label: 'Pendiente',   icon: CircleDot,    color: 'var(--nom-text-muted)', bg: 'var(--nom-bg-subtle)' },
  en_progreso: { label: 'En progreso', icon: Clock,        color: '#d97706',               bg: 'rgba(245,158,11,0.10)' },
  completado:  { label: 'Completado',  icon: CheckCircle2, color: 'var(--nom-success)',    bg: 'var(--nom-success-subtle)' },
  cancelado:   { label: 'Cancelado',   icon: Ban,          color: 'var(--nom-danger)',     bg: 'var(--nom-danger-subtle)' },
};

const EMPTY_PLAN   = { ciclo: '', descripcion: '' };
const EMPTY_ACCION = {
  descripcion: '', tipo: 'preventiva', factor_riesgo: '',
  responsable: '', fecha_limite: '', prioridad: 'media',
  estado: 'pendiente', avance_notas: '',
};

function Chip({ map, val }) {
  const c = map[val] || {};
  const Icon = c.icon;
  return (
    <span className={styles.chip} style={{ color: c.color, background: c.bg }}>
      {Icon && <Icon size={10} strokeWidth={2.5} />}
      {c.label}
    </span>
  );
}

export default function PlanAccion() {
  const [ciclos, setCiclos]   = useState([]);
  const [cicloId, setCicloId] = useState('');
  const [plan, setPlan]       = useState(null);
  const [acciones, setAcciones] = useState([]);
  const [loading, setLoading] = useState(false);

  const [estadoFilter, setEstadoFilter] = useState('');
  const [modal, setModal]         = useState(null); // null | 'plan' | 'accion'
  const [editTarget, setEditTarget] = useState(null);
  const [form, setForm]           = useState(EMPTY_PLAN);
  const [aForm, setAForm]         = useState(EMPTY_ACCION);
  const [saving, setSaving]       = useState(false);
  const [formErr, setFormErr]     = useState('');
  const [confirmDel, setConfirmDel] = useState(null);

  useEffect(() => {
    ciclosService.list().then(res => {
      const data = res.data.data;
      setCiclos(data);
      if (data.length > 0) setCicloId(String(data[0].id));
    });
  }, []);

  const fetchPlan = useCallback(async () => {
    if (!cicloId) return;
    setLoading(true);
    try {
      const res = await planAccionService.list({ ciclo_id: cicloId });
      const p   = res.data.data[0] || null;
      setPlan(p);
      if (p) {
        const aRes = await accionesService.list({ plan_id: p.id });
        setAcciones(aRes.data.data);
      } else {
        setAcciones([]);
      }
    } finally {
      setLoading(false);
    }
  }, [cicloId]);

  useEffect(() => { fetchPlan(); }, [fetchPlan]);

  // --- Modals ---
  const openCreatePlan = () => {
    setForm({ ...EMPTY_PLAN, ciclo: cicloId });
    setFormErr('');
    setEditTarget(null);
    setModal('plan');
  };

  const openEditPlan = () => {
    setForm({ ciclo: String(plan.ciclo), descripcion: plan.descripcion || '' });
    setFormErr('');
    setEditTarget(plan);
    setModal('plan');
  };

  const openAddAccion = () => {
    setAForm(EMPTY_ACCION);
    setFormErr('');
    setEditTarget(null);
    setModal('accion');
  };

  const openEditAccion = (a) => {
    setAForm({
      descripcion:   a.descripcion,
      tipo:          a.tipo,
      factor_riesgo: a.factor_riesgo || '',
      responsable:   a.responsable,
      fecha_limite:  a.fecha_limite,
      prioridad:     a.prioridad,
      estado:        a.estado,
      avance_notas:  a.avance_notas || '',
    });
    setFormErr('');
    setEditTarget(a);
    setModal('accion');
  };

  const closeModal = () => { setModal(null); setEditTarget(null); setFormErr(''); };

  // --- Save ---
  const handleSavePlan = async (e) => {
    e.preventDefault();
    setSaving(true); setFormErr('');
    try {
      const payload = { ...form, ciclo: Number(form.ciclo) };
      if (editTarget) {
        await planAccionService.update(editTarget.id, payload);
      } else {
        await planAccionService.create(payload);
      }
      closeModal();
      fetchPlan();
    } catch (err) {
      const errors = err.response?.data?.errors;
      setFormErr(errors ? Object.values(errors).flat().join(' ') : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAccion = async (e) => {
    e.preventDefault();
    setSaving(true); setFormErr('');
    try {
      const payload = { ...aForm, plan: plan.id };
      if (editTarget) {
        await accionesService.update(editTarget.id, payload);
      } else {
        await accionesService.create(payload);
      }
      closeModal();
      fetchPlan();
    } catch (err) {
      const errors = err.response?.data?.errors;
      setFormErr(errors ? Object.values(errors).flat().join(' ') : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirmDel) return;
    try {
      if (confirmDel.type === 'accion') await accionesService.delete(confirmDel.id);
      fetchPlan();
    } finally {
      setConfirmDel(null);
    }
  };

  const handleDescargar = () => {
    if (!plan) return;
    const token = localStorage.getItem('access_token') || '';
    fetch(`/api/v1/plan-accion/${plan.id}/reporte/`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then(r => {
      const ct = r.headers.get('content-type') || '';
      const cd = r.headers.get('content-disposition') || '';
      if (ct.includes('text/html')) {
        return r.text().then(html => {
          const w = window.open('', '_blank');
          w.document.write(html); w.document.close();
        });
      }
      return r.blob().then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = cd.match(/filename="?([^";]+)"?/)?.[1] || `plan_accion_${cicloId}.pdf`;
        a.click();
        URL.revokeObjectURL(a.href);
      });
    }).catch(() => alert('Error al generar el reporte.'));
  };

  const stats    = plan?.stats || {};
  const filtered = estadoFilter ? acciones.filter(a => a.estado === estadoFilter) : acciones;
  const cicloAnio = ciclos.find(c => String(c.id) === cicloId)?.anio || cicloId;

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Plan de Accion</h1>
          <p className={styles.subtitle}>Medidas correctivas y preventivas para reducir factores de riesgo psicosocial</p>
        </div>
        <div className={styles.headerActions}>
          {ciclos.length > 0 && (
            <div className={styles.selectWrap}>
              <ChevronDown size={14} className={styles.selectIcon} />
              <select className={styles.select} value={cicloId} onChange={e => setCicloId(e.target.value)}>
                {ciclos.map(c => <option key={c.id} value={c.id}>Ciclo {c.anio}</option>)}
              </select>
            </div>
          )}
          {plan && (
            <button className="nom-btn nom-btn-ghost" onClick={handleDescargar}>
              <FileDown size={15} strokeWidth={2} />
              Descargar PDF
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className={styles.loadingWrap}><Loader2 size={28} className="nom-spin" /></div>
      ) : !plan ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}><ClipboardList size={36} strokeWidth={1.25} /></div>
          <h2 className={styles.emptyTitle}>Sin plan de accion</h2>
          <p className={styles.emptyText}>
            Crea el plan de accion para el ciclo {cicloAnio} y registra las medidas a implementar.
          </p>
          <button className="nom-btn nom-btn-primary" onClick={openCreatePlan} disabled={!cicloId}>
            <Plus size={15} />
            Crear plan
          </button>
        </div>
      ) : (
        <div className={styles.content}>
          {/* Progress card */}
          <div className={`${styles.progressCard} nom-card`}>
            <div className={styles.progressTop}>
              <div>
                <div className={styles.progressTitle}>Avance del plan — Ciclo {plan.ciclo_anio}</div>
                {plan.descripcion && (
                  <div className={styles.progressDesc}>{plan.descripcion}</div>
                )}
              </div>
              <button className={styles.editPlanBtn} onClick={openEditPlan}>
                <Pencil size={13} strokeWidth={1.75} /> Editar
              </button>
            </div>

            <div className={styles.progressBarWrap}>
              <div className={styles.progressBar}>
                <div
                  className={styles.progressFill}
                  style={{ width: `${stats.pct_avance || 0}%` }}
                />
              </div>
              <span className={styles.progressPct}>{stats.pct_avance || 0}%</span>
            </div>

            <div className={styles.statsRow}>
              {[
                { key: 'total',       label: 'Total',       val: stats.total       || 0, color: 'var(--nom-text)' },
                { key: 'completadas', label: 'Completadas', val: stats.completadas || 0, color: 'var(--nom-success)' },
                { key: 'en_progreso', label: 'En progreso', val: stats.en_progreso || 0, color: '#d97706' },
                { key: 'pendientes',  label: 'Pendientes',  val: stats.pendientes  || 0, color: 'var(--nom-text-muted)' },
              ].map(s => (
                <button
                  key={s.key}
                  className={`${styles.statChip} ${estadoFilter === (s.key === 'total' ? '' : s.key) ? styles.statChipActive : ''}`}
                  onClick={() => setEstadoFilter(estadoFilter === (s.key === 'total' ? '' : s.key) ? '' : (s.key === 'total' ? '' : s.key))}
                  style={{ '--chip-color': s.color }}
                >
                  <span className={styles.statNum} style={{ color: s.color }}>{s.val}</span>
                  <span className={styles.statLabel}>{s.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Actions section */}
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>
              Acciones
              {estadoFilter && (
                <button className={styles.clearFilter} onClick={() => setEstadoFilter('')}>
                  <X size={12} /> Limpiar filtro
                </button>
              )}
            </h2>
            <button className="nom-btn nom-btn-primary" onClick={openAddAccion}>
              <Plus size={15} /> Nueva accion
            </button>
          </div>

          {filtered.length === 0 ? (
            <div className={styles.emptyAcciones}>
              <ClipboardList size={32} strokeWidth={1.25} />
              <p>{estadoFilter ? 'Sin acciones para este estado.' : 'Agrega la primera accion al plan.'}</p>
            </div>
          ) : (
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead className={styles.thead}>
                  <tr>
                    <th>Descripcion</th>
                    <th>Tipo</th>
                    <th>Factor</th>
                    <th>Responsable</th>
                    <th>Fecha limite</th>
                    <th>Prioridad</th>
                    <th>Estado</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map(a => (
                    <tr key={a.id} className={`${styles.tr} ${a.vencida ? styles.trVencida : ''}`}>
                      <td className={styles.tdDesc}>
                        <div className={styles.descText}>{a.descripcion}</div>
                        {a.avance_notas && (
                          <div className={styles.notasText}>{a.avance_notas}</div>
                        )}
                      </td>
                      <td><Chip map={TIPO_CFG}    val={a.tipo} /></td>
                      <td className={styles.tdMuted}>{a.factor_riesgo || '—'}</td>
                      <td className={styles.tdMuted}>{a.responsable}</td>
                      <td className={`${styles.tdMuted} ${a.vencida ? styles.vencida : ''}`}>
                        {new Date(a.fecha_limite + 'T00:00:00').toLocaleDateString('es-MX')}
                        {a.vencida && <span className={styles.vencidaTag}>Vencida</span>}
                      </td>
                      <td><Chip map={PRIO_CFG}   val={a.prioridad} /></td>
                      <td><Chip map={ESTADO_CFG} val={a.estado} /></td>
                      <td>
                        <div className={styles.rowActions}>
                          <button className={styles.rowBtn} onClick={() => openEditAccion(a)} title="Editar">
                            <Pencil size={13} strokeWidth={1.75} />
                          </button>
                          <button
                            className={`${styles.rowBtn} ${styles.rowBtnDanger}`}
                            onClick={() => setConfirmDel({ type: 'accion', id: a.id, label: a.descripcion.slice(0, 50) })}
                            title="Eliminar"
                          >
                            <Trash2 size={13} strokeWidth={1.75} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ---- Modal Plan ---- */}
      {modal === 'plan' && (
        <Overlay onClick={closeModal}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>{editTarget ? 'Editar plan' : 'Crear plan de accion'}</h2>
              <button className={styles.modalClose} onClick={closeModal}><X size={18} /></button>
            </div>
            <form onSubmit={handleSavePlan} className={styles.modalForm}>
              <div className={styles.field}>
                <label className={styles.label}>Descripcion / objetivo general</label>
                <textarea
                  className="nom-input"
                  placeholder="Objetivo general del plan de accion para este ciclo..."
                  value={form.descripcion}
                  onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))}
                  rows={3}
                  style={{ resize: 'vertical' }}
                />
              </div>
              {formErr && <div className={styles.formError}>{formErr}</div>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  {saving ? 'Guardando...' : (editTarget ? 'Guardar cambios' : 'Crear plan')}
                </button>
              </div>
            </form>
          </div>
        </Overlay>
      )}

      {/* ---- Modal Accion ---- */}
      {modal === 'accion' && (
        <Overlay onClick={closeModal}>
          <div className={`${styles.modal} ${styles.modalLg} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>{editTarget ? 'Editar accion' : 'Nueva accion'}</h2>
              <button className={styles.modalClose} onClick={closeModal}><X size={18} /></button>
            </div>
            <form onSubmit={handleSaveAccion} className={styles.modalForm}>
              <div className={styles.formGrid}>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Descripcion de la medida *</label>
                  <textarea
                    className="nom-input"
                    placeholder="Describe la accion o medida a implementar..."
                    value={aForm.descripcion}
                    onChange={e => setAForm(f => ({ ...f, descripcion: e.target.value }))}
                    rows={2}
                    style={{ resize: 'vertical' }}
                    required
                  />
                </div>

                <div className={styles.field}>
                  <label className={styles.label}>Tipo *</label>
                  <div className={styles.selectWrap} style={{ position: 'relative', maxWidth: '100%' }}>
                    <ChevronDown size={14} className={styles.selectIcon} />
                    <select
                      className={styles.select}
                      style={{ width: '100%', paddingLeft: '14px' }}
                      value={aForm.tipo}
                      onChange={e => setAForm(f => ({ ...f, tipo: e.target.value }))}
                    >
                      <option value="preventiva">Preventiva</option>
                      <option value="correctiva">Correctiva</option>
                      <option value="mejora">Mejora continua</option>
                    </select>
                  </div>
                </div>

                <div className={styles.field}>
                  <label className={styles.label}>Prioridad *</label>
                  <div className={styles.selectWrap} style={{ position: 'relative', maxWidth: '100%' }}>
                    <ChevronDown size={14} className={styles.selectIcon} />
                    <select
                      className={styles.select}
                      style={{ width: '100%', paddingLeft: '14px' }}
                      value={aForm.prioridad}
                      onChange={e => setAForm(f => ({ ...f, prioridad: e.target.value }))}
                    >
                      <option value="alta">Alta</option>
                      <option value="media">Media</option>
                      <option value="baja">Baja</option>
                    </select>
                  </div>
                </div>

                <div className={styles.field}>
                  <label className={styles.label}>Factor de riesgo</label>
                  <input
                    className="nom-input"
                    placeholder="Ej. Carga de trabajo, liderazgo..."
                    value={aForm.factor_riesgo}
                    onChange={e => setAForm(f => ({ ...f, factor_riesgo: e.target.value }))}
                  />
                </div>

                <div className={styles.field}>
                  <label className={styles.label}>Responsable *</label>
                  <input
                    className="nom-input"
                    placeholder="Nombre o area responsable"
                    value={aForm.responsable}
                    onChange={e => setAForm(f => ({ ...f, responsable: e.target.value }))}
                    required
                  />
                </div>

                <div className={styles.field}>
                  <label className={styles.label}>Fecha limite *</label>
                  <input
                    className="nom-input"
                    type="date"
                    value={aForm.fecha_limite}
                    onChange={e => setAForm(f => ({ ...f, fecha_limite: e.target.value }))}
                    required
                  />
                </div>

                <div className={styles.field}>
                  <label className={styles.label}>Estado</label>
                  <div className={styles.selectWrap} style={{ position: 'relative', maxWidth: '100%' }}>
                    <ChevronDown size={14} className={styles.selectIcon} />
                    <select
                      className={styles.select}
                      style={{ width: '100%', paddingLeft: '14px' }}
                      value={aForm.estado}
                      onChange={e => setAForm(f => ({ ...f, estado: e.target.value }))}
                    >
                      <option value="pendiente">Pendiente</option>
                      <option value="en_progreso">En progreso</option>
                      <option value="completado">Completado</option>
                      <option value="cancelado">Cancelado</option>
                    </select>
                  </div>
                </div>

                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Notas de avance</label>
                  <textarea
                    className="nom-input"
                    placeholder="Comentarios sobre el progreso o evidencias..."
                    value={aForm.avance_notas}
                    onChange={e => setAForm(f => ({ ...f, avance_notas: e.target.value }))}
                    rows={2}
                    style={{ resize: 'vertical' }}
                  />
                </div>
              </div>

              {formErr && <div className={styles.formError}>{formErr}</div>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  {saving ? 'Guardando...' : (editTarget ? 'Guardar cambios' : 'Agregar accion')}
                </button>
              </div>
            </form>
          </div>
        </Overlay>
      )}

      {/* ---- Confirm delete ---- */}
      {confirmDel && (
        <Overlay onClick={() => setConfirmDel(null)}>
          <div className={`${styles.modal} ${styles.modalSm} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Eliminar accion</h2>
              <button className={styles.modalClose} onClick={() => setConfirmDel(null)}><X size={18} /></button>
            </div>
            <div className={styles.confirmWrap}>
              <AlertTriangle size={30} className={styles.confirmIcon} />
              <p className={styles.confirmText}>
                Se eliminara: <strong>{confirmDel.label}</strong>. Esta accion no se puede deshacer.
              </p>
            </div>
            <div className={styles.modalActions}>
              <button className="nom-btn nom-btn-ghost" onClick={() => setConfirmDel(null)}>Cancelar</button>
              <button className={`nom-btn ${styles.btnDanger}`} onClick={handleDelete}>Eliminar</button>
            </div>
          </div>
        </Overlay>
      )}
    </div>
  );
}
