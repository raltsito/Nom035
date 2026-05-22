import Overlay from '../components/ui/Overlay';
import { useState, useEffect, useCallback } from 'react';
import {
  Users, Plus, Search, Pencil, Trash2, ToggleLeft, ToggleRight,
  Loader2, X, CheckCircle2, AlertCircle, UserCheck, UserX,
  Calendar, ChevronRight, Upload, FileSpreadsheet, CheckCheck, Eye,
} from 'lucide-react';
import { trabajadoresService, ciclosService } from '../services/trabajadores';
import styles from './Trabajadores.module.css';

const SEXO_LABELS          = { M: 'Masculino', F: 'Femenino' };
const ESTADO_CIVIL_LABELS  = { soltero: 'Soltero', casado: 'Casado', union_libre: 'Unión libre', divorciado: 'Divorciado', viudo: 'Viudo', otro: 'Otro' };
const NIVEL_LABELS         = { primaria: 'Primaria', secundaria: 'Secundaria', bachillerato: 'Bachillerato / Preparatoria', tecnico: 'Técnico', licenciatura: 'Licenciatura', ingenieria: 'Ingeniería', posgrado: 'Posgrado', otro: 'Otro' };
const PERSONAL_LABELS      = { sindicalizado: 'Sindicalizado / Directo', confianza: 'Confianza / Indirecto', salary: 'Salary / Administrativo', otro: 'Otro' };
const JORNADA_LABELS       = { diurno: 'Diurno', mixto: 'Mixto', nocturno: 'Nocturno' };
const CONTRAT_LABELS       = { planta: 'Planta', eventual: 'Eventual', subcontratado: 'Subcontratado' };

const DETALLE_SECCIONES = [
  {
    titulo: 'Identificación',
    campos: [
      { key: 'num_empleado',   label: 'No. empleado' },
      { key: 'email',          label: 'Correo electrónico' },
    ],
  },
  {
    titulo: 'Posición',
    campos: [
      { key: 'puesto',             label: 'Puesto / Profesión' },
      { key: 'area',               label: 'Departamento / Área' },
      { key: 'tipo_puesto',        label: 'Tipo de puesto' },
      { key: 'tipo_contratacion',  label: 'Tipo de contratación',  map: CONTRAT_LABELS },
      { key: 'tipo_personal',      label: 'Tipo de personal',      map: PERSONAL_LABELS },
    ],
  },
  {
    titulo: 'Perfil demográfico',
    campos: [
      { key: 'sexo',           label: 'Sexo',             map: SEXO_LABELS },
      { key: 'edad',           label: 'Edad',             suffix: 'años' },
      { key: 'estado_civil',   label: 'Estado civil',     map: ESTADO_CIVIL_LABELS },
      { key: 'nivel_estudios', label: 'Nivel de estudios', map: NIVEL_LABELS },
    ],
  },
  {
    titulo: 'Jornada',
    campos: [
      { key: 'tipo_jornada',    label: 'Jornada de trabajo', map: JORNADA_LABELS },
      { key: 'rotacion_turnos', label: '¿Rota turnos?',      bool: true },
    ],
  },
  {
    titulo: 'Experiencia',
    campos: [
      { key: 'experiencia_anios',         label: 'Exp. laboral total',       suffix: 'años' },
      { key: 'experiencia_empresa_anios', label: 'Exp. empresa actual',       suffix: 'años' },
      { key: 'tiempo_puesto_actual',      label: 'Tiempo en puesto actual',   suffix: 'años' },
    ],
  },
];

function formatVal(t, campo) {
  const raw = t[campo.key];
  if (campo.bool) {
    if (raw === true)  return { texto: 'Sí',  vacio: false };
    if (raw === false) return { texto: 'No', vacio: false };
    return { texto: '—', vacio: true };
  }
  if (raw === null || raw === undefined || raw === '') return { texto: '—', vacio: true };
  if (campo.map) return { texto: campo.map[raw] ?? raw, vacio: false };
  if (campo.suffix) return { texto: `${raw} ${campo.suffix}`, vacio: false };
  return { texto: String(raw), vacio: false };
}

function completitud(t) {
  const todos = DETALLE_SECCIONES.flatMap(s => s.campos).filter(c => c.key !== 'email');
  const llenos = todos.filter(c => {
    const v = t[c.key];
    return v !== null && v !== undefined && v !== '';
  });
  return Math.round((llenos.length / todos.length) * 100);
}

function DetalleModal({ t, onClose }) {
  const pct = completitud(t);
  const initials = [t.nombre?.[0], t.apellido_paterno?.[0]].filter(Boolean).join('').toUpperCase();

  return (
    <Overlay onClick={onClose}>
      <div
        className={`${styles.modal} nom-glass`}
        style={{ maxWidth: 680, maxHeight: '90vh', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 0, padding: 0 }}
        onClick={e => e.stopPropagation()}
      >
        {/* Cabecera */}
        <div style={{ padding: '1.5rem 1.75rem 1.25rem', borderBottom: '1px solid var(--nom-border)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: 52, height: 52, borderRadius: '50%', flexShrink: 0,
            background: 'var(--nom-accent-subtle)', color: 'var(--nom-accent)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 700, fontSize: '1.15rem', fontFamily: 'var(--nom-font-display)',
            border: '2px solid var(--nom-accent)',
          }}>
            {initials}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--nom-text)', lineHeight: 1.2, marginBottom: 4 }}>
              {t.nombre_completo}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              {t.num_empleado && (
                <span style={{ fontFamily: 'monospace', fontSize: '0.78rem', color: 'var(--nom-accent)', letterSpacing: '0.06em' }}>
                  #{t.num_empleado}
                </span>
              )}
              <span className={`${styles.statusChip} ${t.activo ? styles.chipActive : styles.chipInactive}`} style={{ fontSize: 11 }}>
                {t.activo ? <CheckCircle2 size={10} /> : <AlertCircle size={10} />}
                {t.activo ? 'Activo' : 'Inactivo'}
              </span>
              <span className={styles.tipoChip} style={{ fontSize: 11 }}>{CONTRAT_LABELS[t.tipo_contratacion]}</span>
            </div>
          </div>
          {/* Barra de completitud */}
          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--nom-text-muted)', marginBottom: 4 }}>Completitud</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{ width: 72, height: 5, borderRadius: 99, background: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${pct}%`, borderRadius: 99, background: pct >= 80 ? 'var(--nom-success)' : pct >= 50 ? 'var(--nom-accent)' : 'var(--nom-danger)', transition: 'width 0.4s' }} />
              </div>
              <span style={{ fontSize: '0.78rem', fontWeight: 700, color: pct >= 80 ? 'var(--nom-success)' : pct >= 50 ? 'var(--nom-accent)' : 'var(--nom-danger)' }}>
                {pct}%
              </span>
            </div>
          </div>
          <button className={styles.modalClose} onClick={onClose} style={{ flexShrink: 0 }}><X size={18} /></button>
        </div>

        {/* Secciones */}
        <div style={{ padding: '1.25rem 1.75rem 1.75rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {DETALLE_SECCIONES.map(sec => (
            <div key={sec.titulo}>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--nom-text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '0.65rem' }}>
                {sec.titulo}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem 1.25rem' }}>
                {sec.campos.map(campo => {
                  const { texto, vacio } = formatVal(t, campo);
                  return (
                    <div key={campo.key} style={{
                      display: 'flex', flexDirection: 'column', gap: 2,
                      padding: '0.6rem 0.75rem',
                      borderRadius: 8,
                      background: vacio ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.04)',
                      border: `1px solid ${vacio ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.1)'}`,
                    }}>
                      <span style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--nom-text-muted)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                        {campo.label}
                      </span>
                      <span style={{ fontSize: '0.88rem', fontWeight: vacio ? 400 : 600, color: vacio ? 'rgba(255,255,255,0.2)' : 'var(--nom-text)' }}>
                        {texto}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Overlay>
  );
}

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
  const [detalle, setDetalle]           = useState(null);   // null | trabajador obj
  const [modal, setModal]               = useState(null);   // null | 'create' | obj
  const [form, setForm]                 = useState(EMPTY_FORM);
  const [saving, setSaving]             = useState(false);
  const [formError, setFormError]       = useState('');
  const [confirmDel, setConfirmDel]     = useState(null);

  // Importar Excel
  const [modalImport, setModalImport]   = useState(false);
  const [importFile, setImportFile]     = useState(null);
  const [importDrag, setImportDrag]     = useState(false);
  const [importing, setImporting]       = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [importError, setImportError]   = useState('');
  const openImport = () => {
    setImportFile(null);
    setImportResult(null);
    setImportError('');
    setModalImport(true);
  };
  const closeImport = () => {
    if (importing) return;
    setModalImport(false);
    setImportFile(null);
    setImportResult(null);
    setImportError('');
  };


  const handleImportSubmit = async () => {
    if (!importFile) return;
    setImporting(true);
    setImportError('');
    setImportResult(null);
    try {
      const res = await trabajadoresService.importarExcel(importFile);
      setImportResult(res.data.data);
      fetchTrabajadores(search, soloActivos);
    } catch (err) {
      const errs = err.response?.data?.errors;
      setImportError(
        errs ? Object.values(errs).flat().join(' ') : 'Error al importar el archivo.'
      );
    } finally {
      setImporting(false);
    }
  };

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
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="nom-btn nom-btn-ghost" onClick={openImport}>
            <Upload size={15} strokeWidth={2} />
            Importar Excel
          </button>
          <button className="nom-btn nom-btn-primary" onClick={openCreate}>
            <Plus size={16} strokeWidth={2.5} />
            Nuevo trabajador
          </button>
        </div>
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
            placeholder="Buscar por nombre, correo, área, puesto..."
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
                <th>Correo</th>
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
                  </td>
                  <td>
                    {t.num_empleado
                      ? <span className={styles.numCell}>{t.num_empleado}</span>
                      : <span className={styles.muteCell}>—</span>
                    }
                  </td>
                  <td className={styles.muteCell}>{t.email}</td>
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
                      <button className={styles.actionBtn} onClick={() => setDetalle(t)} title="Ver detalle">
                        <Eye size={14} strokeWidth={1.75} />
                      </button>
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
                  <label className={styles.label}>Correo electrónico *</label>
                  <input className="nom-input" type="email" placeholder="juan@empresa.com" value={form.email}
                    onChange={e => setForm(f => ({ ...f, email: e.target.value }))} required />
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

      {/* Modal importar Excel */}
      {modalImport && (
        <Overlay onClick={closeImport}>
          <div className={`${styles.modal} nom-glass`} onClick={e => e.stopPropagation()}
               style={{ maxWidth: '520px' }}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Importar trabajadores desde Excel</h2>
              <button className={styles.modalClose} onClick={closeImport} disabled={importing}>
                <X size={18} />
              </button>
            </div>

            {!importResult ? (
              <>
                {/* Patrón label+input: el click en el label abre el diálogo nativo sin js */}
                <label
                  htmlFor="import-file-input"
                  style={{
                    display: 'block',
                    border: `2px dashed ${importDrag ? 'var(--nom-accent)' : 'rgba(255,255,255,0.18)'}`,
                    borderRadius: '10px',
                    padding: '2rem',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'border-color 0.2s, background 0.2s',
                    background: importDrag ? 'rgba(3,196,206,0.06)' : 'transparent',
                    margin: '1rem 0',
                    userSelect: 'none',
                  }}
                  onDragOver={e => { e.preventDefault(); setImportDrag(true); }}
                  onDragLeave={() => setImportDrag(false)}
                  onDrop={e => { e.preventDefault(); setImportDrag(false); const f = e.dataTransfer.files[0]; if (f) setImportFile(f); }}
                >
                  <input
                    id="import-file-input"
                    type="file"
                    accept=".xlsx,.xls"
                    style={{ display: 'none' }}
                    onChange={e => { if (e.target.files[0]) setImportFile(e.target.files[0]); }}
                  />
                  {importFile ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', pointerEvents: 'none' }}>
                      <FileSpreadsheet size={32} style={{ color: 'var(--nom-accent)' }} strokeWidth={1.5} />
                      <span style={{ fontWeight: 600 }}>{importFile.name}</span>
                      <span style={{ fontSize: '0.8rem', opacity: 0.55 }}>
                        {(importFile.size / 1024).toFixed(0)} KB · Haz clic para cambiar
                      </span>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', pointerEvents: 'none' }}>
                      <Upload size={32} strokeWidth={1.5} style={{ opacity: 0.45 }} />
                      <span style={{ fontWeight: 600, opacity: 0.7 }}>Arrastra tu Excel aquí o haz clic</span>
                      <span style={{ fontSize: '0.78rem', opacity: 0.4 }}>.xlsx · .xls</span>
                    </div>
                  )}
                </label>

                <p style={{ fontSize: '0.78rem', opacity: 0.5, lineHeight: 1.5, margin: '0 0 1rem' }}>
                  El sistema detecta el formato y normaliza campos automáticamente. Si el empleado
                  ya existe por código, sus datos se actualizan.
                </p>

                {importError && <div className={styles.formError}>{importError}</div>}

                <div className={styles.modalActions}>
                  <button type="button" className="nom-btn nom-btn-ghost" onClick={closeImport} disabled={importing}>
                    Cancelar
                  </button>
                  <button
                    className="nom-btn nom-btn-primary"
                    onClick={handleImportSubmit}
                    disabled={!importFile || importing}
                    style={{ opacity: (!importFile || importing) ? 0.4 : 1, cursor: (!importFile || importing) ? 'not-allowed' : 'pointer' }}
                  >
                    {importing
                      ? <><Loader2 size={15} className="nom-spin" /> Procesando...</>
                      : <><Upload size={15} /> Importar</>
                    }
                  </button>
                </div>
              </>
            ) : (
              /* Resultado */
              <div style={{ padding: '0.5rem 0 1rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
                  {[
                    { label: 'Nuevos', value: importResult.importados, color: 'var(--nom-success)' },
                    { label: 'Actualizados', value: importResult.actualizados, color: 'var(--nom-accent)' },
                    { label: 'Omitidos', value: importResult.omitidos, color: 'rgba(255,255,255,0.4)' },
                    { label: 'Errores', value: importResult.errores?.length ?? 0, color: 'var(--nom-danger)' },
                  ].map(({ label, value, color }) => (
                    <div key={label} style={{
                      background: 'rgba(255,255,255,0.04)',
                      borderRadius: '8px',
                      padding: '0.85rem 1rem',
                      textAlign: 'center',
                    }}>
                      <div style={{ fontSize: '1.75rem', fontWeight: 700, color }}>{value}</div>
                      <div style={{ fontSize: '0.78rem', opacity: 0.6 }}>{label}</div>
                    </div>
                  ))}
                </div>

                {importResult.errores?.length > 0 && (
                  <div style={{
                    background: 'rgba(255,80,80,0.07)',
                    border: '1px solid rgba(255,80,80,0.2)',
                    borderRadius: '8px',
                    padding: '0.75rem 1rem',
                    maxHeight: '150px',
                    overflowY: 'auto',
                    marginBottom: '1rem',
                  }}>
                    <p style={{ fontSize: '0.78rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--nom-danger)' }}>
                      Filas con error:
                    </p>
                    {importResult.errores.map((e, i) => (
                      <p key={i} style={{ fontSize: '0.75rem', opacity: 0.8, margin: '0.15rem 0' }}>
                        Fila {e.fila}: {e.motivo}
                      </p>
                    ))}
                  </div>
                )}

                <div className={styles.modalActions}>
                  <button className="nom-btn nom-btn-ghost" onClick={openImport}>
                    <Upload size={14} /> Importar otro
                  </button>
                  <button className="nom-btn nom-btn-primary" onClick={closeImport}>
                    <CheckCheck size={15} /> Listo
                  </button>
                </div>
              </div>
            )}
          </div>
        </Overlay>
      )}

      {/* Detalle trabajador */}
      {detalle && <DetalleModal t={detalle} onClose={() => setDetalle(null)} />}

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
