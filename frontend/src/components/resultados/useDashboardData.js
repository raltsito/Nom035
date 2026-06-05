import { useState, useEffect, useCallback } from 'react';
import { resultadosService } from '../../services/resultados';

// ---------------------------------------------------------------------------
// Constantes
// ---------------------------------------------------------------------------

const RISK_WEIGHT = { nulo: 0, bajo: 1, medio: 2, alto: 3, muy_alto: 4 };

// 5 macro-dimensiones NOM-035 con sus dominios correspondientes
const RADAR_DIMS = [
  { subject: 'Condiciones\nAmbientales',    claves: ['D1'] },
  { subject: 'Factores de\nla Actividad',   claves: ['D2', 'D3', 'D4'] },
  { subject: 'Organización\ndel Tiempo',    claves: ['D5'] },
  { subject: 'Liderazgo y\nRelaciones',     claves: ['D9', 'D10'] },
  { subject: 'Entorno\nOrganizacional',     claves: ['D6', 'D7', 'D8', 'D11', 'D12'] },
];

// ---------------------------------------------------------------------------
// Utilidades
// ---------------------------------------------------------------------------

function weightedRiskScore(dist) {
  const total = Object.values(dist).reduce((a, b) => a + b, 0);
  if (!total) return 0;
  const sum = Object.entries(dist).reduce(
    (s, [cat, n]) => s + (RISK_WEIGHT[cat] ?? 0) * n, 0,
  );
  return sum / total;
}

function scoreToCategoria(score) {
  if (score <= 0.5) return 'nulo';
  if (score <= 1.5) return 'bajo';
  if (score <= 2.5) return 'medio';
  if (score <= 3.5) return 'alto';
  return 'muy_alto';
}

// ---------------------------------------------------------------------------
// Procesamiento principal
// ---------------------------------------------------------------------------

function procesarDatos(resultados, resumen, dominiosAgregados, atencionClinica) {
  const distIII = resumen.guia_iii?.distribucion ?? resumen.distribucion ?? {};

  // ---- Chart 1: Gauge de riesgo global (solo Guía III) -------------------
  const riskScore = weightedRiskScore(distIII);
  const riskCat   = scoreToCategoria(riskScore);
  const riskPct   = riskScore <= 1
    ? 0
    : Math.min(100, Math.round(((riskScore - 1) / 3) * 100));

  // ---- Índice de dominios por clave --------------------------------------
  const dominioMap = Object.fromEntries(
    dominiosAgregados.map(d => [d.dominio_clave, d]),
  );

  // ---- Chart 2: Radar de 5 macro-dimensiones (datos reales) --------------
  const radar = RADAR_DIMS.map(dim => {
    const doms = dim.claves.map(k => dominioMap[k]).filter(Boolean);
    const pcts = doms.map(d => d.pct_promedio);
    const pct  = pcts.length
      ? Math.round(pcts.reduce((a, b) => a + b, 0) / pcts.length)
      : 0;
    return { subject: dim.subject, valor: pct, fullMark: 100 };
  });

  // ---- Chart 3: Bar de 14 dominios (datos reales) ------------------------
  const dominios = [...dominiosAgregados].sort((a, b) =>
    a.dominio_clave.localeCompare(b.dominio_clave, undefined, { numeric: true }),
  );

  // ---- Chart 4: Violencia laboral — D12 real -----------------------------
  const d12    = dominioMap['D12'];
  const violPct = d12?.pct_promedio ?? 0;
  const violCat = d12?.categoria_modal ?? 'nulo';
  const violencia = {
    data: [
      { name: 'Riesgo detectado', value: violPct },
      { name: 'Sin riesgo',       value: Math.max(0, 100 - violPct) },
    ],
    categoria: violCat,
    pct:       violPct,
  };

  // ---- Chart 5: Stacked bar por perfil demográfico (tipo_puesto) ---------
  const tipoPuestoMap = {};
  resultados
    .filter(r => r.cuestionario_clave === 'III')
    .forEach(r => {
      const perfil = r.trabajador_tipo_puesto || 'Sin clasificar';
      if (!tipoPuestoMap[perfil]) {
        tipoPuestoMap[perfil] = { perfil, nulo: 0, bajo: 0, medio: 0, alto: 0, muy_alto: 0 };
      }
      tipoPuestoMap[perfil][r.categoria] = (tipoPuestoMap[perfil][r.categoria] ?? 0) + 1;
    });
  const distData = Object.values(tipoPuestoMap);

  // ---- Chart 6: Barras por área (Guía III) --------------------------------
  const areaMap = {};
  resultados
    .filter(r => r.cuestionario_clave === 'III')
    .forEach(r => {
      const area = r.trabajador_area || 'Sin área';
      if (!areaMap[area]) {
        areaMap[area] = { area, nulo: 0, bajo: 0, medio: 0, alto: 0, muy_alto: 0 };
      }
      areaMap[area][r.categoria] = (areaMap[area][r.categoria] ?? 0) + 1;
    });
  const areas = Object.values(areaMap);

  // ---- Top 3 dominios con mayor riesgo (para CardTop3Dominios) -----------
  const PESO_NIVEL = { nulo: 0, bajo: 1, medio: 2, alto: 3, muy_alto: 4 };
  const top3 = [...dominiosAgregados]
    .filter(d => d.puntaje_promedio > 0)
    .sort((a, b) => {
      const pa = PESO_NIVEL[a.categoria_modal] ?? 0;
      const pb = PESO_NIVEL[b.categoria_modal] ?? 0;
      if (pb !== pa) return pb - pa;
      return b.pct_promedio - a.pct_promedio;
    })
    .slice(0, 3);

  return {
    riesgoGlobal:    { score: riskScore, categoria: riskCat, pct: riskPct },
    radar,
    dominios,
    violencia,
    distData,
    areas,
    top3,
    atencionClinica: atencionClinica ?? [],
    resumen,
  };
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useDashboardData(cicloId) {
  const [loading, setLoading] = useState(false);
  const [data,    setData]    = useState(null);
  const [error,   setError]   = useState(null);

  const fetch = useCallback(async () => {
    if (!cicloId) { setData(null); return; }
    setLoading(true);
    setError(null);
    try {
      const params = { ciclo_id: cicloId };

      // 4 requests en paralelo — sin N requests individuales por trabajador
      const [listRes, resumenRes, dominiosRes, atencionRes] = await Promise.all([
        resultadosService.list(params),
        resultadosService.resumen(params),
        resultadosService.dominiosAgregados(params),
        resultadosService.atencionClinica(params),
      ]);

      const resultados        = listRes.data.data     ?? [];
      const resumen           = resumenRes.data.data  ?? {};
      const dominiosAgregados = dominiosRes.data.data ?? [];
      const atencionClinica   = atencionRes.data.data ?? [];

      setData(procesarDatos(resultados, resumen, dominiosAgregados, atencionClinica));
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }, [cicloId]);

  useEffect(() => { fetch(); }, [fetch]);

  return { loading, data, error, refetch: fetch };
}
