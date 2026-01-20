import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
};

// Shop API
export const shopAPI = {
  getShops: (params) => api.get('/shops', { params }),
  getShop: (id) => api.get(`/shops/${id}`),
  createShop: (data) => api.post('/shops', data),
  updateShop: (id, data) => api.put(`/shops/${id}`, data),
  deleteShop: (id) => api.delete(`/shops/${id}`),
};

// Review API
export const reviewAPI = {
  getReviews: (params) => api.get('/reviews', { params }),
  createReview: (data) => api.post('/reviews', data),
  updateReview: (id, data) => api.put(`/reviews/${id}`, data),
  deleteReview: (id) => api.delete(`/reviews/${id}`),
};

// Statistics API
export const statisticsAPI = {
  getStatistics: () => api.get('/statistics'),
};

// Order API
export const orderAPI = {
  getOrders: (params) => api.get('/orders', { params }),
  getOrder: (id) => api.get(`/orders/${id}`),
  createOrder: (data) => api.post('/orders', data),
};

// Dashboard API
export const dashboardAPI = {
  getUserDashboard: () => api.get('/dashboard/user'),
  getShopOwnerDashboard: () => api.get('/dashboard/shop-owner'),
};

// Shop Verification API
export const verificationAPI = {
  requestVerification: (shopId) => api.post(`/shop-verification/request/${shopId}`),
  getVerificationStatus: (shopId) => api.get(`/shop-verification/status/${shopId}`),
  getAllVerificationRequests: (statusFilter = 'pending') => api.get(`/shop-verification/all`, { params: { status_filter: statusFilter } }),
  approveVerification: (shopId) => api.post(`/shop-verification/approve/${shopId}`),
  rejectVerification: (shopId) => api.post(`/shop-verification/reject/${shopId}`),
};

// Security Monitoring API
export const securityAPI = {
  getLoginLogs: (params = {}) => api.get('/security/login-logs', { params }),
  getFailedLogins: (params = {}) => api.get('/security/failed-logins', { params }),
  getSuspiciousActivities: (params = {}) => api.get('/security/suspicious-activities', { params }),
  getIpTracking: (params = {}) => api.get('/security/ip-tracking', { params }),
  resolveAlert: (alertId) => api.post(`/security/resolve-alert/${alertId}`),
  getStatistics: (params = {}) => api.get('/security/statistics', { params }),
};

// Review Response API
export const reviewResponseAPI = {
  createResponse: (data) => api.post('/review-responses', data),
  getResponse: (reviewId) => api.get(`/review-responses/review/${reviewId}`),
  deleteResponse: (id) => api.delete(`/review-responses/${id}`),
};

// Review API extended with response functionality
reviewAPI.respondToReview = (reviewId, data) => api.post(`/review-responses`, { review_id: reviewId, ...data });

// Billing API
export const billingAPI = {
  getPlans: () => api.get('/billing/plans'),
  createCheckoutSession: (data) => api.post('/billing/checkout', data),
  getCheckoutStatus: (sessionId) => api.get(`/billing/checkout/status/${sessionId}`),
  getSubscription: () => api.get('/billing/subscription'),
  getTransactions: () => api.get('/billing/transactions'),
};

// Search API
export const searchAPI = {
  searchShops: (params) => api.get('/search/shops', { params }),
  getCategories: () => api.get('/search/categories'),
  getSuggestions: (q) => api.get('/search/suggestions', { params: { q } }),
};

// Admin APIs
export const adminAPI = {
  // Users
  getAllUsers: (params) => api.get('/admin/users', { params }),
  getUserDetail: (userId) => api.get(`/admin/users/${userId}`),
  updateUser: (userId, data) => api.put(`/admin/users/${userId}`, data),
  suspendUser: (userId, reason) => api.post(`/admin/users/${userId}/suspend`, { reason }),
  activateUser: (userId) => api.post(`/admin/users/${userId}/activate`),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  resetPassword: (userId, newPassword) => api.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword }),
  changeRole: (userId, newRole) => api.post(`/admin/users/${userId}/change-role`, { new_role: newRole }),
  terminateSession: (userId, sessionId) => api.post(`/admin/users/${userId}/sessions/${sessionId}/terminate`),
  terminateAllSessions: (userId) => api.post(`/admin/users/${userId}/sessions/terminate-all`),
  getLoginHistory: (userId, params) => api.get(`/admin/users/${userId}/login-history`, { params }),
  enable2FA: (userId) => api.post(`/admin/users/${userId}/2fa/enable`),
  disable2FA: (userId) => api.post(`/admin/users/${userId}/2fa/disable`),
  
  // Shops
  getAllShops: (params) => api.get('/admin/shops', { params }),
  getShopDetail: (shopId) => api.get(`/admin/shops/${shopId}`),
  updateShop: (shopId, data) => api.put(`/admin/shops/${shopId}`, data),
  verifyShop: (shopId, notes) => api.post(`/admin/shops/${shopId}/verify`, { notes }),
  suspendShop: (shopId, reason) => api.post(`/admin/shops/${shopId}/suspend`, { reason }),
  activateShop: (shopId) => api.post(`/admin/shops/${shopId}/activate`),
  deleteShop: (shopId) => api.delete(`/admin/shops/${shopId}`),
  banShop: (shopId, reason) => api.post(`/admin/shops/${shopId}/ban`, { reason }),
  
  // Dashboard
  getDashboardOverview: () => api.get('/admin/dashboard/overview'),
  getSecurityAlerts: () => api.get('/admin/dashboard/security-alerts'),
  resolveAlert: (alertId) => api.post(`/admin/dashboard/security-alerts/${alertId}/resolve`),
};

export default api;
