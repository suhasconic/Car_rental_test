import { create } from 'zustand';
import { authAPI } from '../services/api';

const useAuthStore = create((set, get) => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    isLoading: false,
    error: null,

    login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
            const response = await authAPI.login(email, password);
            const { access_token } = response.data;

            localStorage.setItem('token', access_token);

            // Fetch user data
            const userResponse = await authAPI.getMe();
            const user = userResponse.data;

            localStorage.setItem('user', JSON.stringify(user));
            set({ token: access_token, user, isLoading: false });

            return { success: true, user };
        } catch (error) {
            const message = error.response?.data?.detail || 'Login failed';
            set({ error: message, isLoading: false });
            return { success: false, error: message };
        }
    },

    signup: async (data) => {
        set({ isLoading: true, error: null });
        try {
            await authAPI.signup(data);
            // Auto login after signup
            return await get().login(data.email, data.password);
        } catch (error) {
            const message = error.response?.data?.detail || 'Signup failed';
            set({ error: message, isLoading: false });
            return { success: false, error: message };
        }
    },

    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        set({ user: null, token: null });
    },

    refreshUser: async () => {
        try {
            const response = await authAPI.getMe();
            const user = response.data;
            localStorage.setItem('user', JSON.stringify(user));
            set({ user });
        } catch (error) {
            // If token is invalid, logout
            get().logout();
        }
    },

    isAuthenticated: () => !!get().token,
    isAdmin: () => get().user?.role === 'admin',
}));

export default useAuthStore;
