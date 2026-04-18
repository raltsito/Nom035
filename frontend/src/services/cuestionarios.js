import api from './api';
import axios from 'axios';

export const cuestionariosService = {
  list:     ()   => api.get('/cuestionarios/'),
  get:      (id) => api.get(`/cuestionarios/${id}/`),
};

export const aplicacionesService = {
  list:            (params = {}) => api.get('/aplicaciones/', { params }),
  get:             (id)          => api.get(`/aplicaciones/${id}/`),
  delete:          (id)          => api.delete(`/aplicaciones/${id}/`),
  crearMasivo:     (data)        => api.post('/aplicaciones/crear-masivo/', data),
  limpiarRespuestas: (id)        => api.delete(`/aplicaciones/${id}/limpiar-respuestas/`),
};

// Acceso público (sin JWT) para la pantalla de respuesta
const publicApi = axios.create({ baseURL: '/api/v1' });

export const publicService = {
  getAplicacion: (token)        => publicApi.get(`/publica/${token}/`),
  responder:     (token, data)  => publicApi.post(`/publica/${token}/responder/`, data),
};
