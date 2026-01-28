import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, LogIn, AlertCircle } from 'lucide-react';
import useAuthStore from '../store/authStore';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { login, isLoading, error } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const result = await login(email, password);
        if (result.success) {
            if (result.user?.role === 'admin') {
                navigate('/admin');
            } else {
                navigate('/cars');
            }
        }
    };

    return (
        <div className="min-h-[calc(100vh-5rem)] flex items-center justify-center px-4 py-12">
            <div className="w-full max-w-md">
                <div className="glass-card">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 mb-4 shadow-lg shadow-primary-500/30">
                            <LogIn className="w-8 h-8 text-white" />
                        </div>
                        <h1 className="text-2xl font-bold text-white mb-2">Welcome Back</h1>
                        <p className="text-gray-400">Sign in to access your account</p>
                    </div>

                    {/* Error message */}
                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3">
                            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                            <p className="text-red-400 text-sm">{error}</p>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Email Address
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="input-field pl-12"
                                    placeholder="you@example.com"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field pl-12"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="btn-primary w-full text-white flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                <>
                                    Sign In
                                    <LogIn className="w-5 h-5" />
                                </>
                            )}
                        </button>
                    </form>

                    {/* Demo credentials */}
                    <div className="mt-6 p-4 rounded-xl bg-white/5 border border-white/10">
                        <p className="text-xs text-gray-400 text-center mb-2">Demo Credentials</p>
                        <div className="space-y-1 text-xs font-mono text-center">
                            <p className="text-gray-300">Admin: admin@surya.com / admin123</p>
                            <p className="text-gray-300">User: rahul@example.com / password123</p>
                        </div>
                    </div>

                    {/* Sign up link */}
                    <p className="mt-8 text-center text-gray-400">
                        Don't have an account?{' '}
                        <Link to="/signup" className="text-primary-400 hover:text-primary-300 font-medium">
                            Sign up
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
