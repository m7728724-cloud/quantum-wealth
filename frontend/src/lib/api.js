import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('qw_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't redirect if already on login page
      if (!window.location.pathname.includes('/login')) {
        localStorage.removeItem('qw_token');
        localStorage.removeItem('qw_user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  login: (username, password) => api.post('/api/auth/login', { username, password }),
  me: () => api.get('/api/auth/me'),
};

export const usersAPI = {
  list: () => api.get('/api/users'),
  create: (data) => api.post('/api/users', data),
  updatePassword: (username, password) => api.put(`/api/users/${encodeURIComponent(username)}/password`, { password }),
  updateTinkoffToken: (username, tinkoffToken) =>
    api.put(`/api/users/${encodeURIComponent(username)}/tinkoff-token`, { tinkoff_token: tinkoffToken }),
};

// Portfolio
export const portfolioAPI = {
  getHoldings: () => api.get('/api/portfolio/holdings'),
  getHoldingsEnriched: () => api.get('/api/portfolio/holdings-enriched'),
  addHolding: (data) => api.post('/api/portfolio/holdings', data),
  deleteHolding: (id) => api.delete(`/api/portfolio/holdings/${id}`),
  resolveISIN: (isin) => api.post('/api/portfolio/resolve-isin', { isin }),
  getAllocation: () => api.get('/api/portfolio/allocation'),
};

// News
export const newsAPI = {
  getNews: (region) => api.get('/api/news', { params: { region } }),
  refreshNews: () => api.post('/api/news/refresh'),
};

// AI
export const aiAPI = {
  getInsight: (data) => api.post('/api/ai/portfolio-insight', data || {}),
};

// Signals
export const signalsAPI = {
  getSignals: (limit) => api.get('/api/signals', { params: { limit } }),
  deleteSignal: (id) => api.delete(`/api/signals/${id}`),
  sendWebhook: (data) => api.post('/api/signals/webhook', data),
  scanSignals: () => api.get('/api/signals/scan'),
  getPerformance: () => api.get('/api/signals/performance'),
  getSupportedPairs: () => api.get('/api/signals/supported-pairs'),
};

// Tinkoff
export const tinkoffAPI = {
  sync: () => api.post('/api/tinkoff/sync'),
  getStatus: () => api.get('/api/tinkoff/status'),
};

// Trades
export const tradesAPI = {
  getTrades: (resultFilter) => api.get('/api/trades', { params: { result_filter: resultFilter } }),
  createTrade: (data) => api.post('/api/trades', data),
  updateTrade: (id, data) => api.put(`/api/trades/${id}`, data),
  getStats: () => api.get('/api/trades/stats'),
};

// Memory
export const memoryAPI = {
  getMemory: (limit) => api.get('/api/memory', { params: { limit } }),
  createMemory: (data) => api.post('/api/memory', data),
};

// Safeguards
export const safeguardsAPI = {
  getRules: () => api.get('/api/safeguards'),
  generateRules: () => api.post('/api/safeguards/generate'),
  toggleRule: (id) => api.put(`/api/safeguards/${id}/toggle`),
  deleteRule: (id) => api.delete(`/api/safeguards/${id}`),
  addManual: (data) => api.post('/api/safeguards/manual', data),
};

// Dashboard
export const dashboardAPI = {
  getStats: () => api.get('/api/dashboard/stats'),
};

export default api;
