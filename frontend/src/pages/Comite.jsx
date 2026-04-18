import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  Users, Plus, FileDown, Loader2, X, ChevronDown,
  Pencil, Trash2, ChevronRight, ChevronUp,
  GraduationCap, UserPlus, AlertTriangle, ShieldCheck,
} from 'lucide-react';
import { comiteService, miembrosService, dc3Service } from '../services/comite';
import { ciclosService } from '../services/trabajadores';
import styles from './Comite.module.css';

const TIPO_CFG = {
  presidente: { label: 'Presidente', color: 'var(--nom-success)',      bg: 'var(--nom-success-subtle)' },
  secretario: { label: 'Secretario', color: 'var(--nom-riesgo-muy-alto, #7c3aed)', bg: 'rgba(124,58,237,0.10)' },
  vocal:      { label: 'Vocal',      color: 'var(--nom-accent)',        bg: 'var(--nom-accent-subtle)' },
};

const EMPTY_COMITE  = { ciclo: '', fecha_constitucion: '', numero_acta: '', observaciones: '' };
const EMPTY_MIEMBRO = { nombre: '', puesto: '', tipo: 'vocal', email: '', telefono: '' };
const EMPTY_DC3     = { tipo_capacitacion: '', fecha: '', horas: 8, instructor: '', numero_dc3: '' };

function TipoChip({ tipo }) {
  const c = TIPO_CFG[tipo] || TIPO_CFG.vocal;
  return (
    <span className={styles.tipoChip} style={{ color: c.color, background: c.bg }}>
      {c.label}
    </span>
  );
}

export default function Comite() {
  const [ciclos, setCiclos]   = useState([]);
  const [cicloId, setCicloId] = useState('');
  const [comite, setComite]   = useState(null);
  const [loading, setLoading] = useState(false);

  // Modals: null | 'comite' | 'miembro' | 'dc3'
  const [modal, setModal]         = useState(null);
  const [editTarget, setEditTarget] = useState(null);
  const [dc3Miembro, setDc3Miembro] = useState(null);

  const [form, setForm]       = useState(EMPTY_COMITE);
  const [mForm, setMForm]     = useState(EMPTY_MIEMBRO);
  const [dForm, setDForm]     = useState(EMPTY_DC3);
  const [saving, setSaving]   = useState(false);
  const [formErr, setFormErr] = useState('');

  const [expanded, setExpanded] = useState(null); // miembro id
  const [confirmDel, setConfirmDel] = useState(null); // { type: 'miembro'|'dc3', id, label }

  // Load ciclos
  useEffect(() => {
    ciclosService.list().then(res => {
      const data = res.data.data;
      setCiclos(data);
      if (data.length > 0) setCicloId(String(data[0].id));
    });
  }, []);

  const fetchComite = useCallback(async () => {
    if (!cicloId) return;
    setLoading(true);
    try {
      const res = await comiteService.list({ ciclo_id: cicloId });
      setComite(res.data.data[0] || null);
    } finally {
      setLoading(false);
    }
  }, [cicloId]);

  useEffect(() => { fetchComite(); }, [fetchComite]);

  // -- Open modals --
  const openCreateComite = () => {
    setForm({ ...EMPTY_COMITE, ciclo: cicloId });
    setFormErr('');
    setEditTarget(null);
    setModal('comite');
  };

  const openEditComite = () => {
    setForm({
      ciclo:              String(comite.ciclo),
      fecha_constitucion: comite.fecha_constitucion,
      numero_acta:        comite.numero_acta || '',
      observaciones:      comite.observaciones || '',
    });
    setFormErr('');
    setEditTarget(comite);
    setModal('comite');
  };

  const openAddMiembro = () => {
    setMForm(EMPTY_MIEMBRO);
    setFormErr('');
    setEditTarget(null);
    setModal('miembro');
  };

  const openEditMiembro = (m) => {
    setMForm({
      nombre:   m.nombre,
      puesto:   m.puesto,
      tipo:     m.tipo,
      email:    m.email || '',
      telefono: m.telefono || '',
    });
    setFormErr('');
    setEditTarget(m);
    setModal('miembro');
  };

  const openAddDC3 = (m) => {
    setDForm(EMPTY_DC3);
    setFormErr('');
    setDc3Miembro(m);
    setModal('dc3');
  };

  const closeModal = () => {
    setModal(null);
    setEditTarget(null);
    setDc3Miembro(null);
    setFormErr('');
  };

  // -- Save handlers --
  const handleSaveComite = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormErr('');
    try {
      const payload = { ...form, ciclo: Number(form.ciclo) };
      if (editTarget) {
        await comiteService.update(editTarget.id, payload);
      } else {
        await comiteService.create(payload);
      }
      closeModal();
      fetchComite();
    } catch (err) {
      const errors = err.response?.data?.errors;
      setFormErr(errors ? Object.values(errors).flat().join(' ') : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveMiembro = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormErr('');
    try {
      const payload = { ...mForm, comite: comite.id };
      if (editTarget) {
        await miembrosService.update(editTarget.id, payload);
      } else {
        await miembrosService.create(payload);
      }
      closeModal();
      fetchComite();
    } catch (err) {
      const errors = err.response?.data?.errors;
      setFormErr(errors ? Object.values(errors).flat().join(' ') : 'Error al guardar.');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveDC3 = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormErr('');
    try {
      await dc3Service.create({ ...dForm, miembro: dc3Miembro.id, horas: Number(dForm.horas) });
      closeModal();
      fetchComite();
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
      if (confirmDel.type === 'miembro') {
        await miembrosService.delete(confirmDel.id);
      } else {
        await dc3Service.delete(confirmDel.id);
      }
      fetchComite();
    } finally {
      setConfirmDel(null);
    }
  };

  const handleDescargarActa = () => {
    if (!comite) return;
    const token = localStorage.getItem('access_token') || '';
    const url   = `/api/v1/comite/${comite.id}/acta/`;
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
          const a = document.createElement('a');
          a.href = URL.createObjectURL(blob);
          a.download = cd.match(/filename="?([^";]+)"?/)?.[1] || `acta_comite_${cicloId}.pdf`;
          a.click();
          URL.revokeObjectURL(a.href);
        });
      })
      .catch(() => alert('Error al generar el acta.'));
  };

  const miembros = comite?.miembros || [];

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Comite NOM-035</h1>
          <p className={styles.subtitle}>Constitucion y gestion del comite de seguridad y salud en el trabajo</p>
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
          {comite && (
            <button
              className="nom-btn nom-btn-ghost"
              onClick={handleDescargarActa}
              title="Descargar acta de constitucion en PDF"
            >
              <FileDown size={15} strokeWidth={2} />
              Descargar Acta
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className={styles.loadingWrap}><Loader2 size={28} className="nom-spin" /></div>
      ) : !comite ? (
        /* ---- Empty state ---- */
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>
            <Users size={36} strokeWidth={1.25} />
          </div>
          <h2 className={styles.emptyTitle}>No hay comite constituido</h2>
          <p className={styles.emptyText}>
            Constituye el comite de seguridad y salud en el trabajo para el ciclo {ciclos.find(c => String(c.id) === cicloId)?.anio || cicloId}.
          </p>
          <button className="nom-btn nom-btn-primary" onClick={openCreateComite} disabled={!cicloId}>
            <Plus size={15} />
            Constituir comite
          </button>
        </div>
      ) : (
        /* ---- Content ---- */
        <div className={styles.content}>
          {/* Comite info card */}
          <div className={`${styles.infoCard} nom-card`}>
            <div className={styles.infoCardLeft}>
              <div className={styles.infoCardIcon}>
                <ShieldCheck size={20} strokeWidth={1.75} />
              </div>
              <div>
                <div className={styles.infoCardTitle}>
                  Comite de Seguridad y Salud en el Trabajo
                </div>
                <div className={styles.infoCardMeta}>
                  <span>Constituido el {new Date(comite.fecha_constitucion).toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                  {comite.numero_acta && <span className={styles.dot}>·</span>}
                  {comite.numero_acta && <span>Acta {comite.numero_acta}</span>}
                  <span className={styles.dot}>·</span>
                  <span>{comite.total_miembros} miembro{comite.total_miembros !== 1 ? 's' : ''}</span>
                </div>
                {comite.observaciones && (
                  <div className={styles.infoCardObs}>{comite.observaciones}</div>
                )}
              </div>
            </div>
            <button className={styles.editInfoBtn} onClick={openEditComite}>
              <Pencil size={14} strokeWidth={1.75} />
              Editar
            </button>
          </div>

          {/* Members section */}
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Integrantes del comite</h2>
            <button className="nom-btn nom-btn-primary" onClick={openAddMiembro}>
              <UserPlus size={15} />
              Agregar miembro
            </button>
          </div>

          {miembros.length === 0 ? (
            <div className={styles.emptyMembers}>
              <Users size={32} strokeWidth={1.25} />
              <p>Aun no hay miembros registrados. Agrega el primer integrante.</p>
            </div>
          ) : (
            <div className={styles.membersList}>
              {miembros.map(m => (
                <div key={m.id} className={`${styles.memberCard} nom-card ${!m.activo ? styles.memberInactive : ''}`}>
                  {/* Member row */}
                  <div className={styles.memberRow}>
                    <div className={styles.memberAvatar}>
                      {m.nombre[0].toUpperCase()}
                    </div>
                    <div className={styles.memberInfo}>
                      <div className={styles.memberName}>{m.nombre}</div>
                      <div className={styles.memberPuesto}>{m.puesto}</div>
                    </div>
                    <TipoChip tipo={m.tipo} />
                    <div className={styles.memberStats}>
                      <GraduationCap size={13} strokeWidth={2} />
                      <span>{m.total_dc3} DC3</span>
                    </div>
                    <div className={styles.memberActions}>
                      <button
                        className={styles.actionBtn}
                        onClick={() => openAddDC3(m)}
                        title="Agregar capacitacion DC3"
                      >
                        <GraduationCap size={14} strokeWidth={1.75} />
                      </button>
                      <button
                        className={styles.actionBtn}
                        onClick={() => openEditMiembro(m)}
                        title="Editar miembro"
                      >
                        <Pencil size={14} strokeWidth={1.75} />
                      </button>
                      <button
                        className={`${styles.actionBtn} ${styles.actionDanger}`}
                        onClick={() => setConfirmDel({ type: 'miembro', id: m.id, label: m.nombre })}
                        title="Eliminar miembro"
                      >
                        <Trash2 size={14} strokeWidth={1.75} />
                      </button>
                      <button
                        className={styles.expandBtn}
                        onClick={() => setExpanded(expanded === m.id ? null : m.id)}
                        title={expanded === m.id ? 'Ocultar DC3' : 'Ver capacitaciones DC3'}
                      >
                        {expanded === m.id
                          ? <ChevronUp size={14} strokeWidth={2} />
                          : <ChevronRight size={14} strokeWidth={2} />
                        }
                      </button>
                    </div>
                  </div>

                  {/* DC3 accordion */}
                  {expanded === m.id && (
                    <div className={styles.dc3Section}>
                      <div className={styles.dc3Header}>
                        <GraduationCap size={13} />
                        Constancias DC3
                      </div>
                      {m.capacitaciones.length === 0 ? (
                        <p className={styles.dc3Empty}>Sin capacitaciones registradas.</p>
                      ) : (
                        <div className={styles.dc3List}>
                          {m.capacitaciones.map(dc3 => (
                            <div key={dc3.id} className={styles.dc3Row}>
                              <div className={styles.dc3Info}>
                                <span className={styles.dc3Tipo}>{dc3.tipo_capacitacion}</span>
                                <span className={styles.dc3Meta}>
                                  {new Date(dc3.fecha).toLocaleDateString('es-MX')}
                                  {' · '}{dc3.horas}h
                                  {dc3.instructor && ` · ${dc3.instructor}`}
                                  {dc3.numero_dc3 && ` · #${dc3.numero_dc3}`}
                                </span>
                              </div>
                              <button
                                className={`${styles.actionBtn} ${styles.actionDanger}`}
                                onClick={() => setConfirmDel({ type: 'dc3', id: dc3.id, label: dc3.tipo_capacitacion })}
                                title="Eliminar DC3"
                              >
                                <Trash2 size={13} strokeWidth={1.75} />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                      <button
                        className={styles.addDc3Btn}
                        onClick={() => openAddDC3(m)}
                      >
                        <Plus size={13} /> Agregar DC3
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ---- Modal Comite ---- */}
      {modal === 'comite' && (
        <Overlay onClick={closeModal}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {editTarget ? 'Editar comite' : 'Constituir comite'}
              </h2>
              <button className={styles.modalClose} onClick={closeModal}><X size={18} /></button>
            </div>
            <form onSubmit={handleSaveComite} className={styles.modalForm}>
              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>Fecha de constitucion *</label>
                  <input
                    className="nom-input"
                    type="date"
                    value={form.fecha_constitucion}
                    onChange={e => setForm(f => ({ ...f, fecha_constitucion: e.target.value }))}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Numero de acta</label>
                  <input
                    className="nom-input"
                    placeholder="Ej. ACT-001-2025"
                    value={form.numero_acta}
                    onChange={e => setForm(f => ({ ...f, numero_acta: e.target.value }))}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Observaciones</label>
                  <textarea
                    className="nom-input"
                    placeholder="Notas o consideraciones adicionales..."
                    value={form.observaciones}
                    onChange={e => setForm(f => ({ ...f, observaciones: e.target.value }))}
                    rows={3}
                    style={{ resize: 'vertical' }}
                  />
                </div>
              </div>
              {formErr && <div className={styles.formError}>{formErr}</div>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  {saving ? 'Guardando...' : (editTarget ? 'Guardar cambios' : 'Constituir comite')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---- Modal Miembro ---- */}
      {modal === 'miembro' && (
        <Overlay onClick={closeModal}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {editTarget ? 'Editar miembro' : 'Agregar miembro'}
              </h2>
              <button className={styles.modalClose} onClick={closeModal}><X size={18} /></button>
            </div>
            <form onSubmit={handleSaveMiembro} className={styles.modalForm}>
              <div className={styles.formGrid}>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Nombre completo *</label>
                  <input
                    className="nom-input"
                    placeholder="Nombre del integrante"
                    value={mForm.nombre}
                    onChange={e => setMForm(f => ({ ...f, nombre: e.target.value }))}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Puesto *</label>
                  <input
                    className="nom-input"
                    placeholder="Puesto en la empresa"
                    value={mForm.puesto}
                    onChange={e => setMForm(f => ({ ...f, puesto: e.target.value }))}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Rol en el comite *</label>
                  <div className={styles.selectWrap} style={{ position: 'relative', maxWidth: '100%' }}>
                    <ChevronDown size={14} className={styles.selectIcon} />
                    <select
                      className={styles.select}
                      style={{ width: '100%', paddingLeft: '14px' }}
                      value={mForm.tipo}
                      onChange={e => setMForm(f => ({ ...f, tipo: e.target.value }))}
                    >
                      <option value="presidente">Presidente</option>
                      <option value="secretario">Secretario</option>
                      <option value="vocal">Vocal</option>
                    </select>
                  </div>
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Correo electronico</label>
                  <input
                    className="nom-input"
                    type="email"
                    placeholder="correo@empresa.com"
                    value={mForm.email}
                    onChange={e => setMForm(f => ({ ...f, email: e.target.value }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Telefono</label>
                  <input
                    className="nom-input"
                    placeholder="55 1234 5678"
                    value={mForm.telefono}
                    onChange={e => setMForm(f => ({ ...f, telefono: e.target.value }))}
                  />
                </div>
              </div>
              {formErr && <div className={styles.formError}>{formErr}</div>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  {saving ? 'Guardando...' : (editTarget ? 'Guardar cambios' : 'Agregar miembro')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---- Modal DC3 ---- */}
      {modal === 'dc3' && (
        <Overlay onClick={closeModal}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div>
                <h2 className={styles.modalTitle}>Agregar capacitacion DC3</h2>
                {dc3Miembro && (
                  <p className={styles.modalSub}>{dc3Miembro.nombre}</p>
                )}
              </div>
              <button className={styles.modalClose} onClick={closeModal}><X size={18} /></button>
            </div>
            <form onSubmit={handleSaveDC3} className={styles.modalForm}>
              <div className={styles.formGrid}>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Tipo de capacitacion *</label>
                  <input
                    className="nom-input"
                    placeholder="Ej. Factores de riesgo psicosocial NOM-035"
                    value={dForm.tipo_capacitacion}
                    onChange={e => setDForm(f => ({ ...f, tipo_capacitacion: e.target.value }))}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Fecha *</label>
                  <input
                    className="nom-input"
                    type="date"
                    value={dForm.fecha}
                    onChange={e => setDForm(f => ({ ...f, fecha: e.target.value }))}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Horas</label>
                  <input
                    className="nom-input"
                    type="number"
                    min="1"
                    value={dForm.horas}
                    onChange={e => setDForm(f => ({ ...f, horas: e.target.value }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Instructor</label>
                  <input
                    className="nom-input"
                    placeholder="Nombre del instructor"
                    value={dForm.instructor}
                    onChange={e => setDForm(f => ({ ...f, instructor: e.target.value }))}
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Numero de DC3</label>
                  <input
                    className="nom-input"
                    placeholder="Folio del documento"
                    value={dForm.numero_dc3}
                    onChange={e => setDForm(f => ({ ...f, numero_dc3: e.target.value }))}
                  />
                </div>
              </div>
              {formErr && <div className={styles.formError}>{formErr}</div>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={14} className="nom-spin" /> : null}
                  {saving ? 'Guardando...' : 'Registrar DC3'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ---- Confirm delete ---- */}
      {confirmDel && (
        <Overlay onClick={() => setConfirmDel(null)}>
          <div className={`${styles.modal} ${styles.modalSm} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Confirmar eliminacion</h2>
              <button className={styles.modalClose} onClick={() => setConfirmDel(null)}>
                <X size={18} />
              </button>
            </div>
            <div className={styles.confirmWrap}>
              <AlertTriangle size={32} className={styles.confirmIcon} />
              <p className={styles.confirmText}>
                Se eliminara <strong>{confirmDel.label}</strong>. Esta accion no se puede deshacer.
              </p>
            </div>
            <div className={styles.modalActions}>
              <button className="nom-btn nom-btn-ghost" onClick={() => setConfirmDel(null)}>Cancelar</button>
              <button className={`nom-btn ${styles.btnDanger}`} onClick={handleDelete}>Eliminar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
