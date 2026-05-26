import { useState, useEffect, useCallback } from 'react';
import {
  Calculator, Users, Target, PieChart, Info,
  Loader2, Building2, UserCircle, Briefcase,
  Clock, BarChart2, Download, RefreshCw, Shuffle,
  ChevronUp, ChevronDown, ListChecks, Search, X,
} from 'lucide-react';
import { trabajadoresService } from '../services/trabajadores';
import styles from './Calculadora.module.css';

const ESTRATOS_CFG = [
  { key: 'area',              label: 'Por área / departamento',    icon: Building2,   color: 'var(--nom-accent)' },
  { key: 'sexo',              label: 'Por sexo',                   icon: UserCircle,  color: '#a78bfa' },
  { key: 'tipo_contratacion', label: 'Por tipo de contratación',   icon: Briefcase,   color: '#f59e0b' },
  { key: 'tipo_puesto',       label: 'Por tipo de puesto',         icon: BarChart2,   color: '#34d399' },
  { key: 'edad',              label: 'Por edad',                   icon: Users,       color: '#f87171' },
  { key: 'antiguedad',        label: 'Por antigüedad en empresa',  icon: Clock,       color: '#60a5fa' },
];

function EstratoCard({ cfg, filas, n }) {
  const { label, icon: Icon, color } = cfg;
  const max = Math.max(...filas.map(f => f.total), 1);
  return (
    <div className={`nom-card ${styles.estratoCard}`}>
      <div className={styles.estratoCardHeader}>
        <div className={styles.estratoCardIcon} style={{ background: `${color}18`, color }}>
          <Icon size={15} strokeWidth={1.75} />
        </div>
        <div>
          <div className={styles.estratoCardTitle}>{label}</div>
          <div className={styles.estratoCardSub}>{filas.length} grupos · muestra total {n}</div>
        </div>
      </div>
      <div className={styles.estratoRows}>
        {filas.map((f, i) => (
          <div key={i} className={styles.estratoRow}>
            <div className={styles.estratoRowLabel}>{f.label}</div>
            <div className={styles.estratoBarWrap}>
              <div
                className={styles.estratoBarFill}
                style={{ width: `${(f.total / max) * 100}%`, background: color }}
              />
            </div>
            <div className={styles.estratoRowNums}>
              <span className={styles.estratoTotal}>{f.total}</span>
              <span className={styles.estratoPct}>{f.pct}%</span>
              <span className={styles.estratoMuestra} style={{ color }}>
                {f.muestra} enc.
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const s = (v) => (v || '');
const SORT_KEYS = {
  nombre_completo:   (a, b) => s(a.nombre_completo).localeCompare(s(b.nombre_completo)),
  area:              (a, b) => s(a.area).localeCompare(s(b.area)),
  puesto:            (a, b) => s(a.puesto).localeCompare(s(b.puesto)),
  sexo:              (a, b) => s(a.sexo).localeCompare(s(b.sexo)),
  tipo_contratacion: (a, b) => s(a.tipo_contratacion).localeCompare(s(b.tipo_contratacion)),
  edad:              (a, b) => (a.edad ?? 0) - (b.edad ?? 0),
  num_empleado:      (a, b) => s(a.num_empleado).localeCompare(s(b.num_empleado)),
};

export default function Calculadora() {
  const [data, setData]               = useState(null);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState('');
  const [sugeridos, setSugeridos]     = useState(null);
  const [loadingSug, setLoadingSug]   = useState(false);
  const [seed, setSeed]               = useState(1);
  const [listaAbierta, setListaAbierta] = useState(false);
  const [sortKey, setSortKey]         = useState('area');
  const [sortAsc, setSortAsc]         = useState(true);
  const [busqueda, setBusqueda]       = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await trabajadoresService.resumenMuestra();
      setData(res.data.data);
    } catch {
      setError('No se pudo cargar la información. Verifica tu conexión.');
    } finally {
      setLoading(false);
    }
  };

  const fetchSugeridos = useCallback(async (s) => {
    setLoadingSug(true);
    try {
      const res = await trabajadoresService.sugeridosMuestra(s);
      setSugeridos(res.data.data);
    } catch {
      setSugeridos(null);
    } finally {
      setLoadingSug(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, []);

  useEffect(() => {
    if (data && data.N > 0) fetchSugeridos(seed);
  }, [data, seed, fetchSugeridos]);

  const regenerar = () => {
    const newSeed = Math.floor(Math.random() * 99999) + 1;
    setSeed(newSeed);
  };

  const toggleSort = (key) => {
    if (sortKey === key) setSortAsc(v => !v);
    else { setSortKey(key); setSortAsc(true); }
  };

  const [exportando, setExportando] = useState(false);

  const exportarExcel = async () => {
    if (!data || exportando) return;
    setExportando(true);
    try {
      const res = await trabajadoresService.exportarMuestra(seed);
      const url = URL.createObjectURL(res.data);
      const hoy = new Date().toISOString().slice(0, 10);
      const a   = document.createElement('a');
      a.href     = url;
      a.download = `muestra_nom035_${hoy}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      // Si el servidor devolvió un blob con el error (4xx/5xx), leerlo para debuggear
      if (err?.response?.data instanceof Blob) {
        err.response.data.text().then(t =>
          console.error(`Error HTTP ${err.response.status} al exportar:`, t.slice(0, 1000))
        );
      } else {
        console.error('Error al exportar Excel:', err?.message || err);
      }
      alert('No se pudo generar el archivo. Intenta de nuevo.');
    } finally {
      setExportando(false);
    }
  };

  const filteredSugeridos = () => {
    if (!sugeridos?.trabajadores) return [];
    let list = sugeridos.trabajadores;
    if (busqueda.trim()) {
      const q = busqueda.toLowerCase();
      list = list.filter(w =>
        w.nombre_completo.toLowerCase().includes(q) ||
        w.area.toLowerCase().includes(q) ||
        w.puesto?.toLowerCase().includes(q) ||
        w.num_empleado?.toLowerCase().includes(q),
      );
    }
    const fn = SORT_KEYS[sortKey];
    list = [...list].sort((a, b) => fn(a, b) * (sortAsc ? 1 : -1));
    return list;
  };

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Calculadora NOM-035</h1>
          <p className={styles.subtitle}>
            Muestra estadísticamente representativa calculada a partir de los trabajadores activos del tenant,
            con desglose proporcional por las dimensiones requeridas por la NOM-035-STPS-2018.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', flexShrink: 0 }}>
          {data && (
            <button className="nom-btn nom-btn-ghost" onClick={exportarExcel} disabled={exportando}>
              {exportando ? <Loader2 size={14} className="nom-spin" /> : <Download size={14} />}
              {exportando ? 'Generando…' : 'Exportar Excel'}
            </button>
          )}
          <button className="nom-btn nom-btn-ghost" onClick={fetchData} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'nom-spin' : ''} />
            Actualizar
          </button>
        </div>
      </div>

      {loading ? (
        <div className={styles.loadingWrap}>
          <Loader2 size={32} className="nom-spin" />
          <span>Calculando muestra…</span>
        </div>
      ) : error ? (
        <div className={styles.errorWrap}>
          <Calculator size={36} strokeWidth={1.25} />
          <p>{error}</p>
          <button className="nom-btn nom-btn-primary" onClick={fetchData}>Reintentar</button>
        </div>
      ) : !data || data.N === 0 ? (
        <div className={styles.errorWrap}>
          <Users size={36} strokeWidth={1.25} />
          <p>No hay trabajadores activos registrados en este tenant.</p>
        </div>
      ) : (
        <>
          {/* ── Hero ── */}
          <div className={`nom-card ${styles.heroCard}`}>
            <div className={styles.heroLeft}>
              <div className={styles.heroKpi}>
                <div className={styles.heroNum}>{data.N.toLocaleString('es-MX')}</div>
                <div className={styles.heroLabel}>trabajadores activos (N)</div>
              </div>
              <div className={styles.heroDivider}>→</div>
              <div className={styles.heroKpi}>
                <div className={`${styles.heroNum} ${styles.heroNumAccent}`}>
                  {data.n.toLocaleString('es-MX')}
                </div>
                <div className={styles.heroLabel}>muestra representativa (n)</div>
              </div>
            </div>
            <div className={styles.heroPills}>
              <div className={styles.heroPill}>
                <Target size={13} />
                <span>{data.pct}% de la plantilla</span>
              </div>
              <div className={styles.heroPill}>
                <PieChart size={13} />
                <span>Confianza 95% · Error ±5%</span>
              </div>
              <div className={`${styles.heroPill} ${styles.heroPillAccent}`}>
                <Users size={13} />
                <span>{(data.N - data.n).toLocaleString('es-MX')} no requeridos</span>
              </div>
              <div className={styles.heroPill} style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '11px' }}>
                <Calculator size={12} />
                <span>n = ⌈0.9604N / (0.0025(N−1) + 0.9604)⌉</span>
              </div>
            </div>
          </div>

          {/* ── Grid de estratos ── */}
          <div className={styles.estratosGrid}>
            {ESTRATOS_CFG.map(cfg => (
              <EstratoCard
                key={cfg.key}
                cfg={cfg}
                filas={data.estratos[cfg.key] || []}
                n={data.n}
              />
            ))}
          </div>

          {/* ── Lista de sugeridos ── */}
          <div className={`nom-card ${styles.sugeridosCard}`}>
            <button
              className={styles.sugeridosToggle}
              onClick={() => setListaAbierta(v => !v)}
            >
              <div className={styles.sugeridosTitleWrap}>
                <div className={styles.sugeridosIcon}>
                  <ListChecks size={16} strokeWidth={1.75} />
                </div>
                <div>
                  <div className={styles.sugeridosTitle}>Trabajadores sugeridos para encuestar</div>
                  <div className={styles.sugeridosSub}>
                    Selección aleatoria estratificada por área · {sugeridos?.trabajadores?.length ?? '—'} de {data.n} trabajadores
                  </div>
                </div>
              </div>
              <div className={styles.sugeridosToggleRight}>
                {listaAbierta
                  ? <ChevronUp size={16} strokeWidth={2} />
                  : <ChevronDown size={16} strokeWidth={2} />}
              </div>
            </button>

            {listaAbierta && (
            <div className={styles.sugeridosBody}>
              <div className={styles.sugeridosHeader}>
                <div className={styles.sugeridosActions}>
                  <button className="nom-btn nom-btn-ghost" onClick={regenerar} disabled={loadingSug} title="Nueva selección aleatoria">
                    <Shuffle size={14} className={loadingSug ? 'nom-spin' : ''} />
                    Regenerar
                  </button>
                  <button className="nom-btn nom-btn-ghost" onClick={exportarExcel} disabled={exportando || !sugeridos}>
                    {exportando ? <Loader2 size={14} className="nom-spin" /> : <Download size={14} />}
                    Excel
                  </button>
                </div>
              </div>

            {/* Buscador */}
            <div className={styles.searchBar}>
              <Search size={15} className={styles.searchBarIcon} />
              <input
                className={styles.searchBarInput}
                placeholder="Buscar por nombre, área, puesto o número de empleado…"
                value={busqueda}
                onChange={e => setBusqueda(e.target.value)}
              />
              {busqueda && (
                <button className={styles.searchBarClear} onClick={() => setBusqueda('')}>
                  <X size={13} />
                </button>
              )}
              {busqueda && (
                <span className={styles.searchBarCount}>
                  {filteredSugeridos().length} resultado{filteredSugeridos().length !== 1 ? 's' : ''}
                </span>
              )}
            </div>

            {loadingSug ? (
              <div className={styles.sugeridosLoading}>
                <Loader2 size={22} className="nom-spin" />
              </div>
            ) : (() => {
              const rows = filteredSugeridos();
              const cols = [
                { k: null,               l: '#',            cls: styles.tdNum  },
                { k: 'num_empleado',     l: 'No. Emp.',     cls: styles.tdMono },
                { k: 'nombre_completo',  l: 'Nombre',       cls: styles.tdName },
                { k: 'area',             l: 'Área',         cls: null          },
                { k: 'puesto',           l: 'Puesto',       cls: styles.tdMuted},
                { k: 'sexo',             l: 'Sexo',         cls: null          },
                { k: 'edad',             l: 'Edad',         cls: styles.tdMono },
                { k: 'tipo_contratacion',l: 'Contratación', cls: styles.tdMuted},
              ];
              return (
                <div className={styles.sugeridosTableWrap}>
                  <table className={styles.sugeridosTable}>
                    <thead>
                      <tr>
                        {cols.map(({ k, l }, i) => (
                          <th key={i} onClick={k ? () => toggleSort(k) : undefined}>
                            {k ? (
                              <span className={styles.thInner}>
                                {l}
                                <span className={styles.thIcon}>
                                  {sortKey === k
                                    ? (sortAsc ? <ChevronUp size={11} /> : <ChevronDown size={11} />)
                                    : <ChevronDown size={11} style={{ opacity: 0.25 }} />}
                                </span>
                              </span>
                            ) : l}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.length === 0 ? (
                        <tr><td colSpan={cols.length} className={styles.tdEmpty}>Sin resultados</td></tr>
                      ) : rows.map((w, i) => (
                        <tr key={w.id}>
                          <td className={styles.tdNum}>{i + 1}</td>
                          <td className={styles.tdMono}>{w.num_empleado}</td>
                          <td className={styles.tdName}>{w.nombre_completo}</td>
                          <td><span className={styles.areaChip}>{w.area}</span></td>
                          <td className={styles.tdMuted}>{w.puesto || '—'}</td>
                          <td>{w.sexo}</td>
                          <td className={styles.tdMono}>{w.edad ?? '—'}</td>
                          <td className={styles.tdMuted}>{w.tipo_contratacion}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              );
            })()}
            </div>
            )}
          </div>

          {/* Nota metodológica */}
          <div className={styles.nota}>
            <Info size={13} />
            <span>
              Muestreo probabilístico estratificado proporcional para poblaciones finitas · NOM-035-STPS-2018.
              La muestra por grupo se calcula como ⌈(N_estrato / N) × n⌉, garantizando representatividad
              en cada dimensión. Los trabajadores sin dato en un campo se agrupan en "No especificado".
            </span>
          </div>
        </>
      )}
    </div>
  );
}
