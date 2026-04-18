import api from './api';

export const notificacionesService = {
  list:        ()   => api.get('/notificaciones/'),
  markRead:    (id) => api.patch(`/notificaciones/${id}/`, { leida: true }),
  delete:      (id) => api.delete(`/notificaciones/${id}/`),
  marcarTodas: ()   => api.post('/notificaciones/marcar_leidas/'),
  generar:     ()   => api.post('/notificaciones/generar/'),
};
