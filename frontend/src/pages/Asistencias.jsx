import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  CalendarCheck, Plus, FileDown, Loader2, X,
  ChevronDown, ChevronUp, Pencil, Trash2,
  Users, MapPin, Calendar, UserPlus, Check,
  AlertTriangle, ClipboardList,
} from 'lucide-react';
import { reunionesService, asistentesService } from '../services/asistencias';
import { ciclosService } from '../services/trabajadores';
import styles from './Asistencias.module.css';

const TIPO_OPTS = [
  { value: 'comite',       label: 'Reunion de Comite',         color: 'var(--nom-accent)',   bg: 'var(--nom-accent-subtle)' },
  { value: 'capacitacion', label: 'Sesion de Capacitacion',    color: 'var(--nom-success)',  bg: 'var(--nom-success-subtle)' },
  { value: 'seguimiento',  label: 'Reunion de Seguimiento',    color: '#d97706',             bg: 'rgba(245,158,11,0.10)' },
  { value: 'informativa',  label: 'Sesion Informativa',        color: '#2563eb',             bg: 'rgba(59,130,246,0.10)' },
  { value: 'otra',         label: 'Otra',                      color: 'var(--nom-text-muted)', bg: 'var(--nom-bg-subtle)' },
];

const TIPO_MAP = Object.fromEntries(TIPO_OPTS.map(t => [t.value, t]));

const EMPTY_REUNION   = { ciclo: '', tipo: 'comite', titulo: '', fecha: '', lugar: '', agenda: '', minuta: '' };
const EMPTY_ASISTENTE = { nombre: '', puesto: '' };

function TipoChip({ tipo }) {
  const c = TIPO_MAP[tipo] || TIPO_MAP.otra;
  return <span className={styles.chip} style={{ color: c.color, background: c.bg }}>{c.label}</span>;
}

export default function Asistencias() {
  const [ciclos, setCiclos]     = useState([]);
  const [cicloId, setCicloId]   = useState('');
  const [reuniones, setReuniones] = useState([]);
  const [meta, setMeta]         = useState({ count: 0, por_tipo: {} });
  const [loading, setLoading]   = useState(false);
  const [tipoFilter, setTipoFilter] = useState('');
  const [expanded, setExpanded] = useState(null);

  const [modal, setModal]           = useState(null); // null | 'reunion' | 'asistente' | 'del'
  const [editTarget, setEditTarget] = useState(null);
  const [targetReunion, setTargetReunion] = useState(null);
  const [confirmDel, setConfirmDel] = useState(null);

  const [rForm, setRForm]       = useState(EMPTY_REUNION);
  const [aForm, setAForm]       = useState(EMPTY_ASISTENTE);
  const [saving, setSaving]     = useState(false);
  const [formErr, setFormErr]   = useState('');

  useEffect(() => {
    ciclosService.list().then(res => {
      const data = res.data.data;
      setCiclos(data);
      if (data.length > 0) setCicloId(String(data[0].id));
    });
  }, []);

  const fetchReuniones = useCallback(async () => {
    if (!cicloId) return;
    setLoading(true);
    try {
      const params = { ciclo_id: cicloId };
      if (tipoFilter) params.tipo = tipoFilter;
      const res = await reunionesService.list(params);
      setReuniones(res.data.data);
      setMeta(res.data.meta || { count: 0, por_tipo: {} });
    } finally {
      setLoading(false);
    }
  }, [cicloId, tipoFilter]);

  useEffect(() => { fetchReuniones(); }, [fetchReuniones]);

  const openCreateReunion = () => {
    setEditTarget(null);
    setRForm({ ...EMPTY_REUNION, ciclo: cicloId });
    setFormErr('');
    setModal('reunion');
  };

  const openEditReunion = (r) => {
    setEditTarget(r);
    setRForm({ ciclo: String(r.ciclo), tipo: r.tipo, titulo: r.titulo, fecha: r.fecha, lugar: r.lugar || '', agenda: r.agenda || '', minuta: r.minuta || '' });
    setFormErr('');
    setModal('reunion');
  };

  const handleSaveReunion = async (e) => {
    e.preventDefault();
    setFormErr('');
    setSaving(true);
    try {
      if (editTarget) {
        await reunionesService.update(editTarget.id, rForm);
      } else {
        await reunionesService.create(rForm);
      }
      setModal(null);
      fetchReuniones();
    } catch (err) {
      const d = err.response?.data;
      setFormErr(d?.errors ? Object.values(d.errors).flat().join(' ') : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  };

  const openAddAsistente = (reunion) => {
    setTargetReunion(reunion);
    setAForm(EMPTY_ASISTENTE);
    setFormErr('');
    setModal('asistente');
  };

  const handleSaveAsistente = async (e) => {
    e.preventDefault();
    setFormErr('');
    setSaving(true);
    try {
      await asistentesService.create({ ...aForm, reunion: targetReunion.id });
      setModal(null);
      fetchReuniones();
    } catch (err) {
      const d = err.response?.data;
      setFormErr(d?.errors ? Object.values(d.errors).flat().join(' ') : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  };

  const toggleFirma = async (asistente) => {
    await asistentesService.update(asistente.id, { firma_recibida: !asistente.firma_recibida });
    fetchReuniones();
  };

  const handleDeleteReunion = async () => {
    if (!confirmDel) return;
    setSaving(true);
    try {
      await reunionesService.delete(confirmDel.id);
      setModal(null); setConfirmDel(null);
      if (expanded === confirmDel.id) setExpanded(null);
      fetchReuniones();
    } finally { setSaving(false); }
  };

  const handleDeleteAsistente = async () => {
    if (!confirmDel) return;
    setSaving(true);
    try {
      await asistentesService.delete(confirmDel.id);
      setModal(null); setConfirmDel(null);
      fetchReuniones();
    } finally { setSaving(false); }
  };

  const handleDescargarActa = async (reunion) => {
    const token = localStorage.getItem('access_token');
    const base  = import.meta.env.VITE_API_URL || '/api/v1';
    const res   = await fetch(`${base}/reuniones/${reunion.id}/acta/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('pdf')) {
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href = url; a.download = `acta_reunion_${reunion.fecha}.pdf`;
      a.click(); URL.revokeObjectURL(url);
    } else {
      const html = await res.text();
      const w = window.open('', '_blank');
      w.document.write(html); w.document.close();
    }
  };

  const activeTipos = TIPO_OPTS.filter(t => (meta.por_tipo || {})[t.value] > 0);

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Asistencias y Minutas</h1>
          <p className={styles.subtitle}>Registro de reuniones, listas de asistencia y minutas NOM-035</p>
        </div>
        <div className={styles.headerActions}>
          <div className={styles.selectWrap}>
            <select
              className={styles.select}
              value={cicloId}
              onChange={e => { setCicloId(e.target.value); setTipoFilter(''); }}
            >
              {ciclos.map(c => <option key={c.id} value={c.id}>{c.anio}</option>)}
            </select>
            <ChevronDown size={14} className={styles.selectIcon} />
          </div>
          <button className="nom-btn-pill nom-btn-primary" onClick={openCreateReunion} disabled={!cicloId}>
            <Plus size={15} />
            Nueva reunion
          </button>
        </div>
      </div>

      {loading && <div className={styles.loadingWrap}><Loader2 size={24} className="nom-spin" /></div>}

      {!loading && !cicloId && (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}><CalendarCheck size={28} /></div>
          <p className={styles.emptyTitle}>Sin ciclos</p>
          <p className={styles.emptyText}>Crea un ciclo NOM-035 para registrar reuniones.</p>
        </div>
      )}

      {!loading && cicloId && (
        <div className={styles.content}>
          {/* KPIs */}
          <div className={styles.kpiRow}>
            <div
              className={`${styles.kpiCard} ${!tipoFilter ? styles.kpiCardActive : ''}`}
              style={{ '--kpi-color': 'var(--nom-accent)' }}
              onClick={() => setTipoFilter('')}
            >
              <span className={styles.kpiNum}>{meta.count ?? reuniones.length}</span>
              <span className={styles.kpiLabel}>Reuniones</span>
            </div>
            {activeTipos.map(t => (
              <div
                key={t.value}
                className={`${styles.kpiCard} ${tipoFilter === t.value ? styles.kpiCardActive : ''}`}
                style={{ '--kpi-color': t.color }}
                onClick={() => setTipoFilter(tipoFilter === t.value ? '' : t.value)}
              >
                <span className={styles.kpiNum} style={{ color: t.color }}>{meta.por_tipo[t.value]}</span>
                <span className={styles.kpiLabel}>{t.label}</span>
              </div>
            ))}
          </div>

          {/* Section header */}
          <div className={styles.sectionHeader}>
            <div className={styles.sectionTitle}>
              <CalendarCheck size={18} />
              Reuniones registradas
            </div>
            {tipoFilter && (
              <button className={styles.clearFilter} onClick={() => setTipoFilter('')}>
                <X size={11} /> Limpiar filtro
              </button>
            )}
          </div>

          {/* Reunion list */}
          {reuniones.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}><CalendarCheck size={28} /></div>
              <p className={styles.emptyTitle}>Sin reuniones</p>
              <p className={styles.emptyText}>
                {tipoFilter ? 'No hay reuniones del tipo seleccionado.' : 'Registra la primera reunion de este ciclo.'}
              </p>
            </div>
          ) : (
            <div className={styles.reunionList}>
              {reuniones.map(r => {
                const isOpen = expanded === r.id;
                const tipoCfg = TIPO_MAP[r.tipo] || TIPO_MAP.otra;
                return (
                  <div key={r.id} className={styles.reunionCard}>
                    <div className={styles.reunionHeader} onClick={() => setExpanded(isOpen ? null : r.id)}>
                      <div className={styles.reunionIcon} style={{ background: tipoCfg.bg }}>
                        <CalendarCheck size={18} color={tipoCfg.color} />
                      </div>
                      <div className={styles.reunionInfo}>
                        <div className={styles.reunionTitle}>{r.titulo}</div>
                        <div className={styles.reunionMeta}>
                          <TipoChip tipo={r.tipo} />
                          <span className={styles.reunionMetaItem}><Calendar size={11} />{r.fecha}</span>
                          {r.lugar && <span className={styles.reunionMetaItem}><MapPin size={11} />{r.lugar}</span>}
                          <span className={styles.reunionMetaItem}><Users size={11} />{r.num_asistentes} asistentes</span>
                        </div>
                      </div>
                      <div className={styles.reunionActions} onClick={e => e.stopPropagation()}>
                        <button className={styles.rowBtn} onClick={() => openEditReunion(r)} title="Editar">
                          <Pencil size={14} />
                        </button>
                        <button
                          className={`${styles.rowBtn} ${styles.rowBtnDanger}`}
                          onClick={() => { setConfirmDel({ id: r.id, label: r.titulo, type: 'reunion' }); setModal('del'); }}
                          title="Eliminar"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                      <ChevronDown
                        size={16}
                        className={`${styles.expandIcon} ${isOpen ? styles.expandIconOpen : ''}`}
                      />
                    </div>

                    {isOpen && (
                      <div className={styles.reunionDetail}>
                        {r.agenda && (
                          <div className={styles.detailSection}>
                            <div className={styles.detailLabel}>Agenda</div>
                            <div className={styles.detailText}>{r.agenda}</div>
                          </div>
                        )}
                        {r.minuta && (
                          <div className={styles.detailSection}>
                            <div className={styles.detailLabel}>Minuta / Acuerdos</div>
                            <div className={styles.detailText}>{r.minuta}</div>
                          </div>
                        )}

                        {/* Asistentes */}
                        <div>
                          <div className={styles.asistentesHeader}>
                            <span className={styles.asistentesTitle}>
                              Lista de asistencia ({r.asistentes?.length ?? 0})
                            </span>
                            <button
                              className="nom-btn-pill nom-btn-ghost"
                              style={{ padding: '5px 12px', fontSize: 'var(--nom-text-xs)' }}
                              onClick={() => openAddAsistente(r)}
                            >
                              <UserPlus size={12} /> Agregar
                            </button>
                          </div>
                          {r.asistentes?.length > 0 ? (
                            r.asistentes.map(a => (
                              <div key={a.id} className={styles.asistenteRow}>
                                <div className={styles.asistenteInfo}>
                                  <div className={styles.asistenteNombre}>{a.nombre}</div>
                                  {a.puesto && <div className={styles.asistentePuesto}>{a.puesto}</div>}
                                </div>
                                <button
                                  className={`${styles.firmaToggle} ${a.firma_recibida ? styles.firmaToggleOn : ''}`}
                                  onClick={() => toggleFirma(a)}
                                  title="Marcar firma"
                                >
                                  <Check size={11} />
                                  {a.firma_recibida ? 'Firmado' : 'Pendiente'}
                                </button>
                                <button
                                  className={`${styles.rowBtn} ${styles.rowBtnDanger}`}
                                  onClick={() => { setConfirmDel({ id: a.id, label: a.nombre, type: 'asistente' }); setModal('del'); }}
                                  title="Eliminar asistente"
                                >
                                  <Trash2 size={12} />
                                </button>
                              </div>
                            ))
                          ) : (
                            <p style={{ fontSize: 'var(--nom-text-xs)', color: 'var(--nom-text-muted)', padding: '8px 0' }}>
                              Sin asistentes registrados.
                            </p>
                          )}
                        </div>

                        <div className={styles.detailActionsRow}>
                          <button className="nom-btn-pill nom-btn-ghost" onClick={() => handleDescargarActa(r)}>
                            <FileDown size={14} />
                            Descargar acta
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Reunion form modal */}
      {modal === 'reunion' && (
        <Overlay onClick={e => e.target === e.currentTarget && setModal(null)}>
          <div className={`nom-glass ${styles.modal} ${styles.modalLg}`}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>{editTarget ? 'Editar reunion' : 'Nueva reunion'}</h2>
              <button className={styles.modalClose} onClick={() => setModal(null)}><X size={16} /></button>
            </div>
            <form className={styles.modalForm} onSubmit={handleSaveReunion}>
              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>Tipo *</label>
                  <select className="nom-input" value={rForm.tipo} onChange={e => setRForm(f => ({ ...f, tipo: e.target.value }))} required>
                    {TIPO_OPTS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Fecha *</label>
                  <input type="date" className="nom-input" value={rForm.fecha} onChange={e => setRForm(f => ({ ...f, fecha: e.target.value }))} required />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Titulo *</label>
                  <input type="text" className="nom-input" placeholder="Ej. Primera reunion de comite NOM-035" value={rForm.titulo} onChange={e => setRForm(f => ({ ...f, titulo: e.target.value }))} required />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Lugar</label>
                  <input type="text" className="nom-input" placeholder="Sala de juntas, planta, etc." value={rForm.lugar} onChange={e => setRForm(f => ({ ...f, lugar: e.target.value }))} />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Agenda</label>
                  <textarea className="nom-input" rows={3} placeholder="Puntos a tratar en la reunion..." value={rForm.agenda} onChange={e => setRForm(f => ({ ...f, agenda: e.target.value }))} />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Minuta / Acuerdos</label>
                  <textarea className="nom-input" rows={4} placeholder="Acuerdos, compromisos y seguimiento..." value={rForm.minuta} onChange={e => setRForm(f => ({ ...f, minuta: e.target.value }))} />
                </div>
              </div>
              {formErr && <p className={styles.formError}>{formErr}</p>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn-pill nom-btn-ghost" onClick={() => setModal(null)}>Cancelar</button>
                <button type="submit" className="nom-btn-pill nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  {editTarget ? 'Guardar cambios' : 'Crear reunion'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Asistente form modal */}
      {modal === 'asistente' && (
        <Overlay onClick={e => e.target === e.currentTarget && setModal(null)}>
          <div className={`nom-glass ${styles.modal} ${styles.modalSm}`}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Agregar asistente</h2>
              <button className={styles.modalClose} onClick={() => setModal(null)}><X size={16} /></button>
            </div>
            <form className={styles.modalForm} onSubmit={handleSaveAsistente}>
              <div className={styles.field}>
                <label className={styles.label}>Nombre *</label>
                <input type="text" className="nom-input" placeholder="Nombre completo" value={aForm.nombre} onChange={e => setAForm(f => ({ ...f, nombre: e.target.value }))} required />
              </div>
              <div className={styles.field}>
                <label className={styles.label}>Puesto</label>
                <input type="text" className="nom-input" placeholder="Cargo o area" value={aForm.puesto} onChange={e => setAForm(f => ({ ...f, puesto: e.target.value }))} />
              </div>
              {formErr && <p className={styles.formError}>{formErr}</p>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn-pill nom-btn-ghost" onClick={() => setModal(null)}>Cancelar</button>
                <button type="submit" className="nom-btn-pill nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  Agregar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirm delete modal */}
      {modal === 'del' && confirmDel && (
        <Overlay onClick={e => e.target === e.currentTarget && setModal(null)}>
          <div className={`nom-glass ${styles.modal} ${styles.modalSm}`}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {confirmDel.type === 'reunion' ? 'Eliminar reunion' : 'Eliminar asistente'}
              </h2>
              <button className={styles.modalClose} onClick={() => setModal(null)}><X size={16} /></button>
            </div>
            <div className={styles.confirmWrap}>
              <AlertTriangle size={20} className={styles.confirmIcon} />
              <p className={styles.confirmText}>
                Se eliminara permanentemente{' '}
                <strong>&ldquo;{confirmDel.label}&rdquo;</strong>.
                {confirmDel.type === 'reunion' && ' Tambien se eliminaran todos sus asistentes.'}
              </p>
            </div>
            <div className={styles.modalActions}>
              <button className="nom-btn-pill nom-btn-ghost" onClick={() => setModal(null)}>Cancelar</button>
              <button
                className={styles.btnDanger}
                onClick={confirmDel.type === 'reunion' ? handleDeleteReunion : handleDeleteAsistente}
                disabled={saving}
              >
                {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
