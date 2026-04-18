import api from './api';

const BASE = '/tenants/';

export const tenantsService = {
  list:          (q = '')      => api.get(BASE, { params: q ? { q } : {} }),
  get:           (id)          => api.get(`${BASE}${id}/`),
  create:        (data)        => api.post(BASE, data),
  update:        (id, data)    => api.patch(`${BASE}${id}/`, data),
  delete:        (id)          => api.delete(`${BASE}${id}/`),
  toggleActivo:  (id)          => api.post(`${BASE}${id}/toggle-activo/`),
  stats:         (id)          => api.get(`${BASE}${id}/stats/`),
  getUsuarios:   (id)          => api.get(`${BASE}${id}/usuarios/`),
  createUsuario: (id, data)    => api.post(`${BASE}${id}/usuarios/`, data),
};
