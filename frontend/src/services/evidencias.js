import api from './api';

const BASE = '/evidencias/';

export const evidenciasService = {
  list:     (params = {}) => api.get(BASE, { params }),
  get:      (id)          => api.get(`${BASE}${id}/`),
  delete:   (id)          => api.delete(`${BASE}${id}/`),

  upload: (formData) =>
    api.post(BASE, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};
