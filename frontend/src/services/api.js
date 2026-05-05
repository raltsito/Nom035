import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh_token');

      if (refresh) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_URL || '/api/v1'}/auth/token/refresh/`,
            { refresh }
          );
          // TokenRefreshView devuelve { access, refresh } sin wrapper
          const newAccess = data.access;
          if (!newAccess) throw new Error('no_access');
          localStorage.setItem('access_token', newAccess);
          if (data.refresh) {
            // ROTATE_REFRESH_TOKENS=True emite nuevo refresh — guardarlo
            localStorage.setItem('refresh_token', data.refresh);
          }
          original.headers.Authorization = `Bearer ${newAccess}`;
          return api(original);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;
