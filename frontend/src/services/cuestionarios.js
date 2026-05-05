import api from './api';
import axios from 'axios';

export const cuestionariosService = {
  list:     ()   => api.get('/cuestionarios/'),
  get:      (id) => api.get(`/cuestionarios/${id}/`),
};

export const aplicacionesService = {
  list:             (params = {}) => api.get('/aplicaciones/', { params }),
  get:              (id)          => api.get(`/aplicaciones/${id}/`),
  delete:           (id)          => api.delete(`/aplicaciones/${id}/`),
  limpiarRespuestas:(id)          => api.delete(`/aplicaciones/${id}/limpiar-respuestas/`),
  progreso:         (params = {}) => api.get('/aplicaciones/progreso/', { params }),
  exportar:         (params = {}) => api.get('/aplicaciones/exportar/', { params, responseType: 'blob' }),
  exportarExcel:    (params = {}) => api.get('/aplicaciones/exportar-excel/', { params, responseType: 'blob' }),
};

export const guiaLinksService = {
  list:        (params = {}) => api.get('/guia-links/', { params }),
  crearLinks:  (data)        => api.post('/guia-links/crear-links/', data),
  delete:      (id)          => api.delete(`/guia-links/${id}/`),
};

// Acceso público (sin JWT) para la pantalla de respuesta
const publicApi = axios.create({ baseURL: '/api/v1' });

export const publicService = {
  getGuiaLink:  (token)        => publicApi.get(`/publica/guia/${token}/`),
  identificar:  (token, data)  => publicApi.post(`/publica/guia/${token}/identificar/`, data),
  confirmar:    (token, data)  => publicApi.post(`/publica/guia/${token}/confirmar/`, data),
  getAplicacion:(token)        => publicApi.get(`/publica/${token}/`),
  responder:    (token, data)  => publicApi.post(`/publica/${token}/responder/`, data),
};
