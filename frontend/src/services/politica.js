import api from './api';

export const politicaService = {
  list:    (params = {}) => api.get('/politica/', { params }),
  get:     (id)          => api.get(`/politica/${id}/`),
  create:  (data)        => api.post('/politica/', data),
  update:  (id, data)    => api.patch(`/politica/${id}/`, data),
  delete:  (id)          => api.delete(`/politica/${id}/`),
  aprobar: (id)          => api.post(`/politica/${id}/aprobar/`),
};
