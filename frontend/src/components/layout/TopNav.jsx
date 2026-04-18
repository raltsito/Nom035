import { NavLink, useNavigate } from 'react-router-dom';
import { Sun, Moon, ChevronDown, LogOut, Bell, Check, CheckCheck, X, Zap, Clock, Calendar } from 'lucide-react';
import { useState, useRef, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../hooks/useTheme';
import { notificacionesService } from '../../services/notificaciones';
import styles from './TopNav.module.css';

const ROL_LABEL = {
  super_admin: 'Super Admin',
  tenant_admin: 'Administrador',
  empleado: 'Empleado',
  auditor: 'Auditor',
};

const NAV_LINKS = [
  { to: '/dashboard',    label: 'Dashboard' },
  { to: '/empresas',     label: 'Empresas' },
  { to: '/trabajadores', label: 'Trabajadores' },
  { to: '/cuestionarios', label: 'Cuestionarios' },
  { to: '/resultados',   label: 'Resultados' },
];

const TIPO_ICON = {
  accion_vencida:    { Icon: Zap,      color: 'var(--nom-danger)',  bg: 'var(--nom-danger-subtle)' },
  accion_por_vencer: { Icon: Clock,    color: '#d97706',            bg: 'rgba(245,158,11,0.10)' },
  ciclo_por_cerrar:  { Icon: Calendar, color: 'var(--nom-accent)',  bg: 'var(--nom-accent-subtle)' },
  info:              { Icon: Bell,     color: 'var(--nom-success)', bg: 'var(--nom-success-subtle)' },
};

export default function TopNav() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { theme, toggle } = useTheme();
  const [menuOpen, setMenuOpen]     = useState(false);
  const [bellOpen, setBellOpen]     = useState(false);
  const [notifs, setNotifs]         = useState([]);
  const [noLeidas, setNoLeidas]     = useState(0);
  const menuRef = useRef(null);
  const bellRef = useRef(null);

  const fetchNotifs = useCallback(async () => {
    if (!user) return;
    try {
      const res = await notificacionesService.generar();
      setNotifs(res.data.data || []);
      setNoLeidas(res.data.meta?.no_leidas ?? 0);
    } catch {
      // silencioso
    }
  }, [user]);

  useEffect(() => { fetchNotifs(); }, [fetchNotifs]);

  useEffect(() => {
    if (!menuOpen && !bellOpen) return;
    const close = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
      if (bellRef.current && !bellRef.current.contains(e.target)) setBellOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, [menuOpen, bellOpen]);

  const handleMarkRead = async (notif) => {
    if (!notif.leida) {
      await notificacionesService.markRead(notif.id);
      setNotifs(prev => prev.map(n => n.id === notif.id ? { ...n, leida: true } : n));
      setNoLeidas(prev => Math.max(0, prev - 1));
    }
    if (notif.url_destino) {
      setBellOpen(false);
      navigate(notif.url_destino);
    }
  };

  const handleMarkAll = async () => {
    await notificacionesService.marcarTodas();
    setNotifs(prev => prev.map(n => ({ ...n, leida: true })));
    setNoLeidas(0);
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    await notificacionesService.delete(id);
    const removed = notifs.find(n => n.id === id);
    setNotifs(prev => prev.filter(n => n.id !== id));
    if (removed && !removed.leida) setNoLeidas(prev => Math.max(0, prev - 1));
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const initials = user
    ? `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
    : '?';

  return (
    <header className={styles.nav}>
      {/* Logo */}
      <div className={styles.logo}>
        <img src="/logo-intra.jpg" alt="Intra" className={styles.logoImg} />
        <span className={styles.logoPill}>NOM-035</span>
      </div>

      {/* Links centrales */}
      <nav className={styles.links}>
        {NAV_LINKS.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `${styles.link} ${isActive ? styles.linkActive : ''}`
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Acciones */}
      <div className={styles.actions}>
        <button
          className={styles.iconBtn}
          onClick={toggle}
          title={theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'}
        >
          {theme === 'light' ? <Moon size={17} strokeWidth={1.75} /> : <Sun size={17} strokeWidth={1.75} />}
        </button>

        {/* Bell */}
        <div ref={bellRef} className={styles.bellWrap}>
          <button
            className={`${styles.iconBtn} ${bellOpen ? styles.iconBtnActive : ''}`}
            onClick={() => setBellOpen(v => !v)}
            title="Notificaciones"
          >
            <Bell size={17} strokeWidth={1.75} />
            {noLeidas > 0 && (
              <span className={styles.badge}>{noLeidas > 9 ? '9+' : noLeidas}</span>
            )}
          </button>

          {bellOpen && (
            <div className={`${styles.bellDropdown} nom-glass`}>
              <div className={styles.bellHeader}>
                <span className={styles.bellTitle}>Notificaciones</span>
                {noLeidas > 0 && (
                  <button className={styles.markAllBtn} onClick={handleMarkAll}>
                    <CheckCheck size={13} />
                    Marcar todas
                  </button>
                )}
              </div>
              <div className={styles.bellList}>
                {notifs.length === 0 ? (
                  <div className={styles.bellEmpty}>
                    <Check size={20} color="var(--nom-success)" />
                    <span>Sin notificaciones pendientes</span>
                  </div>
                ) : (
                  notifs.slice(0, 8).map(n => {
                    const cfg  = TIPO_ICON[n.tipo] || TIPO_ICON.info;
                    const Icon = cfg.Icon;
                    return (
                      <div
                        key={n.id}
                        className={`${styles.notifItem} ${!n.leida ? styles.notifUnread : ''}`}
                        onClick={() => handleMarkRead(n)}
                      >
                        <div className={styles.notifIcon} style={{ background: cfg.bg }}>
                          <Icon size={14} color={cfg.color} />
                        </div>
                        <div className={styles.notifBody}>
                          <p className={styles.notifTitle}>{n.titulo}</p>
                          {n.mensaje && <p className={styles.notifMsg}>{n.mensaje}</p>}
                        </div>
                        <button
                          className={styles.notifDel}
                          onClick={(e) => handleDelete(e, n.id)}
                          title="Descartar"
                        >
                          <X size={11} />
                        </button>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>

        {/* User menu */}
        <div ref={menuRef} className={styles.userWrap}>
          <button
            className={styles.userBtn}
            onClick={() => setMenuOpen(v => !v)}
          >
            <div className={styles.avatar}>{initials}</div>
            <div className={styles.userInfo}>
              <span className={styles.userName}>
                {user?.first_name} {user?.last_name}
              </span>
              <span className={styles.userRole}>
                {ROL_LABEL[user?.rol] || ''}
              </span>
            </div>
            <ChevronDown
              size={13}
              strokeWidth={2.5}
              className={`${styles.chevron} ${menuOpen ? styles.chevronOpen : ''}`}
            />
          </button>

          {menuOpen && (
            <div className={`${styles.dropdown} nom-glass`}>
              <button className={styles.dropItemConfig} onClick={() => { navigate('/configuracion'); setMenuOpen(false); }}>
                Configuracion de empresa
              </button>
              <div className={styles.dropDivider} />
              <button className={styles.dropItem} onClick={handleLogout}>
                <LogOut size={14} strokeWidth={2} />
                Cerrar sesion
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
