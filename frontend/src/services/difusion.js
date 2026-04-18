import api from './api';

export const difusionService = {
  list:   (params = {}) => api.get('/actividades-difusion/', { params }),
  get:    (id)          => api.get(`/actividades-difusion/${id}/`),
  create: (data)        => api.post('/actividades-difusion/', data),
  update: (id, data)    => api.patch(`/actividades-difusion/${id}/`, data),
  delete: (id)          => api.delete(`/actividades-difusion/${id}/`),
};
