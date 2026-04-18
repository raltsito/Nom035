import { useAuth } from '../context/AuthContext';
import {
  Building2, Users, ClipboardCheck, AlertTriangle,
  TrendingUp, FileText, Shield, CheckCircle2,
  Megaphone, FolderOpen, CalendarCheck, ClipboardList,
} from 'lucide-react';
import styles from './Dashboard.module.css';

const KPI_CARDS = [
  { label: 'Empresas activas',        value: '—', sub: 'tenants registrados',    icon: Building2,     color: 'accent'   },
  { label: 'Empleados totales',        value: '—', sub: 'en todos los tenants',   icon: Users,         color: 'blue'     },
  { label: 'Cuestionarios aplicados',  value: '—', sub: 'ciclo actual',           icon: ClipboardCheck,color: 'success'  },
  { label: 'Alertas pendientes',       value: '—', sub: 'requieren atencion',     icon: AlertTriangle, color: 'warning'  },
];

const MODULE_CARDS = [
  { label: 'Gestion de Comite',        icon: Users,         status: 'Pendiente' },
  { label: 'Plan de Accion',           icon: ClipboardList, status: 'Pendiente' },
  { label: 'Politica y Manual',        icon: FileText,      status: 'Pendiente' },
  { label: 'Centro de Difusion',       icon: Megaphone,     status: 'Pendiente' },
  { label: 'Cuestionarios NOM-035',    icon: Shield,        status: 'Critico'   },
  { label: 'Resultados y Diagnostico', icon: TrendingUp,    status: 'Critico'   },
  { label: 'Gestion de Evidencias',    icon: FolderOpen,    status: 'Pendiente' },
  { label: 'Asistencias y Minutas',    icon: CalendarCheck, status: 'Pendiente' },
  { label: 'Generador de Documentos',  icon: CheckCircle2,  status: 'Critico'   },
];

export default function Dashboard() {
  const { user } = useAuth();

  return (
    <div className={styles.page}>
      {/* Page header */}
      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.title}>
            Hola, {user?.first_name}.
          </h1>
          <p className={styles.subtitle}>
            Vista general del cumplimiento NOM-035-STPS-2018
          </p>
        </div>
        <div className={styles.statusBadge}>
          <span className={styles.statusDot} />
          Sistema activo
        </div>
      </div>

      {/* KPIs */}
      <div className={styles.kpiGrid}>
        {KPI_CARDS.map(({ label, value, sub, icon: Icon, color }, i) => (
          <div
            key={label}
            className={`${styles.kpiCard} nom-card`}
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className={`${styles.kpiIcon} ${styles[`color_${color}`]}`}>
              <Icon size={19} strokeWidth={1.75} />
            </div>
            <div className={styles.kpiValue}>{value}</div>
            <div className={styles.kpiLabel}>{label}</div>
            <div className={styles.kpiSub}>{sub}</div>
          </div>
        ))}
      </div>

      {/* Modules */}
      <div className={styles.sectionHead}>
        <h2 className={styles.sectionTitle}>Modulos del sistema</h2>
        <span className={styles.sectionChip}>En construccion</span>
      </div>

      <div className={styles.modulesGrid}>
        {MODULE_CARDS.map(({ label, icon: Icon, status }, i) => (
          <div
            key={label}
            className={`${styles.moduleCard} nom-card`}
            style={{ animationDelay: `${200 + i * 40}ms` }}
          >
            <div className={styles.moduleIcon}>
              <Icon size={17} strokeWidth={1.75} />
            </div>
            <div className={styles.moduleBody}>
              <span className={styles.moduleLabel}>{label}</span>
              <span className={`${styles.chip} ${status === 'Critico' ? styles.chipCritical : styles.chipPending}`}>
                {status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
