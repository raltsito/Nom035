import api from './api';

export const configuracionService = {
  get:    ()     => api.get('/tenants/mi-empresa/'),
  update: (data) => api.patch('/tenants/mi-empresa/', data),
};
