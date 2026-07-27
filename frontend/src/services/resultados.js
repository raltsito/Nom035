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

// Informe fotográfico: galería de las fotos tomadas antes de la Guía III.
// Solo se habilita en ciclos con cobertura suficiente (el backend decide).
export const fotosService = {
  resumen: (cicloId) => api.get('/informe-fotografico/resumen/', {
    params: { ciclo_id: cicloId },
  }),
  listado: (cicloId, page = 1, pageSize = 60) => api.get('/informe-fotografico/', {
    params: { ciclo_id: cicloId, page, page_size: pageSize },
  }),
  // La imagen de 640 px se pide solo al abrir una foto (blob autenticado).
  imagen:  (fotoId) => api.get(`/informe-fotografico/${fotoId}/imagen/`, {
    responseType: 'blob',
  }),
  anexo:   (cicloId) => api.get('/informe-fotografico/anexo/', {
    params: { ciclo_id: cicloId }, responseType: 'blob',
  }),
};
