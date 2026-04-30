import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Building2, Users, ClipboardList,
  FileText, Megaphone, HelpCircle, BarChart3,
  FolderOpen, CalendarCheck, Calculator,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import styles from './Sidebar.module.css';

const NAV_ITEMS = [
  { to: '/dashboard',    icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/empresas',     icon: Building2,       label: 'Empresas',       roles: ['super_admin'] },
  { to: '/comite',       icon: Users,           label: 'Comite' },
  { to: '/plan-accion',  icon: ClipboardList,   label: 'Plan de Accion' },
  { to: '/politica',     icon: FileText,        label: 'Politica' },
  { to: '/difusion',     icon: Megaphone,       label: 'Difusion' },
  { to: '/cuestionarios',icon: HelpCircle,      label: 'Cuestionarios' },
  { to: '/resultados',   icon: BarChart3,       label: 'Resultados' },
  { to: '/evidencias',   icon: FolderOpen,      label: 'Evidencias' },
  { to: '/asistencias',  icon: CalendarCheck,   label: 'Asistencias' },
  { to: '/calculadora',  icon: Calculator,      label: 'Calculadora NOM' },
];

export default function Sidebar() {
  const { user } = useAuth();
  const visibleItems = NAV_ITEMS.filter(({ roles }) => !roles || roles.includes(user?.rol));

  return (
    <aside className={styles.sidebar}>
      <nav className={styles.nav}>
        {visibleItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `${styles.item} ${isActive ? styles.active : ''}`
            }
          >
            <Icon size={18} strokeWidth={1.75} />
            <span className={styles.tooltip}>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
