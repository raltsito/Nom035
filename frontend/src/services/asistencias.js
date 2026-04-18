import api from './api';

export const reunionesService = {
  list:   (params = {}) => api.get('/reuniones/', { params }),
  get:    (id)          => api.get(`/reuniones/${id}/`),
  create: (data)        => api.post('/reuniones/', data),
  update: (id, data)    => api.patch(`/reuniones/${id}/`, data),
  delete: (id)          => api.delete(`/reuniones/${id}/`),
};

export const asistentesService = {
  create: (data)      => api.post('/asistentes/', data),
  update: (id, data)  => api.patch(`/asistentes/${id}/`, data),
  delete: (id)        => api.delete(`/asistentes/${id}/`),
};
