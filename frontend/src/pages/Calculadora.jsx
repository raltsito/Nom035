import { useState, useCallback } from 'react';
import {
  Calculator, Plus, Trash2, ChevronDown, ChevronUp,
  Info, Users, Target, PieChart, Download,
} from 'lucide-react';
import styles from './Calculadora.module.css';

/* ── Formula: n = 0.9604N / (0.0025(N-1) + 0.9604) ─────────────────────── */
function calcularMuestra(N) {
  if (!N || N < 1) return 0;
  return Math.ceil((0.9604 * N) / (0.0025 * (N - 1) + 0.9604));
}

/* ── Sample size for a stratum (proportional allocation) ────────────────── */
function muestraEstrato(nTotal, NTotal, NEstrato) {
  if (!NTotal || !NEstrato) return 0;
  return Math.ceil((NEstrato / NTotal) * nTotal);
}

/* ── Gauge ring ──────────────────────────────────────────────────────────── */
function PctRing({ pct, color = 'var(--nom-accent)' }) {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <svg width={90} height={90} viewBox="0 0 90 90">
      <circle cx={45} cy={45} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={8} />
      <circle
        cx={45} cy={45} r={r} fill="none"
        stroke={color} strokeWidth={8}
        strokeDasharray={`${dash} ${circ - dash}`}
        strokeLinecap="round"
        transform="rotate(-90 45 45)"
        style={{ transition: 'stroke-dasharray 0.5s ease' }}
      />
      <text x={45} y={49} textAnchor="middle" fontSize={14} fontWeight={700} fill="var(--nom-text)">
        {pct}%
      </text>
    </svg>
  );
}

/* ── Area row ────────────────────────────────────────────────────────────── */
function AreaRow({ area, index, nTotal, NTotal, onChange, onRemove }) {
  const n = muestraEstrato(nTotal, NTotal, area.trabajadores);
  const pct = area.trabajadores > 0 ? Math.round((area.trabajadores / NTotal) * 100) : 0;
  return (
    <div className={styles.areaRow}>
      <div className={styles.areaInputs}>
        <input
          className={styles.areaInput}
          placeholder="Nombre del área / departamento"
          value={area.nombre}
          onChange={e => onChange(index, 'nombre', e.target.value)}
        />
        <input
          className={`${styles.areaInput} ${styles.areaNum}`}
          type="number"
          min={1}
          placeholder="Trabajadores"
          value={area.trabajadores === '' ? '' : area.trabajadores}
          onChange={e => onChange(index, 'trabajadores', e.target.value === '' ? '' : Number(e.target.value))}
        />
      </div>
      <div className={styles.areaMeta}>
        {NTotal > 0 && area.trabajadores > 0 && (
          <>
            <span className={styles.areaChip}>{pct}% del total</span>
            <span className={styles.areaChip} style={{ background: 'rgba(3,196,206,0.12)', color: 'var(--nom-accent)' }}>
              {n} a encuestar
            </span>
          </>
        )}
      </div>
      <button className={styles.areaRemove} onClick={() => onRemove(index)} title="Eliminar área">
        <Trash2 size={14} />
      </button>
    </div>
  );
}

/* ── Main ────────────────────────────────────────────────────────────────── */
export default function Calculadora() {
  const [N, setN]             = useState('');
  const [areas, setAreas]     = useState([]);
  const [showFormula, setShowFormula] = useState(false);

  const Nval = Number(N) || 0;
  const n    = calcularMuestra(Nval);
  const pct  = Nval > 0 ? Math.round((n / Nval) * 100) : 0;

  /* total en áreas */
  const totalAreas = areas.reduce((s, a) => s + (Number(a.trabajadores) || 0), 0);
  const diff       = Nval - totalAreas;

  const addArea = () => setAreas(prev => [...prev, { nombre: '', trabajadores: '' }]);

  const changeArea = useCallback((i, key, val) => {
    setAreas(prev => prev.map((a, idx) => idx === i ? { ...a, [key]: val } : a));
  }, []);

  const removeArea = useCallback((i) => {
    setAreas(prev => prev.filter((_, idx) => idx !== i));
  }, []);

  /* CSV export */
  const exportCSV = () => {
    const rows = [
      ['Área / Departamento', 'Trabajadores totales', '% del total', 'Muestra requerida'],
      ...areas
        .filter(a => a.nombre || a.trabajadores)
        .map(a => {
          const nE = muestraEstrato(n, Nval, Number(a.trabajadores) || 0);
          const p  = Nval > 0 ? Math.round(((Number(a.trabajadores) || 0) / Nval) * 100) : 0;
          return [a.nombre || '(sin nombre)', a.trabajadores || 0, `${p}%`, nE];
        }),
      ['TOTAL', Nval, '100%', n],
    ];
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = `muestra_nom035_N${Nval}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const hasAreas = areas.length > 0;
  const areasValidas = areas.filter(a => (Number(a.trabajadores) || 0) > 0);

  return (
    <div className={styles.page}>

      {/* ---- Header ---- */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Calculadora NOM-035</h1>
          <p className={styles.subtitle}>
            Tamaño de muestra estadísticamente representativo para la evaluación de factores de riesgo psicosocial
          </p>
        </div>
      </div>

      {/* ---- Fórmula colapsable ---- */}
      <button className={styles.formulaToggle} onClick={() => setShowFormula(v => !v)}>
        <Info size={14} />
        Ver fórmula y parámetros estadísticos
        {showFormula ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {showFormula && (
        <div className={`nom-card ${styles.formulaCard}`}>
          <div className={styles.formulaMain}>
            <div className={styles.formulaDisplay}>
              <span className={styles.formulaN}>n =</span>
              <div className={styles.formulaFrac}>
                <div className={styles.formulaNum}>0.9604 × N</div>
                <div className={styles.formulaLine} />
                <div className={styles.formulaDen}>0.0025 (N − 1) + 0.9604</div>
              </div>
            </div>
          </div>
          <div className={styles.formulaParams}>
            <div className={styles.paramItem}>
              <span className={styles.paramKey}>N</span>
              <span className={styles.paramVal}>Población total de trabajadores</span>
            </div>
            <div className={styles.paramItem}>
              <span className={styles.paramKey}>n</span>
              <span className={styles.paramVal}>Tamaño de muestra mínimo requerido</span>
            </div>
            <div className={styles.paramItem}>
              <span className={styles.paramKey}>0.9604</span>
              <span className={styles.paramVal}>Z² × p × q = (1.96)² × 0.5 × 0.5 — nivel de confianza 95%</span>
            </div>
            <div className={styles.paramItem}>
              <span className={styles.paramKey}>0.0025</span>
              <span className={styles.paramVal}>e² = (0.05)² — margen de error del 5%</span>
            </div>
          </div>
        </div>
      )}

      {/* ---- Input principal ---- */}
      <div className={`nom-card ${styles.inputCard}`}>
        <div className={styles.inputSection}>
          <label className={styles.inputLabel}>
            <Users size={15} />
            Total de trabajadores en la empresa (N)
          </label>
          <div className={styles.inputRow}>
            <input
              className={styles.mainInput}
              type="number"
              min={1}
              placeholder="Ej. 120"
              value={N}
              onChange={e => setN(e.target.value)}
            />
            {Nval > 0 && (
              <span className={styles.inputHint}>
                {Nval.toLocaleString('es-MX')} trabajadores registrados
              </span>
            )}
          </div>
        </div>

        {/* Resultado */}
        {Nval > 0 && (
          <div className={styles.resultRow}>
            <div className={styles.resultKpi}>
              <PctRing pct={pct} />
              <div>
                <div className={styles.kpiNum}>{n}</div>
                <div className={styles.kpiLabel}>trabajadores a encuestar</div>
              </div>
            </div>

            <div className={styles.resultStats}>
              <div className={styles.statPill}>
                <Target size={13} />
                <span>{pct}% de la plantilla</span>
              </div>
              <div className={styles.statPill}>
                <PieChart size={13} />
                <span>Confianza 95% · Error ±5%</span>
              </div>
              <div className={styles.statPill} style={{ background: 'rgba(3,196,206,0.10)', color: 'var(--nom-accent)' }}>
                <Users size={13} />
                <span>{Nval - n} trabajadores no requeridos</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ---- Muestreo estratificado ---- */}
      {Nval > 0 && (
        <div className={`nom-card ${styles.estratoCard}`}>
          <div className={styles.estratoHeader}>
            <div>
              <h2 className={styles.estratoTitle}>Muestreo estratificado por área</h2>
              <p className={styles.estratoSub}>
                Distribuye la muestra proporcionalmente entre departamentos para mayor representatividad
              </p>
            </div>
            <div className={styles.estratoActions}>
              {hasAreas && areasValidas.length > 0 && (
                <button className="nom-btn nom-btn-ghost" onClick={exportCSV}>
                  <Download size={14} />
                  Exportar CSV
                </button>
              )}
              <button className="nom-btn nom-btn-primary" onClick={addArea}>
                <Plus size={14} />
                Agregar área
              </button>
            </div>
          </div>

          {!hasAreas ? (
            <div className={styles.estratoEmpty}>
              <Calculator size={32} strokeWidth={1.25} />
              <p>Agrega áreas o departamentos para calcular cuántos trabajadores encuestar en cada uno.</p>
              <button className="nom-btn nom-btn-primary" onClick={addArea}>
                <Plus size={14} />
                Agregar primera área
              </button>
            </div>
          ) : (
            <>
              <div className={styles.areaList}>
                {areas.map((area, i) => (
                  <AreaRow
                    key={i}
                    area={area}
                    index={i}
                    nTotal={n}
                    NTotal={Nval}
                    onChange={changeArea}
                    onRemove={removeArea}
                  />
                ))}
              </div>

              {/* Validación de totales */}
              {totalAreas > 0 && (
                <div className={`${styles.totalRow} ${diff < 0 ? styles.totalError : diff === 0 ? styles.totalOk : ''}`}>
                  <span>
                    Total capturado: <strong>{totalAreas.toLocaleString('es-MX')}</strong> de {Nval.toLocaleString('es-MX')}
                  </span>
                  {diff > 0 && <span className={styles.diffHint}>{diff} trabajadores sin asignar a un área</span>}
                  {diff < 0 && <span className={styles.diffError}>La suma excede N en {Math.abs(diff)} trabajadores</span>}
                  {diff === 0 && <span className={styles.diffOk}>✓ Suma correcta</span>}
                </div>
              )}

              {/* Tabla resumen */}
              {areasValidas.length > 0 && (
                <div className={styles.tableWrap}>
                  <table className={styles.table}>
                    <thead>
                      <tr>
                        <th>Área / Departamento</th>
                        <th>Trabajadores</th>
                        <th>% del total</th>
                        <th>Muestra requerida</th>
                        <th>Representación</th>
                      </tr>
                    </thead>
                    <tbody>
                      {areasValidas.map((area, i) => {
                        const nE  = muestraEstrato(n, Nval, Number(area.trabajadores));
                        const pE  = Math.round((Number(area.trabajadores) / Nval) * 100);
                        return (
                          <tr key={i}>
                            <td>{area.nombre || <span className={styles.unnamed}>(sin nombre)</span>}</td>
                            <td>{Number(area.trabajadores).toLocaleString('es-MX')}</td>
                            <td>
                              <div className={styles.barCell}>
                                <div className={styles.barTrack}>
                                  <div className={styles.barFill} style={{ width: `${pE}%` }} />
                                </div>
                                <span>{pE}%</span>
                              </div>
                            </td>
                            <td><strong className={styles.nResult}>{nE}</strong></td>
                            <td>
                              <div className={styles.barCell}>
                                <div className={styles.barTrack}>
                                  <div
                                    className={styles.barFill}
                                    style={{ width: `${pE}%`, background: 'var(--nom-accent)' }}
                                  />
                                </div>
                                <span>{nE} / {Number(area.trabajadores)}</span>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                    <tfoot>
                      <tr className={styles.tfootRow}>
                        <td><strong>TOTAL</strong></td>
                        <td><strong>{totalAreas.toLocaleString('es-MX')}</strong></td>
                        <td><strong>{Nval > 0 ? Math.round((totalAreas / Nval) * 100) : 0}%</strong></td>
                        <td>
                          <strong className={styles.nResult}>
                            {areasValidas.reduce((s, a) => s + muestraEstrato(n, Nval, Number(a.trabajadores)), 0)}
                          </strong>
                        </td>
                        <td></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* ---- Nota metodológica ---- */}
      <div className={styles.nota}>
        <Info size={13} />
        <span>
          Fórmula basada en muestreo probabilístico para poblaciones finitas con nivel de confianza del 95%
          y margen de error del 5%, conforme a los lineamientos de la NOM-035-STPS-2018.
          El resultado se redondea siempre al entero superior (ceil) para garantizar representatividad.
        </span>
      </div>
    </div>
  );
}
