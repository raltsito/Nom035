import api from './api';

export const planAccionService = {
  list:    (params = {}) => api.get('/plan-accion/', { params }),
  get:     (id)          => api.get(`/plan-accion/${id}/`),
  create:  (data)        => api.post('/plan-accion/', data),
  update:  (id, data)    => api.patch(`/plan-accion/${id}/`, data),
  delete:  (id)          => api.delete(`/plan-accion/${id}/`),
};

export const accionesService = {
  list:    (params = {}) => api.get('/acciones/', { params }),
  create:  (data)        => api.post('/acciones/', data),
  update:  (id, data)    => api.patch(`/acciones/${id}/`, data),
  delete:  (id)          => api.delete(`/acciones/${id}/`),
};
