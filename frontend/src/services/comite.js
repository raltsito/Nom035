import api from './api';

export const comiteService = {
  list:   (params = {}) => api.get('/comite/', { params }),
  get:    (id)          => api.get(`/comite/${id}/`),
  create: (data)        => api.post('/comite/', data),
  update: (id, data)    => api.patch(`/comite/${id}/`, data),
  delete: (id)          => api.delete(`/comite/${id}/`),
};

export const miembrosService = {
  create: (data)       => api.post('/miembros-comite/', data),
  update: (id, data)   => api.patch(`/miembros-comite/${id}/`, data),
  delete: (id)         => api.delete(`/miembros-comite/${id}/`),
};

export const dc3Service = {
  create: (data) => api.post('/dc3/', data),
  delete: (id)   => api.delete(`/dc3/${id}/`),
};
