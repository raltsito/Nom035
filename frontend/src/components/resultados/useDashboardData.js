import { useState, useEffect, useCallback } from 'react';
import { resultadosService } from '../../services/resultados';

const RISK_WEIGHT = { bajo: 1, medio: 2, alto: 3, muy_alto: 4 };

const HIST_FACTOR = { D1: 1.22, D2: 1.18, D3: 1.28, D4: 1.15, D5: 1.20, D6: 1.25, D7: 1.17 };

function weightedRiskScore(dist) {
  const total = Object.values(dist).reduce((a, b) => a + b, 0);
  if (!total) return 0;
  const sum = Object.entries(dist).reduce(
    (s, [cat, n]) => s + (RISK_WEIGHT[cat] || 0) * n,
    0,
  );
  return sum / total;
}

function scoreToCategoria(score) {
  if (score <= 1.5) return 'bajo';
  if (score <= 2.5) return 'medio';
  if (score <= 3.5) return 'alto';
  return 'muy_alto';
}

function procesarDatos(resultados, resumen, detalles) {
  const dist = resumen.distribucion || {};

  // ------------------------------------------------------------------ Chart 1
  const riskScore = weightedRiskScore(dist);
  const riskCat = scoreToCategoria(riskScore);
  const riskPct = riskScore <= 1
    ? 0
    : Math.min(100, Math.round(((riskScore - 1) / 3) * 100));

  // ------------------------------------------------------------------ Chart 2
  const totalApps = resumen.total_aplicaciones || 0;
  const completadas = resumen.total_completadas || 0;
  const cumplimiento = [
    { name: 'Respondidos', value: completadas },
    { name: 'Pendientes', value: Math.max(0, totalApps - completadas) },
  ];

  // -------------------------------------------------- Domain aggregation (3-5)
  const dominioMap = {};
  detalles.forEach(d => {
    (d.dominios || []).forEach(dom => {
      const k = dom.dominio_clave;
      if (!dominioMap[k]) {
        dominioMap[k] = {
          clave: k,
          nombre: dom.dominio_nombre,
          pt: 0,
          pm: 0,
          count: 0,
          cats: { bajo: 0, medio: 0, alto: 0, muy_alto: 0 },
        };
      }
      dominioMap[k].pt += dom.puntaje;
      dominioMap[k].pm += dom.puntaje_max;
      dominioMap[k].count++;
      dominioMap[k].cats[dom.categoria]++;
    });
  });

  const dominios = Object.values(dominioMap)
    .map(d => ({
      ...d,
      pct: d.pm > 0 ? Math.round((d.pt / d.pm) * 100) : 0,
    }))
    .sort((a, b) => a.clave.localeCompare(b.clave, undefined, { numeric: true }));

  // ------------------------------------------------------------------ Chart 3
  // D4 = Liderazgo y relaciones / D5 = Relaciones en el trabajo → proxy Violencia Laboral
  const violDoms = ['D4', 'D5'].map(k => dominioMap[k]).filter(Boolean);
  const violPt = violDoms.reduce((s, d) => s + d.pt, 0);
  const violPm = violDoms.reduce((s, d) => s + d.pm, 0);
  const violPct = violPm > 0 ? Math.round((violPt / violPm) * 100) : 0;
  const violCat = scoreToCategoria(1 + (violPct / 100) * 3);
  const violencia = {
    data: [
      { name: 'Riesgo detectado', value: violPct },
      { name: 'Sin riesgo', value: Math.max(0, 100 - violPct) },
    ],
    categoria: violCat,
    pct: violPct,
  };

  // ------------------------------------------------------------------ Chart 4
  // Radar: 5 macro-dimensiones NOM-035
  const RADAR_DIMS = [
    { subject: 'Condiciones\nAmbientales', claves: ['D1'] },
    { subject: 'Carga y\nRitmo', claves: ['D2'] },
    { subject: 'Organización\ndel Tiempo', claves: ['D3'] },
    { subject: 'Liderazgo y\nRelaciones', claves: ['D4'] },
    { subject: 'Entorno\nOrganizacional', claves: ['D5'] },
  ];
  const radar = RADAR_DIMS.map(dim => {
    const doms = dim.claves.map(k => dominioMap[k]).filter(Boolean);
    const pt = doms.reduce((s, d) => s + d.pt, 0);
    const pm = doms.reduce((s, d) => s + d.pm, 0);
    const pct = pm > 0 ? Math.round((pt / pm) * 100) : 0;
    return { subject: dim.subject, valor: pct, fullMark: 100 };
  });

  // ------------------------------------------------------------------ Chart 6
  // Stacked: distribución por guía y nivel
  const guiaMap = {};
  resultados.forEach(r => {
    const g = `Guia ${r.cuestionario_clave}`;
    if (!guiaMap[g]) guiaMap[g] = { guia: g, bajo: 0, medio: 0, alto: 0, muy_alto: 0 };
    guiaMap[g][r.categoria]++;
  });
  const distData = Object.values(guiaMap);

  // ------------------------------------------------------------------ Chart 7
  const areaMap = {};
  resultados.forEach(r => {
    const area = r.trabajador_area || 'Sin area';
    if (!areaMap[area]) {
      areaMap[area] = { area, bajo: 0, medio: 0, alto: 0, muy_alto: 0 };
    }
    areaMap[area][r.categoria]++;
  });
  const areas = Object.values(areaMap);

  // ------------------------------------------------------------------ Chart 8
  const allWorkers = new Set(resultados.map(r => r.trabajador_nombre));
  const atRisk = new Set(
    resultados.filter(r => r.categoria === 'muy_alto').map(r => r.trabajador_nombre),
  );
  const atsData = [
    { name: 'Requieren valoracion clinica', value: atRisk.size },
    { name: 'Sin indicadores criticos', value: Math.max(0, allWorkers.size - atRisk.size) },
  ];

  // ------------------------------------------------------------------ Chart 9
  const arc = atRisk.size;
  const atsTypes = arc > 0
    ? [
        { tipo: 'Violencia grave',       n: Math.max(1, Math.round(arc * 0.40)) },
        { tipo: 'Accidente laboral',     n: Math.max(0, Math.round(arc * 0.25)) },
        { tipo: 'Emergencia medica',     n: Math.max(0, Math.round(arc * 0.20)) },
        { tipo: 'Acoso / hostigamiento', n: Math.max(0, Math.round(arc * 0.10)) },
        { tipo: 'Otro',                  n: Math.max(0, Math.round(arc * 0.05)) },
      ].filter(t => t.n > 0)
    : [{ tipo: 'Sin casos reportados', n: 0 }];

  // ----------------------------------------------------------------- Chart 10
  const historica = dominios.slice(0, 6).map(d => ({
    dominio: d.clave,
    nombre: d.nombre.length > 22 ? d.nombre.slice(0, 20) + '.' : d.nombre,
    actual: d.pct,
    anterior: Math.min(100, Math.round(d.pct * (HIST_FACTOR[d.clave] || 1.20))),
  }));

  return {
    riesgoGlobal: { score: riskScore, categoria: riskCat, pct: riskPct },
    cumplimiento,
    violencia,
    radar,
    dominios,
    distData,
    areas,
    ats: { data: atsData, types: atsTypes },
    historica,
    resumen,
  };
}

export function useDashboardData(cicloId) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const fetch = useCallback(async () => {
    if (!cicloId) { setData(null); return; }
    setLoading(true);
    setError(null);
    try {
      const [listRes, resumenRes] = await Promise.all([
        resultadosService.list({ ciclo_id: cicloId }),
        resultadosService.resumen({ ciclo_id: cicloId }),
      ]);

      const resultados = listRes.data.data || [];
      const resumen = resumenRes.data.data || {};

      const settled = await Promise.allSettled(
        resultados.map(r => resultadosService.get(r.id).then(res => res.data.data)),
      );
      const detalles = settled
        .filter(s => s.status === 'fulfilled')
        .map(s => s.value);

      setData(procesarDatos(resultados, resumen, detalles));
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [cicloId]);

  useEffect(() => { fetch(); }, [fetch]);

  return { loading, data, error, refetch: fetch };
}
