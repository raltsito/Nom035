import api from './api';

export const resultadosService = {
  list:              (params = {}) => api.get('/resultados/', { params }),
  get:               (id)          => api.get(`/resultados/${id}/`),
  calcular:          (data)        => api.post('/resultados/calcular/', data),
  resumen:           (params = {}) => api.get('/resultados/resumen/', { params }),
  dominiosAgregados: (params = {}) => api.get('/resultados/dominios-agregados/', { params }),
  atencionClinica:   (params = {}) => api.get('/resultados/atencion-clinica/', { params }),
};

// Documentos descargables del ciclo (DOCX / Excel), vía blob autenticado.
export const documentosService = {
  informeDiagnostico:   (cicloId) => api.get('/documentos/informe-diagnostico/', {
    params: { ciclo_id: cicloId }, responseType: 'blob',
  }),
  exportarRespuestas:   (cicloId) => api.get('/documentos/respuestas-nom035/', {
    params: { ciclo_id: cicloId }, responseType: 'blob',
  }),
};
