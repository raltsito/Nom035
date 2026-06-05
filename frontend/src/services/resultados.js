import api from './api';

export const resultadosService = {
  list:              (params = {}) => api.get('/resultados/', { params }),
  get:               (id)          => api.get(`/resultados/${id}/`),
  calcular:          (data)        => api.post('/resultados/calcular/', data),
  resumen:           (params = {}) => api.get('/resultados/resumen/', { params }),
  dominiosAgregados: (params = {}) => api.get('/resultados/dominios-agregados/', { params }),
  atencionClinica:   (params = {}) => api.get('/resultados/atencion-clinica/', { params }),
};

// URLs de documentos descargables (se abren con fetch + token para soportar PDF y fallback HTML)
export const documentosUrls = {
  informe:          (cicloId) => `/api/v1/documentos/informe-nom035/?ciclo_id=${cicloId}`,
  reportePsicologico: (cicloId, { anonimo = false, responsable = '' } = {}) => {
    const params = new URLSearchParams({ ciclo_id: cicloId });
    if (anonimo) params.set('anonimo', 'true');
    if (responsable) params.set('responsable', responsable);
    return `/api/v1/documentos/reporte-psicologico/?${params.toString()}`;
  },
};
