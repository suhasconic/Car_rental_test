import { useState, useEffect } from 'react';
import { User, Mail, Phone, Shield, Car, Star, AlertTriangle, TrendingUp } from 'lucide-react';
import useAuthStore from '../store/authStore';
import TrustBadge from '../components/TrustBadge';

export default function Profile() {
    const { user, refreshUser } = useAuthStore();
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        refreshUser();
    }, []);

    const stats = [
        { label: 'Total Rides', value: user?.total_rides || 0, icon: Car, color: 'text-blue-400' },
        { label: 'Avg Rating', value: parseFloat(user?.avg_rating || 0).toFixed(1), icon: Star, color: 'text-yellow-400' },
        { label: 'Damage Reports', value: user?.damage_count || 0, icon: AlertTriangle, color: 'text-red-400' },
        { label: 'Rash Incidents', value: user?.rash_count || 0, icon: AlertTriangle, color: 'text-orange-400' },
    ];

    return (
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-bold text-white mb-8">My Profile</h1>

            {/* Profile Card */}
            <div className="glass-card mb-8">
                <div className="flex flex-col sm:flex-row items-center gap-6">
                    <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center shadow-lg">
                        <span className="text-3xl font-bold text-white">
                            {user?.name?.charAt(0).toUpperCase()}
                        </span>
                    </div>

                    <div className="text-center sm:text-left flex-1">
                        <h2 className="text-2xl font-bold text-white mb-1">{user?.name}</h2>
                        <div className="flex flex-wrap justify-center sm:justify-start gap-4 text-gray-400 text-sm">
                            <span className="flex items-center gap-1">
                                <Mail className="w-4 h-4" />
                                {user?.email}
                            </span>
                            {user?.phone && (
                                <span className="flex items-center gap-1">
                                    <Phone className="w-4 h-4" />
                                    {user?.phone}
                                </span>
                            )}
                        </div>
                    </div>

                    <div className="text-center">
                        <TrustBadge score={user?.trust_score} size="lg" showLabel />
                    </div>
                </div>
            </div>

            {/* Trust Score Breakdown */}
            <div className="glass-card mb-8">
                <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-primary-400" />
                    Trust Score Breakdown
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    {stats.map((stat, index) => (
                        <div key={index} className="p-4 rounded-xl bg-white/5 text-center">
                            <stat.icon className={`w-6 h-6 ${stat.color} mx-auto mb-2`} />
                            <p className="text-2xl font-bold text-white">{stat.value}</p>
                            <p className="text-gray-400 text-sm">{stat.label}</p>
                        </div>
                    ))}
                </div>

                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                    <p className="text-sm text-center text-gray-400 font-mono">
                        Trust Score = ({parseFloat(user?.avg_rating || 0).toFixed(1)} × 20) + ({user?.total_rides || 0} × 0.5) - ({user?.damage_count || 0} × 15) - ({user?.rash_count || 0} × 10) = <span className="text-primary-400 font-bold">{parseFloat(user?.trust_score || 0).toFixed(1)}</span>
                    </p>
                </div>
            </div>

            {/* Trust Level Explanation */}
            <div className="glass-card">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-emerald-400" />
                    How to Improve Your Trust Score
                </h3>

                <div className="space-y-4">
                    <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                            <Star className="w-4 h-4 text-emerald-400" />
                        </div>
                        <div>
                            <p className="text-white font-medium">Get High Ratings</p>
                            <p className="text-gray-400 text-sm">Each 5-star ride adds +20 to your score formula</p>
                        </div>
                    </div>

                    <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                            <Car className="w-4 h-4 text-blue-400" />
                        </div>
                        <div>
                            <p className="text-white font-medium">Complete More Rides</p>
                            <p className="text-gray-400 text-sm">Each completed ride adds +0.5 to your score</p>
                        </div>
                    </div>

                    <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center flex-shrink-0">
                            <AlertTriangle className="w-4 h-4 text-red-400" />
                        </div>
                        <div>
                            <p className="text-white font-medium">Avoid Damage & Rash Driving</p>
                            <p className="text-gray-400 text-sm">Damage reports cost -15, rash driving costs -10</p>
                        </div>
                    </div>
                </div>

                {user?.trust_score < 30 && (
                    <div className="mt-6 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
                        <p className="text-amber-400 text-sm">
                            ⚠️ Your trust score is below 30. This means in auctions, you'll compete primarily on offer price rather than trust-weighted scoring. Improve your score for better chances!
                        </p>
                    </div>
                )}

                {user?.is_blocked && (
                    <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30">
                        <p className="text-red-400 text-sm">
                            🚫 Your account is currently blocked. Please contact support to resolve this.
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
