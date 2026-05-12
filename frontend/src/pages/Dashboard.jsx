import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  Building2, Users, ClipboardCheck, Bell,
  TrendingUp, FileText, Shield,
  Megaphone, FolderOpen, CalendarCheck, ClipboardList,
  Calculator, ArrowUpRight, CalendarRange,
} from 'lucide-react';
import styles from './Dashboard.module.css';

const MODULES = [
  { to: '/empresas',      icon: Building2,     label: 'Empresas',          desc: 'Gestiona tenants registrados',     accent: 'accent',  roles: ['super_admin'] },
  { to: '/trabajadores',  icon: Users,         label: 'Trabajadores',      desc: 'Padron de empleados',              accent: 'blue',    roles: ['super_admin'] },
  { to: '/comite',        icon: Users,         label: 'Comite',            desc: 'Integrantes y minutas',            accent: 'accent'  },
  { to: '/plan-accion',   icon: ClipboardList, label: 'Plan de Accion',    desc: 'Acciones correctivas NOM-035',     accent: 'warning' },
  { to: '/politica',      icon: FileText,      label: 'Politica',          desc: 'Politica y manual interno',        accent: 'blue'    },
  { to: '/difusion',      icon: Megaphone,     label: 'Difusion',          desc: 'Centro de comunicacion interna',   accent: 'accent'  },
  { to: '/cuestionarios', icon: Shield,        label: 'Cuestionarios',     desc: 'Aplica las guias NOM-035',         accent: 'success' },
  { to: '/resultados',    icon: TrendingUp,    label: 'Resultados',        desc: 'Diagnostico y reportes',           accent: 'success' },
  { to: '/evidencias',    icon: FolderOpen,    label: 'Evidencias',        desc: 'Documentacion del cumplimiento',   accent: 'blue'    },
  { to: '/asistencias',   icon: CalendarCheck, label: 'Asistencias',       desc: 'Sesiones, minutas y firmas',       accent: 'warning' },
  { to: '/calculadora',   icon: Calculator,    label: 'Calculadora NOM',   desc: 'Calcula puntajes y categorias',    accent: 'accent'  },
];

const ESTADO_LABEL = {
  iniciado:    'Iniciado',
  en_progreso: 'En progreso',
  completado:  'Completado',
  cerrado:     'Cerrado',
};

const fmt = (v) => (v === null || v === undefined ? '—' : String(v));

function formatDateEs(d = new Date()) {
  const dias = ['Domingo', 'Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado'];
  const meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
  return `${dias[d.getDay()]} · ${d.getDate()} de ${meses[d.getMonth()]} ${d.getFullYear()}`;
}

async function loadTenantData() {
  const [trabRes, ciclosRes, notifsRes, empresaRes] = await Promise.all([
    api.get('/trabajadores/?activos=1'),
    api.get('/ciclos/'),
    api.get('/notificaciones/'),
    api.get('/tenants/mi-empresa/').catch(() => ({ data: { data: null } })),
  ]);

  const empleados   = trabRes.data.meta?.count ?? trabRes.data.data?.length ?? 0;
  const noLeidas    = notifsRes.data.meta?.no_leidas ?? 0;
  const ciclos      = ciclosRes.data.data || [];
  const ciclo       = ciclos.find((c) => c.estado !== 'cerrado') || ciclos[0] || null;
  const tenantName  = empresaRes.data.data?.nombre || null;

  let completados = 0;
  let total       = 0;
  let avance      = null;

  if (ciclo) {
    try {
      const progRes = await api.get(`/aplicaciones/progreso/?ciclo_id=${ciclo.id}`);
      completados = progRes.data.meta?.completados_total ?? 0;
      total       = progRes.data.meta?.total ?? 0;
      avance      = total > 0 ? Math.round((completados / total) * 100) : 0;
    } catch {
      /* deja en null */
    }
  }

  const cicloLabel = ciclo ? `ciclo ${ciclo.anio}` : 'sin ciclo activo';

  return {
    hero: {
      title:    tenantName || 'Tu empresa',
      eyebrow:  'Cumplimiento NOM-035-STPS-2018',
      ciclo:    ciclo ? `Ciclo ${ciclo.anio}` : 'Sin ciclo activo',
      cicloEstado: ciclo ? ESTADO_LABEL[ciclo.estado] || ciclo.estado : null,
      avance,
      progressLabel: ciclo ? `${completados} de ${total} trabajadores completados` : 'No hay aplicaciones registradas',
    },
    kpis: [
      { label: 'Empleados activos',         value: fmt(empleados),     sub: 'en tu empresa',       icon: Users,         color: 'blue'    },
      { label: 'Cuestionarios completados', value: fmt(completados),   sub: cicloLabel,            icon: ClipboardCheck,color: 'success' },
      { label: 'Notificaciones',            value: fmt(noLeidas),      sub: 'pendientes de leer',  icon: Bell,          color: 'warning' },
      { label: 'Avance NOM-035',            value: avance === null ? '—' : `${avance}%`, sub: cicloLabel, icon: TrendingUp, color: 'accent' },
    ],
  };
}

async function loadSuperData() {
  const [tenantsRes, trabRes, ciclosRes, notifsRes] = await Promise.all([
    api.get('/tenants/'),
    api.get('/trabajadores/'),
    api.get('/ciclos/'),
    api.get('/notificaciones/'),
  ]);

  const empresas      = tenantsRes.data.meta?.count ?? tenantsRes.data.data?.length ?? 0;
  const empleados     = trabRes.data.meta?.count    ?? trabRes.data.data?.length    ?? 0;
  const ciclosArr     = ciclosRes.data.data || [];
  const ciclosActivos = ciclosArr.filter((c) => c.estado !== 'cerrado').length;
  const noLeidas      = notifsRes.data.meta?.no_leidas ?? 0;

  return {
    hero: {
      title:   'Plataforma NOM-035',
      eyebrow: 'Panel global',
      ciclo:   `${ciclosActivos} ciclos activos`,
      cicloEstado: `${empresas} empresas`,
      avance:  null,
      progressLabel: `${empleados} trabajadores en todos los tenants`,
    },
    kpis: [
      { label: 'Empresas activas',  value: fmt(empresas),       sub: 'tenants registrados',  icon: Building2,    color: 'accent'  },
      { label: 'Empleados totales', value: fmt(empleados),      sub: 'en todos los tenants', icon: Users,        color: 'blue'    },
      { label: 'Ciclos activos',    value: fmt(ciclosActivos),  sub: 'en curso',             icon: CalendarRange,color: 'success' },
      { label: 'Notificaciones',    value: fmt(noLeidas),       sub: 'pendientes de leer',   icon: Bell,         color: 'warning' },
    ],
  };
}

export default function Dashboard() {
  const { user } = useAuth();
  const isSuperAdmin = user?.rol === 'super_admin';
  const [data, setData] = useState(null);
  const modules = MODULES.filter(({ roles }) => !roles || roles.includes(user?.rol));
  const fechaHoy = formatDateEs();

  useEffect(() => {
    let cancel = false;
    const loader = isSuperAdmin ? loadSuperData : loadTenantData;
    loader()
      .then((res) => { if (!cancel) setData(res); })
      .catch(() => { if (!cancel) setData({ hero: null, kpis: [] }); });
    return () => { cancel = true; };
  }, [isSuperAdmin]);

  const hero = data?.hero;
  const kpis = data?.kpis;
  const avanceVal = hero?.avance;

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <span className={styles.heroBlob1} aria-hidden />
        <span className={styles.heroBlob2} aria-hidden />
        <span className={styles.heroGrid} aria-hidden />

        <div className={styles.heroTopRow}>
          <span className={styles.heroDate}>{fechaHoy}</span>
          <span className={styles.heroStatus}>
            <span className={styles.heroStatusDot} />
            Sistema activo
          </span>
        </div>

        {hero ? (
          <div className={styles.heroMain}>
            <div className={styles.heroLeft}>
              <span className={styles.heroEyebrow}>{hero.eyebrow}</span>
              <h1 className={styles.heroTitle}>{hero.title}</h1>
              <div className={styles.heroMeta}>
                <span className={styles.heroChip}>{hero.ciclo}</span>
                {hero.cicloEstado && (
                  <span className={`${styles.heroChip} ${styles.heroChipGhost}`}>{hero.cicloEstado}</span>
                )}
              </div>
            </div>

            {!isSuperAdmin && (
              <div className={styles.heroRight}>
                <div className={styles.progressRing}>
                  <svg viewBox="0 0 120 120" className={styles.ringSvg}>
                    <circle cx="60" cy="60" r="52" className={styles.ringTrack} />
                    <circle
                      cx="60" cy="60" r="52"
                      className={styles.ringFill}
                      style={{
                        strokeDasharray:  `${2 * Math.PI * 52}`,
                        strokeDashoffset: `${2 * Math.PI * 52 * (1 - (avanceVal ?? 0) / 100)}`,
                      }}
                    />
                  </svg>
                  <div className={styles.ringCenter}>
                    <span className={styles.ringValue}>{avanceVal === null || avanceVal === undefined ? '—' : `${avanceVal}%`}</span>
                    <span className={styles.ringLabel}>avance</span>
                  </div>
                </div>
                <span className={styles.heroProgressNote}>{hero.progressLabel}</span>
              </div>
            )}

            {isSuperAdmin && (
              <div className={styles.heroRight}>
                <span className={styles.heroBigStat}>{hero.progressLabel}</span>
              </div>
            )}
          </div>
        ) : (
          <div className={styles.heroMain}>
            <div className={styles.heroLeft}>
              <div className={styles.heroSkelEyebrow} />
              <div className={styles.heroSkelTitle} />
              <div className={styles.heroSkelChips} />
            </div>
          </div>
        )}
      </section>

      <div className={styles.kpiGrid}>
        {(kpis ?? Array(4).fill(null)).map((kpi, i) => (
          <div
            key={kpi?.label ?? i}
            className={`${styles.kpiCard} nom-card`}
            style={{ animationDelay: `${i * 60}ms` }}
          >
            {kpi ? (
              <>
                <div className={`${styles.kpiIcon} ${styles[`color_${kpi.color}`]}`}>
                  <kpi.icon size={19} strokeWidth={1.75} />
                </div>
                <div className={styles.kpiValue}>{kpi.value}</div>
                <div className={styles.kpiLabel}>{kpi.label}</div>
                <div className={styles.kpiSub}>{kpi.sub}</div>
              </>
            ) : (
              <>
                <div className={styles.kpiSkeletonIcon} />
                <div className={styles.kpiSkeletonValue} />
                <div className={styles.kpiSkeletonLine} />
                <div className={styles.kpiSkeletonLineShort} />
              </>
            )}
          </div>
        ))}
      </div>

      <div className={styles.sectionHead}>
        <h2 className={styles.sectionTitle}>Modulos del sistema</h2>
        <span className={styles.sectionChip}>{modules.length} disponibles</span>
      </div>

      <div className={styles.modulesGrid}>
        {modules.map(({ to, icon: Icon, label, desc, accent }, i) => (
          <NavLink
            key={to}
            to={to}
            className={`${styles.moduleCard} nom-card`}
            style={{ animationDelay: `${200 + i * 50}ms` }}
          >
            <div className={`${styles.moduleIcon} ${styles[`accent_${accent}`]}`}>
              <Icon size={20} strokeWidth={1.75} />
            </div>
            <div className={styles.moduleBody}>
              <span className={styles.moduleLabel}>{label}</span>
              <span className={styles.moduleDesc}>{desc}</span>
            </div>
            <ArrowUpRight size={16} strokeWidth={2} className={styles.moduleArrow} />
            <span className={styles.moduleShine} aria-hidden />
          </NavLink>
        ))}
      </div>
    </div>
  );
}
