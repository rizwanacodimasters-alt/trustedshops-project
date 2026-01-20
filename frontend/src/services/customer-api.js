import api from './api';

export const customerAPI = {
  // Dashboard
  getDashboard: () => api.get('/customer/dashboard'),
  
  // Reviews
  getMyReviews: (params) => api.get('/customer/reviews', { params }),
  
  // Favorites
  getFavorites: () => api.get('/customer/favorites'),
  addFavorite: (shopId) => api.post(`/customer/favorites/${shopId}`),
  removeFavorite: (shopId) => api.delete(`/customer/favorites/${shopId}`),
  
  // Notifications
  getNotifications: (unreadOnly = false) => api.get('/customer/notifications', { params: { unread_only: unreadOnly } }),
  markAsRead: (notificationId) => api.put(`/customer/notifications/${notificationId}/read`),
  
  // Profile
  getProfile: () => api.get('/customer/profile'),
  updateProfile: (data) => api.put('/customer/profile', data),
  changePassword: (data) => api.post('/customer/profile/change-password', data),
  deleteAccount: () => api.delete('/customer/profile/account')
};

export default customerAPI;
