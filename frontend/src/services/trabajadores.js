import api from './api';

const BASE = '/trabajadores/';
const CICLOS = '/ciclos/';

export const trabajadoresService = {
  list:        (params = {}) => api.get(BASE, { params }),
  get:         (id)          => api.get(`${BASE}${id}/`),
  create:      (data)        => api.post(BASE, data),
  update:      (id, data)    => api.patch(`${BASE}${id}/`, data),
  delete:      (id)          => api.delete(`${BASE}${id}/`),
  toggleActivo:(id)          => api.post(`${BASE}${id}/toggle-activo/`),
  importarExcel: (file, tenantId) => {
    const form = new FormData();
    form.append('archivo', file);
    const params = tenantId ? `?tenant_id=${tenantId}` : '';
    return api.post(`${BASE}importar-excel/${params}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const ciclosService = {
  list:           ()         => api.get(CICLOS),
  create:         (data)     => api.post(CICLOS, data),
  update:         (id, data) => api.patch(`${CICLOS}${id}/`, data),
  delete:         (id)       => api.delete(`${CICLOS}${id}/`),
  avanzarEstado:  (id)       => api.post(`${CICLOS}${id}/avanzar-estado/`),
};
