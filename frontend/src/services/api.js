import axios from 'axios';

// Use environment variable or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    signup: (data) => api.post('/auth/signup', data),
    login: (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        return api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
    },
    getMe: () => api.get('/auth/me'),
};

// Cars API
export const carsAPI = {
    list: (params = {}) => api.get('/cars', { params }),
    get: (id) => api.get(`/cars/${id}`),
    getAvailability: (id) => api.get(`/cars/${id}/availability`),
};

// Bookings API
export const bookingsAPI = {
    request: (data) => api.post('/bookings/request', data),
    getMy: (status = null) => api.get('/bookings/my', { params: { status } }),
    get: (id) => api.get(`/bookings/${id}`),
    cancel: (id) => api.post(`/bookings/${id}/cancel`),
};

// Auctions API
export const auctionsAPI = {
    list: (status = null) => api.get('/auctions', { params: { status } }),
    getMy: () => api.get('/auctions/my'),
    get: (id) => api.get(`/auctions/${id}`),
    bid: (id, offerPrice) => api.post(`/auctions/${id}/bid`, null, { params: { offer_price: offerPrice } }),
};

// Admin API
export const adminAPI = {
    getDashboard: () => api.get('/admin/dashboard'),

    // Cars
    addCar: (data) => api.post('/admin/cars', data),
    updateCar: (id, data) => api.put(`/admin/cars/${id}`, data),
    deleteCar: (id) => api.delete(`/admin/cars/${id}`),

    // Bookings
    listBookings: (status = null) => api.get('/admin/bookings', { params: { status } }),
    approveBooking: (id) => api.post(`/admin/bookings/${id}/approve`),
    rejectBooking: (id) => api.post(`/admin/bookings/${id}/reject`),

    // Rides
    startRide: (bookingId) => api.post(`/admin/bookings/${bookingId}/start-ride`),
    completeRide: (rideId) => api.post(`/admin/rides/${rideId}/complete`),
    rateRide: (rideId, data) => api.post(`/admin/rides/${rideId}/rate`, data),

    // Users
    listUsers: (blockedOnly = false) => api.get('/admin/users', { params: { blocked_only: blockedOnly } }),
    getLeaderboard: () => api.get('/admin/users/leaderboard'),
    blockUser: (id) => api.post(`/admin/users/${id}/block`),
    unblockUser: (id) => api.post(`/admin/users/${id}/unblock`),

    // Auctions
    listAuctions: (status = null) => api.get('/admin/auctions', { params: { status } }),
    closeAuction: (id) => api.post(`/admin/auctions/${id}/close`),
};

export default api;
