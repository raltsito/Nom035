import api from './api';

export const resultadosService = {
  list:     (params = {}) => api.get('/resultados/', { params }),
  get:      (id)          => api.get(`/resultados/${id}/`),
  calcular: (data)        => api.post('/resultados/calcular/', data),
  resumen:  (params = {}) => api.get('/resultados/resumen/', { params }),
};
