import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  Users, Plus, Search, Pencil, Trash2, ToggleLeft, ToggleRight,
  Loader2, X, CheckCircle2, AlertCircle, UserCheck, UserX,
  Calendar, ChevronRight,
} from 'lucide-react';
import { trabajadoresService, ciclosService } from '../services/trabajadores';
import styles from './Trabajadores.module.css';

const TIPO_LABELS = {
  planta:        'Planta',
  eventual:      'Eventual',
  subcontratado: 'Subcontratado',
};

const EMPTY_FORM = {
  nombre: '', apellido_paterno: '', apellido_materno: '',
  num_empleado: '', email: '', puesto: '', area: '', tipo_contratacion: 'planta',
};

export default function Trabajadores() {
  const [trabajadores, setTrabajadores] = useState([]);
  const [loading, setLoading]           = useState(true);
  const [search, setSearch]             = useState('');
  const [soloActivos, setSoloActivos]   = useState(false);
  const [modal, setModal]               = useState(null);   // null | 'create' | obj
  const [form, setForm]                 = useState(EMPTY_FORM);
  const [saving, setSaving]             = useState(false);
  const [formError, setFormError]       = useState('');
  const [confirmDel, setConfirmDel]     = useState(null);

  // Ciclos
  const [ciclos, setCiclos]             = useState([]);
  const [modalCiclo, setModalCiclo]     = useState(false);
  const [cicloForm, setCicloForm]       = useState({ anio: new Date().getFullYear(), fecha_inicio: '', notas: '' });
  const [savingCiclo, setSavingCiclo]   = useState(false);
  const [cicloError, setCicloError]     = useState('');

  const fetchCiclos = useCallback(async () => {
    try {
      const res = await ciclosService.list();
      setCiclos(res.data.data);
    } catch {}
  }, []);

  useEffect(() => { fetchCiclos(); }, [fetchCiclos]);

  const handleSaveCiclo = async (e) => {
    e.preventDefault();
    setSavingCiclo(true);
    setCicloError('');
    try {
      await ciclosService.create(cicloForm);
      setModalCiclo(false);
      setCicloForm({ anio: new Date().getFullYear(), fecha_inicio: '', notas: '' });
      fetchCiclos();
    } catch (err) {
      const errors = err.response?.data?.errors;
      setCicloError(errors ? Object.values(errors).flat().join(' ') : 'Error al crear el ciclo.');
    } finally {
      setSavingCiclo(false);
    }
  };

  const handleAvanzarCiclo = async (id) => {
    try {
      const res = await ciclosService.avanzarEstado(id);
      setCiclos(prev => prev.map(c => c.id === id ? res.data.data : c));
    } catch {}
  };

  const fetchTrabajadores = useCallback(async (q = '', activos = false) => {
    setLoading(true);
    try {
      const params = {};
      if (q)      params.q      = q;
      if (activos) params.activos = '1';
      const res = await trabajadoresService.list(params);
      setTrabajadores(res.data.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTrabajadores(); }, [fetchTrabajadores]);

  useEffect(() => {
    const t = setTimeout(() => fetchTrabajadores(search, soloActivos), 300);
    return () => clearTimeout(t);
  }, [search, soloActivos, fetchTrabajadores]);

  const openCreate = () => { setForm(EMPTY_FORM); setFormError(''); setModal('create'); };
  const openEdit   = (t)  => {
    setForm({
      nombre: t.nombre, apellido_paterno: t.apellido_paterno,
      apellido_materno: t.apellido_materno || '',
      num_empleado: t.num_empleado || '', email: t.email || '',
      puesto: t.puesto, area: t.area,
      tipo_contratacion: t.tipo_contratacion,
    });
    setFormError('');
    setModal(t);
  };
  const closeModal = () => { setModal(null); setFormError(''); };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormError('');
    try {
      if (modal === 'create') {
        await trabajadoresService.create(form);
      } else {
        await trabajadoresService.update(modal.id, form);
      }
      closeModal();
      fetchTrabajadores(search, soloActivos);
    } catch (err) {
      const errors = err.response?.data?.errors;
      if (errors) {
        setFormError(Object.values(errors).flat().join(' '));
      } else {
        setFormError('Ocurrió un error. Intenta de nuevo.');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (t) => {
    try {
      const res = await trabajadoresService.toggleActivo(t.id);
      setTrabajadores(prev => prev.map(w => w.id === t.id ? res.data.data : w));
    } catch {}
  };

  const handleDelete = async () => {
    if (!confirmDel) return;
    try {
      await trabajadoresService.delete(confirmDel.id);
      setTrabajadores(prev => prev.filter(w => w.id !== confirmDel.id));
    } finally {
      setConfirmDel(null);
    }
  };

  const isEditing = modal && modal !== 'create';
  const total     = trabajadores.length;
  const activos   = trabajadores.filter(w => w.activo).length;

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Trabajadores</h1>
          <p className={styles.subtitle}>Padrón de trabajadores del centro de trabajo</p>
        </div>
        <button className="nom-btn nom-btn-primary" onClick={openCreate}>
          <Plus size={16} strokeWidth={2.5} />
          Nuevo trabajador
        </button>
      </div>

      {/* Stats */}
      <div className={styles.statsRow}>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon}><Users size={18} strokeWidth={1.75} /></div>
          <div>
            <div className={styles.statNum}>{total}</div>
            <div className={styles.statLabel}>Total registrados</div>
          </div>
        </div>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon} style={{ background: 'var(--nom-success-subtle)', color: 'var(--nom-success)' }}>
            <UserCheck size={18} strokeWidth={1.75} />
          </div>
          <div>
            <div className={styles.statNum}>{activos}</div>
            <div className={styles.statLabel}>Activos</div>
          </div>
        </div>
        <div className={`${styles.statCard} nom-card`}>
          <div className={styles.statIcon} style={{ background: 'var(--nom-danger-subtle)', color: 'var(--nom-danger)' }}>
            <UserX size={18} strokeWidth={1.75} />
          </div>
          <div>
            <div className={styles.statNum}>{total - activos}</div>
            <div className={styles.statLabel}>Inactivos</div>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className={styles.toolbar}>
        <div className={styles.searchWrap}>
          <Search size={16} className={styles.searchIcon} />
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Buscar por nombre, área, puesto..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {search && (
            <button className={styles.searchClear} onClick={() => setSearch('')}>
              <X size={14} />
            </button>
          )}
        </div>
        <button
          className={`${styles.filterChip} ${soloActivos ? styles.filterChipActive : ''}`}
          onClick={() => setSoloActivos(v => !v)}
        >
          <UserCheck size={14} strokeWidth={2} />
          Solo activos
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className={styles.loadingWrap}>
          <Loader2 size={28} className="nom-spin" />
        </div>
      ) : trabajadores.length === 0 ? (
        <div className={styles.empty}>
          <Users size={40} strokeWidth={1.25} />
          <p>{search ? 'No se encontraron resultados.' : 'Aún no hay trabajadores registrados.'}</p>
          {!search && (
            <button className="nom-btn nom-btn-accent" onClick={openCreate}>
              <Plus size={15} />
              Registrar primer trabajador
            </button>
          )}
        </div>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead className={styles.thead}>
              <tr>
                <th>Nombre completo</th>
                <th>No. empleado</th>
                <th>Puesto</th>
                <th>Área</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody className={styles.tbody}>
              {trabajadores.map(t => (
                <tr key={t.id} className={!t.activo ? styles.trInactive : ''}>
                  <td>
                    <div className={styles.nameCell}>{t.nombre_completo}</div>
                    {t.email && <div className={styles.muteCell}>{t.email}</div>}
                  </td>
                  <td>
                    {t.num_empleado
                      ? <span className={styles.numCell}>{t.num_empleado}</span>
                      : <span className={styles.muteCell}>—</span>
                    }
                  </td>
                  <td>{t.puesto}</td>
                  <td className={styles.muteCell}>{t.area}</td>
                  <td>
                    <span className={styles.tipoChip}>{TIPO_LABELS[t.tipo_contratacion]}</span>
                  </td>
                  <td>
                    <span className={`${styles.statusChip} ${t.activo ? styles.chipActive : styles.chipInactive}`}>
                      {t.activo ? <CheckCircle2 size={11} /> : <AlertCircle size={11} />}
                      {t.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td>
                    <div className={styles.actionsCell}>
                      <button
                        className={styles.actionBtn}
                        onClick={() => handleToggle(t)}
                        title={t.activo ? 'Desactivar' : 'Activar'}
                      >
                        {t.activo
                          ? <ToggleRight size={16} strokeWidth={1.75} />
                          : <ToggleLeft  size={16} strokeWidth={1.75} />
                        }
                      </button>
                      <button className={styles.actionBtn} onClick={() => openEdit(t)} title="Editar">
                        <Pencil size={14} strokeWidth={1.75} />
                      </button>
                      <button
                        className={`${styles.actionBtn} ${styles.actionDanger}`}
                        onClick={() => setConfirmDel(t)}
                        title="Eliminar"
                      >
                        <Trash2 size={14} strokeWidth={1.75} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Ciclos NOM-035 */}
      <div className={styles.ciclosSection}>
        <div className={styles.ciclosHeader}>
          <div className={styles.ciclosHeadLeft}>
            <div className={styles.ciclosIcon}><Calendar size={16} strokeWidth={1.75} /></div>
            <div>
              <h2 className={styles.ciclosTitle}>Ciclos NOM-035</h2>
              <p className={styles.ciclosSub}>Periodos de evaluación por año</p>
            </div>
          </div>
          <button className="nom-btn nom-btn-ghost" onClick={() => { setCicloError(''); setModalCiclo(true); }}>
            <Plus size={14} strokeWidth={2.5} /> Nuevo ciclo
          </button>
        </div>

        {ciclos.length === 0 ? (
          <div className={styles.ciclosEmpty}>
            <Calendar size={22} strokeWidth={1.25} />
            <span>No hay ciclos creados aún</span>
          </div>
        ) : (
          <div className={styles.ciclosGrid}>
            {ciclos.map(c => (
              <div key={c.id} className={styles.cicloCard}>
                <div className={styles.cicloYear}>{c.anio}</div>
                <div className={styles.cicloMeta}>
                  <span className={`${styles.cicloEstado} ${styles[`estado_${c.estado}`]}`}>
                    {c.estado.replace('_', ' ')}
                  </span>
                  <span className={styles.cicloWorkers}>
                    <Users size={11} strokeWidth={2} /> {c.total_trabajadores} trabajadores
                  </span>
                </div>
                {c.fecha_inicio && (
                  <div className={styles.cicloDate}>Inicio: {c.fecha_inicio}</div>
                )}
                {c.estado !== 'cerrado' && (
                  <button className={styles.cicloAvanzar} onClick={() => handleAvanzarCiclo(c.id)}>
                    Avanzar estado <ChevronRight size={13} strokeWidth={2.5} />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal nuevo ciclo */}
      {modalCiclo && (
        <Overlay onClick={() => setModalCiclo(false)}>
          <div className={`${styles.modal} ${styles.modalSm} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Nuevo ciclo NOM-035</h2>
              <button className={styles.modalClose} onClick={() => setModalCiclo(false)}><X size={18} /></button>
            </div>
            <form onSubmit={handleSaveCiclo} className={styles.modalForm}>
              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>Año *</label>
                  <input className="nom-input" type="number" min="2020" max="2099"
                    value={cicloForm.anio}
                    onChange={e => setCicloForm(f => ({ ...f, anio: Number(e.target.value) }))} required />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Fecha de inicio *</label>
                  <input className="nom-input" type="date"
                    value={cicloForm.fecha_inicio}
                    onChange={e => setCicloForm(f => ({ ...f, fecha_inicio: e.target.value }))} required />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Notas</label>
                  <input className="nom-input" placeholder="Opcional"
                    value={cicloForm.notas}
                    onChange={e => setCicloForm(f => ({ ...f, notas: e.target.value }))} />
                </div>
              </div>
              {cicloError && <div className={styles.formError}>{cicloError}</div>}
              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={() => setModalCiclo(false)}>Cancelar</button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={savingCiclo}>
                  {savingCiclo ? <Loader2 size={15} className="nom-spin" /> : 'Crear ciclo'}
                </button>
              </div>
            </form>
          </div>
        </Overlay>
      )}

      {/* Modal crear / editar */}
      {modal && (
        <Overlay onClick={closeModal}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>{isEditing ? 'Editar trabajador' : 'Nuevo trabajador'}</h2>
              <button className={styles.modalClose} onClick={closeModal}><X size={18} /></button>
            </div>

            <form onSubmit={handleSave} className={styles.modalForm}>
              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>Nombre(s) *</label>
                  <input className="nom-input" placeholder="Juan" value={form.nombre}
                    onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} required />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Apellido paterno *</label>
                  <input className="nom-input" placeholder="García" value={form.apellido_paterno}
                    onChange={e => setForm(f => ({ ...f, apellido_paterno: e.target.value }))} required />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Apellido materno</label>
                  <input className="nom-input" placeholder="López" value={form.apellido_materno}
                    onChange={e => setForm(f => ({ ...f, apellido_materno: e.target.value }))} />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>No. de empleado</label>
                  <input className="nom-input" placeholder="EMP-001" value={form.num_empleado}
                    onChange={e => setForm(f => ({ ...f, num_empleado: e.target.value }))} />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Correo electrónico</label>
                  <input className="nom-input" type="email" placeholder="juan@empresa.com" value={form.email}
                    onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Puesto / cargo *</label>
                  <input className="nom-input" placeholder="Operador de producción" value={form.puesto}
                    onChange={e => setForm(f => ({ ...f, puesto: e.target.value }))} required />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Área / departamento *</label>
                  <input className="nom-input" placeholder="Manufactura" value={form.area}
                    onChange={e => setForm(f => ({ ...f, area: e.target.value }))} required />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Tipo de contratación *</label>
                  <select className="nom-input" value={form.tipo_contratacion}
                    onChange={e => setForm(f => ({ ...f, tipo_contratacion: e.target.value }))}>
                    <option value="planta">Planta</option>
                    <option value="eventual">Eventual</option>
                    <option value="subcontratado">Subcontratado</option>
                  </select>
                </div>
              </div>

              {formError && <div className={styles.formError}>{formError}</div>}

              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={15} className="nom-spin" /> : (isEditing ? 'Guardar cambios' : 'Registrar')}
                </button>
              </div>
            </form>
          </div>
        </Overlay>
      )}

      {/* Confirmar eliminación */}
      {confirmDel && (
        <Overlay onClick={() => setConfirmDel(null)}>
          <div className={`${styles.modal} ${styles.modalSm} nom-glass`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Eliminar trabajador</h2>
              <button className={styles.modalClose} onClick={() => setConfirmDel(null)}><X size={18} /></button>
            </div>
            <p className={styles.confirmText}>
              Esta acción es irreversible. Se eliminará a <strong>{confirmDel.nombre_completo}</strong> del padrón.
            </p>
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
