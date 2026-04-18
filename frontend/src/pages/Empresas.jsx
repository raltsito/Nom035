import { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import {
  Building2, Plus, Search, Users, FileText,
  ToggleLeft, ToggleRight, Pencil, Trash2,
  Loader2, X, CheckCircle2, AlertCircle,
  ChevronRight, BarChart2, RefreshCw, UserPlus,
  TrendingUp, ClipboardList, ShieldCheck,
} from 'lucide-react';
import { tenantsService } from '../services/tenants';
import styles from './Empresas.module.css';

const GUIA_LABELS  = { I: 'Guia I', III: 'Guia III', V: 'Guia V' };
const TAMANO_LABELS = {
  micro:          'Micro (hasta 15)',
  pequena:        'Pequena (16-50)',
  mediana_grande: 'Mediana / Grande (50+)',
};
const CAT_CFG = {
  bajo:     { label: 'Nulo / Bajo', color: 'var(--nom-riesgo-nulo)' },
  medio:    { label: 'Medio',       color: 'var(--nom-riesgo-medio)' },
  alto:     { label: 'Alto',        color: 'var(--nom-riesgo-alto)' },
  muy_alto: { label: 'Muy alto',    color: 'var(--nom-riesgo-muy-alto)' },
};

const EMPTY_FORM  = { nombre: '', rfc: '', giro: '', num_trabajadores: '' };
const EMPTY_USER  = { email: '', first_name: '', last_name: '', password: '' };
const EMPTY_ADMIN = { first_name: '', last_name: '', email: '', password: '' };

export default function Empresas() {
  const [tenants, setTenants]       = useState([]);
  const [loading, setLoading]       = useState(true);
  const [search, setSearch]         = useState('');
  const [modal, setModal]           = useState(null);
  const [form, setForm]             = useState(EMPTY_FORM);
  const [saving, setSaving]         = useState(false);
  const [formError, setFormError]   = useState('');
  const [confirmDel, setConfirmDel] = useState(null);
  const [adminForm, setAdminForm]   = useState(EMPTY_ADMIN);

  // Detail drawer
  const [drawer, setDrawer]           = useState(null);   // tenant object
  const [drawerTab, setDrawerTab]     = useState('stats');
  const [drawerStats, setDrawerStats] = useState(null);
  const [drawerUsers, setDrawerUsers] = useState([]);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [showUserForm, setShowUserForm]   = useState(false);
  const [userForm, setUserForm]     = useState(EMPTY_USER);
  const [userSaving, setUserSaving] = useState(false);
  const [userError, setUserError]   = useState('');

  const fetchTenants = useCallback(async (q = '') => {
    setLoading(true);
    try {
      const res = await tenantsService.list(q);
      setTenants(res.data.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTenants(); }, [fetchTenants]);

  useEffect(() => {
    const t = setTimeout(() => fetchTenants(search), 300);
    return () => clearTimeout(t);
  }, [search, fetchTenants]);

  const openCreate = () => {
    setForm(EMPTY_FORM);
    setAdminForm(EMPTY_ADMIN);
    setFormError('');
    setModal('create');
  };

  const openEdit = (tenant) => {
    setForm({
      nombre:           tenant.nombre,
      rfc:              tenant.rfc,
      giro:             tenant.giro,
      num_trabajadores: String(tenant.num_trabajadores),
    });
    setFormError('');
    setModal(tenant);
  };

  const closeModal = () => { setModal(null); setFormError(''); setAdminForm(EMPTY_ADMIN); };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setFormError('');
    try {
      const payload = { ...form, num_trabajadores: Number(form.num_trabajadores) };
      if (modal === 'create') {
        const res = await tenantsService.create(payload);
        await tenantsService.createUsuario(res.data.data.id, adminForm);
      } else {
        await tenantsService.update(modal.id, payload);
      }
      closeModal();
      fetchTenants(search);
    } catch (err) {
      const errors = err.response?.data?.errors;
      setFormError(errors
        ? Object.values(errors).flat().join(' ')
        : 'Ocurrio un error. Intenta de nuevo.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (tenant) => {
    try {
      const res = await tenantsService.toggleActivo(tenant.id);
      setTenants(prev => prev.map(t => t.id === tenant.id ? res.data.data : t));
    } catch {}
  };

  const handleDelete = async () => {
    if (!confirmDel) return;
    try {
      await tenantsService.delete(confirmDel.id);
      setTenants(prev => prev.filter(t => t.id !== confirmDel.id));
    } finally {
      setConfirmDel(null);
    }
  };

  // Detail drawer
  const openDrawer = async (tenant) => {
    setDrawer(tenant);
    setDrawerTab('stats');
    setDrawerStats(null);
    setDrawerUsers([]);
    setShowUserForm(false);
    setUserError('');
    setDrawerLoading(true);
    try {
      const [sRes, uRes] = await Promise.all([
        tenantsService.stats(tenant.id),
        tenantsService.getUsuarios(tenant.id),
      ]);
      setDrawerStats(sRes.data.data);
      setDrawerUsers(uRes.data.data);
    } finally {
      setDrawerLoading(false);
    }
  };

  const closeDrawer = () => {
    setDrawer(null);
    setShowUserForm(false);
    setUserError('');
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setUserSaving(true);
    setUserError('');
    try {
      const res = await tenantsService.createUsuario(drawer.id, userForm);
      setDrawerUsers(prev => [...prev, res.data.data]);
      setShowUserForm(false);
      setUserForm(EMPTY_USER);
    } catch (err) {
      const errors = err.response?.data?.errors;
      setUserError(errors
        ? Object.values(errors).flat().join(' ')
        : 'Ocurrio un error al crear el usuario.');
    } finally {
      setUserSaving(false);
    }
  };

  const isEditing = modal && modal !== 'create';

  const dist = drawerStats?.distribucion || {};
  const totalDist = Object.values(dist).reduce((a, b) => a + b, 0);

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Empresas</h1>
          <p className={styles.subtitle}>Gestiona las empresas cliente registradas en el sistema</p>
        </div>
        <button className="nom-btn nom-btn-primary" onClick={openCreate}>
          <Plus size={16} strokeWidth={2.5} />
          Nueva empresa
        </button>
      </div>

      {/* Search */}
      <div className={styles.searchWrap}>
        <Search size={16} className={styles.searchIcon} />
        <input
          type="text"
          className={styles.searchInput}
          placeholder="Buscar por nombre o RFC..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        {search && (
          <button className={styles.searchClear} onClick={() => setSearch('')}>
            <X size={14} />
          </button>
        )}
      </div>

      {/* Content */}
      {loading ? (
        <div className={styles.loadingWrap}>
          <Loader2 size={28} className="nom-spin" />
        </div>
      ) : tenants.length === 0 ? (
        <div className={styles.empty}>
          <Building2 size={40} strokeWidth={1.25} />
          <p>{search ? 'No se encontraron resultados.' : 'Aun no hay empresas registradas.'}</p>
          {!search && (
            <button className="nom-btn nom-btn-accent" onClick={openCreate}>
              <Plus size={15} />
              Registrar primera empresa
            </button>
          )}
        </div>
      ) : (
        <div className={styles.grid}>
          {tenants.map((t, i) => (
            <div
              key={t.id}
              className={`${styles.card} nom-card ${!t.activo ? styles.cardInactive : ''}`}
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <div className={styles.cardTop}>
                <div className={styles.cardIcon}>
                  <Building2 size={18} strokeWidth={1.75} />
                </div>
                <div className={styles.cardMeta}>
                  <span className={`${styles.statusChip} ${t.activo ? styles.statusActive : styles.statusInactive}`}>
                    {t.activo ? <CheckCircle2 size={11} /> : <AlertCircle size={11} />}
                    {t.activo ? 'Activa' : 'Inactiva'}
                  </span>
                </div>
              </div>

              <h3 className={styles.cardName}>{t.nombre}</h3>
              <p className={styles.cardRfc}>{t.rfc}</p>
              <p className={styles.cardGiro}>{t.giro}</p>

              <div className={styles.statsRow}>
                <div className={styles.stat}>
                  <Users size={13} strokeWidth={2} />
                  <span>{t.num_trabajadores} trabajadores</span>
                </div>
                <div className={styles.stat}>
                  <FileText size={13} strokeWidth={2} />
                  <span>{TAMANO_LABELS[t.categoria_tamano]}</span>
                </div>
              </div>

              <div className={styles.guiasRow}>
                {t.guias_aplicables.map(g => (
                  <span key={g} className={styles.guiaChip}>{GUIA_LABELS[g]}</span>
                ))}
              </div>

              <div className={styles.cardActions}>
                <button
                  className={styles.actionBtn}
                  onClick={() => handleToggle(t)}
                  title={t.activo ? 'Desactivar' : 'Activar'}
                >
                  {t.activo
                    ? <ToggleRight size={16} strokeWidth={1.75} />
                    : <ToggleLeft size={16} strokeWidth={1.75} />
                  }
                </button>
                <button className={styles.actionBtn} onClick={() => openEdit(t)} title="Editar">
                  <Pencil size={15} strokeWidth={1.75} />
                </button>
                <button
                  className={`${styles.actionBtn} ${styles.actionDanger}`}
                  onClick={() => setConfirmDel(t)}
                  title="Eliminar"
                >
                  <Trash2 size={15} strokeWidth={1.75} />
                </button>
                <span className={styles.actionSpacer} />
                <button className={styles.detailBtn} onClick={() => openDrawer(t)}>
                  Ver detalle <ChevronRight size={13} strokeWidth={2.5} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ---- Detail Drawer ---- */}
      {drawer && (
        <div className={styles.drawerOverlay} onClick={closeDrawer}>
          <div className={styles.drawer} onClick={e => e.stopPropagation()}>
            {/* Drawer header */}
            <div className={styles.drawerHeader}>
              <div className={styles.drawerHeaderLeft}>
                <div className={styles.drawerIcon}>
                  <Building2 size={20} strokeWidth={1.75} />
                </div>
                <div>
                  <h2 className={styles.drawerTitle}>{drawer.nombre}</h2>
                  <p className={styles.drawerRfc}>{drawer.rfc}</p>
                </div>
              </div>
              <button className={styles.modalClose} onClick={closeDrawer}>
                <X size={18} />
              </button>
            </div>

            {/* Tabs */}
            <div className={styles.drawerTabs}>
              <button
                className={`${styles.drawerTab} ${drawerTab === 'stats' ? styles.drawerTabActive : ''}`}
                onClick={() => setDrawerTab('stats')}
              >
                <BarChart2 size={14} />
                Estadisticas
              </button>
              <button
                className={`${styles.drawerTab} ${drawerTab === 'usuarios' ? styles.drawerTabActive : ''}`}
                onClick={() => setDrawerTab('usuarios')}
              >
                <Users size={14} />
                Usuarios
              </button>
            </div>

            {/* Drawer body */}
            <div className={styles.drawerBody}>
              {drawerLoading ? (
                <div className={styles.loadingWrap}>
                  <Loader2 size={26} className="nom-spin" />
                </div>
              ) : drawerTab === 'stats' ? (
                drawerStats ? (
                  <>
                    {/* KPI grid */}
                    <div className={styles.drawerKpis}>
                      <div className={`${styles.kpiCard} nom-card`}>
                        <div className={styles.kpiIcon} style={{ background: 'var(--nom-accent-subtle)', color: 'var(--nom-accent)' }}>
                          <Users size={16} strokeWidth={1.75} />
                        </div>
                        <div className={styles.kpiNum}>{drawerStats.total_trabajadores}</div>
                        <div className={styles.kpiLabel}>Trabajadores</div>
                      </div>
                      <div className={`${styles.kpiCard} nom-card`}>
                        <div className={styles.kpiIcon} style={{ background: 'var(--nom-success-subtle)', color: 'var(--nom-success)' }}>
                          <RefreshCw size={16} strokeWidth={1.75} />
                        </div>
                        <div className={styles.kpiNum}>{drawerStats.total_ciclos}</div>
                        <div className={styles.kpiLabel}>Ciclos</div>
                      </div>
                      <div className={`${styles.kpiCard} nom-card`}>
                        <div className={styles.kpiIcon} style={{ background: 'rgba(245,158,11,0.12)', color: '#d97706' }}>
                          <ClipboardList size={16} strokeWidth={1.75} />
                        </div>
                        <div className={styles.kpiNum}>{drawerStats.total_aplicaciones}</div>
                        <div className={styles.kpiLabel}>Aplicaciones</div>
                      </div>
                      <div className={`${styles.kpiCard} nom-card`}>
                        <div className={styles.kpiIcon} style={{ background: 'rgba(139,92,246,0.12)', color: '#7c3aed' }}>
                          <TrendingUp size={16} strokeWidth={1.75} />
                        </div>
                        <div className={styles.kpiNum}>{drawerStats.total_completadas}</div>
                        <div className={styles.kpiLabel}>Completadas</div>
                      </div>
                      <div className={`${styles.kpiCard} nom-card`}>
                        <div className={styles.kpiIcon} style={{ background: 'var(--nom-accent-subtle)', color: 'var(--nom-accent)' }}>
                          <ShieldCheck size={16} strokeWidth={1.75} />
                        </div>
                        <div className={styles.kpiNum}>{drawerStats.total_resultados}</div>
                        <div className={styles.kpiLabel}>Diagnosticados</div>
                      </div>
                    </div>

                    {/* Risk distribution */}
                    {totalDist > 0 && (
                      <div className={styles.distSection}>
                        <h4 className={styles.distTitle}>Distribucion de riesgo</h4>
                        <div className={styles.distList}>
                          {Object.entries(CAT_CFG).map(([key, cfg]) => {
                            const count = dist[key] || 0;
                            const pct   = totalDist > 0 ? Math.round(count / totalDist * 100) : 0;
                            return (
                              <div key={key} className={styles.distRow}>
                                <span className={styles.distLabel} style={{ color: cfg.color }}>
                                  {cfg.label}
                                </span>
                                <div className={styles.distTrack}>
                                  <div
                                    className={styles.distFill}
                                    style={{ width: `${pct}%`, background: cfg.color }}
                                  />
                                </div>
                                <span className={styles.distCount}>{count}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className={styles.empty}>
                    <BarChart2 size={32} strokeWidth={1.25} />
                    <p>No hay estadisticas disponibles.</p>
                  </div>
                )
              ) : (
                /* --- Usuarios tab --- */
                <div className={styles.usersSection}>
                  <div className={styles.usersSectionHeader}>
                    <span className={styles.usersCount}>
                      {drawerUsers.length} usuario{drawerUsers.length !== 1 ? 's' : ''}
                    </span>
                    {!showUserForm && (
                      <button
                        className="nom-btn nom-btn-primary"
                        style={{ padding: '7px 16px', fontSize: '13px' }}
                        onClick={() => { setShowUserForm(true); setUserForm(EMPTY_USER); setUserError(''); }}
                      >
                        <UserPlus size={14} />
                        Agregar usuario
                      </button>
                    )}
                  </div>

                  {showUserForm && (
                    <form onSubmit={handleCreateUser} className={styles.userForm}>
                      <div className={styles.userFormTitle}>
                        <UserPlus size={14} />
                        Nuevo administrador
                      </div>
                      <div className={styles.userFormGrid}>
                        <div className={styles.field}>
                          <label className={styles.label}>Nombre *</label>
                          <input
                            className="nom-input"
                            placeholder="Nombre"
                            value={userForm.first_name}
                            onChange={e => setUserForm(f => ({ ...f, first_name: e.target.value }))}
                            required
                          />
                        </div>
                        <div className={styles.field}>
                          <label className={styles.label}>Apellido *</label>
                          <input
                            className="nom-input"
                            placeholder="Apellido"
                            value={userForm.last_name}
                            onChange={e => setUserForm(f => ({ ...f, last_name: e.target.value }))}
                            required
                          />
                        </div>
                        <div className={`${styles.field} ${styles.fieldFull}`}>
                          <label className={styles.label}>Correo electronico *</label>
                          <input
                            className="nom-input"
                            type="email"
                            placeholder="correo@empresa.com"
                            value={userForm.email}
                            onChange={e => setUserForm(f => ({ ...f, email: e.target.value }))}
                            required
                          />
                        </div>
                        <div className={`${styles.field} ${styles.fieldFull}`}>
                          <label className={styles.label}>Contrasena inicial *</label>
                          <input
                            className="nom-input"
                            type="password"
                            placeholder="Minimo 8 caracteres"
                            value={userForm.password}
                            onChange={e => setUserForm(f => ({ ...f, password: e.target.value }))}
                            minLength={8}
                            required
                          />
                        </div>
                      </div>
                      {userError && (
                        <div className={styles.formError}>{userError}</div>
                      )}
                      <div className={styles.modalActions}>
                        <button
                          type="button"
                          className="nom-btn nom-btn-ghost"
                          onClick={() => setShowUserForm(false)}
                        >
                          Cancelar
                        </button>
                        <button type="submit" className="nom-btn nom-btn-primary" disabled={userSaving}>
                          {userSaving ? <Loader2 size={14} className="nom-spin" /> : <UserPlus size={14} />}
                          {userSaving ? 'Creando...' : 'Crear usuario'}
                        </button>
                      </div>
                    </form>
                  )}

                  {drawerUsers.length === 0 ? (
                    <div className={styles.emptyUsers}>
                      <Users size={32} strokeWidth={1.25} />
                      <p>Esta empresa aun no tiene usuarios registrados.</p>
                    </div>
                  ) : (
                    <div className={styles.usersList}>
                      {drawerUsers.map(u => (
                        <div key={u.id} className={styles.userRow}>
                          <div className={styles.userAvatar}>
                            {(u.first_name?.[0] || u.email[0]).toUpperCase()}
                          </div>
                          <div className={styles.userInfo}>
                            <span className={styles.userName}>{u.nombre_completo || u.email}</span>
                            <span className={styles.userEmail}>{u.email}</span>
                          </div>
                          <span className={`${styles.userRolChip} ${u.is_active ? styles.userActive : styles.userInactive}`}>
                            {u.is_active ? <CheckCircle2 size={10} /> : <AlertCircle size={10} />}
                            {u.is_active ? 'Activo' : 'Inactivo'}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ---- Modal crear/editar ---- */}
      {modal && createPortal(
        <div className={styles.overlay} onClick={closeModal}>
          <div className={styles.modal} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>
                {isEditing ? 'Editar empresa' : 'Nueva empresa'}
              </h2>
              <button className={styles.modalClose} onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSave} className={styles.modalForm}>
              <div className={styles.formGrid}>
                <div className={styles.field}>
                  <label className={styles.label}>Razon social *</label>
                  <input
                    className="nom-input"
                    placeholder="Empresa S.A. de C.V."
                    value={form.nombre}
                    onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>RFC *</label>
                  <input
                    className="nom-input"
                    placeholder="EMP010101XXX"
                    value={form.rfc}
                    onChange={e => setForm(f => ({ ...f, rfc: e.target.value.toUpperCase() }))}
                    maxLength={13}
                    required
                    disabled={isEditing}
                    style={isEditing ? { opacity: 0.6 } : {}}
                  />
                </div>
                <div className={`${styles.field} ${styles.fieldFull}`}>
                  <label className={styles.label}>Giro o actividad *</label>
                  <input
                    className="nom-input"
                    placeholder="Manufactura, servicios, comercio..."
                    value={form.giro}
                    onChange={e => setForm(f => ({ ...f, giro: e.target.value }))}
                    required
                  />
                </div>
                <div className={styles.field}>
                  <label className={styles.label}>Numero de trabajadores *</label>
                  <input
                    className="nom-input"
                    type="number"
                    placeholder="0"
                    min="1"
                    value={form.num_trabajadores}
                    onChange={e => setForm(f => ({ ...f, num_trabajadores: e.target.value }))}
                    required
                  />
                </div>
              </div>

              {form.num_trabajadores && (
                <div className={styles.guiasHint}>
                  <FileText size={13} />
                  Guias aplicables:&nbsp;
                  <strong>
                    {Number(form.num_trabajadores) <= 15
                      ? 'Guia I'
                      : Number(form.num_trabajadores) <= 50
                        ? 'Guias I y III'
                        : 'Guias I, III y V'
                    }
                  </strong>
                </div>
              )}

              {!isEditing && (
                <>
                  <div className={styles.sectionDivider}>
                    <UserPlus size={13} />
                    Acceso del administrador
                  </div>
                  <div className={styles.formGrid}>
                    <div className={styles.field}>
                      <label className={styles.label}>Nombre *</label>
                      <input
                        className="nom-input"
                        placeholder="Nombre"
                        value={adminForm.first_name}
                        onChange={e => setAdminForm(f => ({ ...f, first_name: e.target.value }))}
                        required
                      />
                    </div>
                    <div className={styles.field}>
                      <label className={styles.label}>Apellido *</label>
                      <input
                        className="nom-input"
                        placeholder="Apellido"
                        value={adminForm.last_name}
                        onChange={e => setAdminForm(f => ({ ...f, last_name: e.target.value }))}
                        required
                      />
                    </div>
                    <div className={`${styles.field} ${styles.fieldFull}`}>
                      <label className={styles.label}>Correo electronico *</label>
                      <input
                        className="nom-input"
                        type="email"
                        placeholder="admin@empresa.com"
                        value={adminForm.email}
                        onChange={e => setAdminForm(f => ({ ...f, email: e.target.value }))}
                        required
                      />
                    </div>
                    <div className={`${styles.field} ${styles.fieldFull}`}>
                      <label className={styles.label}>Contrasena inicial *</label>
                      <input
                        className="nom-input"
                        type="password"
                        placeholder="Minimo 8 caracteres"
                        value={adminForm.password}
                        onChange={e => setAdminForm(f => ({ ...f, password: e.target.value }))}
                        minLength={8}
                        required
                      />
                    </div>
                  </div>
                </>
              )}

              {formError && <div className={styles.formError}>{formError}</div>}

              <div className={styles.modalActions}>
                <button type="button" className="nom-btn nom-btn-ghost" onClick={closeModal}>
                  Cancelar
                </button>
                <button type="submit" className="nom-btn nom-btn-primary" disabled={saving}>
                  {saving ? <Loader2 size={15} className="nom-spin" /> : (isEditing ? 'Guardar cambios' : 'Crear empresa')}
                </button>
              </div>
            </form>
          </div>
        </div>,
        document.body
      )}

      {/* ---- Modal confirmar eliminacion ---- */}
      {confirmDel && createPortal(
        <div className={styles.overlay} onClick={() => setConfirmDel(null)}>
          <div className={`${styles.modal} ${styles.modalSm}`} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Eliminar empresa</h2>
              <button className={styles.modalClose} onClick={() => setConfirmDel(null)}>
                <X size={18} />
              </button>
            </div>
            <p className={styles.confirmText}>
              Esta accion es irreversible. Se eliminara <strong>{confirmDel.nombre}</strong> y todos sus datos asociados.
            </p>
            <div className={styles.modalActions}>
              <button className="nom-btn nom-btn-ghost" onClick={() => setConfirmDel(null)}>Cancelar</button>
              <button className={`nom-btn ${styles.btnDanger}`} onClick={handleDelete}>Eliminar</button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
