import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
    LayoutDashboard, Car, Calendar, Trophy, Users,
    ArrowRight, TrendingUp, AlertTriangle, CheckCircle
} from 'lucide-react';
import { adminAPI } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function AdminDashboard() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboard();
    }, []);

    const fetchDashboard = async () => {
        try {
            const response = await adminAPI.getDashboard();
            setStats(response.data);
        } catch (err) {
            console.error('Failed to fetch dashboard:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <LoadingSpinner text="Loading dashboard..." />;
    }

    const cards = [
        {
            title: 'Users',
            icon: Users,
            gradient: 'from-blue-500 to-indigo-600',
            stats: [
                { label: 'Total', value: stats?.users?.total || 0 },
                { label: 'Active', value: stats?.users?.active || 0 },
                { label: 'Blocked', value: stats?.users?.blocked || 0, danger: true },
            ],
            link: '/admin/users',
        },
        {
            title: 'Fleet',
            icon: Car,
            gradient: 'from-emerald-500 to-teal-600',
            stats: [
                { label: 'Total Cars', value: stats?.cars?.total || 0 },
                { label: 'Active', value: stats?.cars?.active || 0 },
                { label: 'Inactive', value: stats?.cars?.inactive || 0 },
            ],
            link: '/admin/cars',
        },
        {
            title: 'Bookings',
            icon: Calendar,
            gradient: 'from-amber-500 to-orange-600',
            stats: [
                { label: 'Pending', value: stats?.bookings?.pending || 0, highlight: true },
                { label: 'Active', value: stats?.bookings?.active || 0 },
            ],
            link: '/admin/bookings',
        },
        {
            title: 'Auctions',
            icon: Trophy,
            gradient: 'from-purple-500 to-pink-600',
            stats: [
                { label: 'Active', value: stats?.auctions?.active || 0, highlight: true },
            ],
            link: '/admin/auctions',
        },
    ];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                        <LayoutDashboard className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
                        <p className="text-gray-400">Manage your car rental platform</p>
                    </div>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {cards.map((card, index) => (
                    <Link key={index} to={card.link} className="glass-card group hover:scale-[1.02] transition-transform">
                        <div className="flex items-center justify-between mb-4">
                            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.gradient} flex items-center justify-center shadow-lg`}>
                                <card.icon className="w-6 h-6 text-white" />
                            </div>
                            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-white group-hover:translate-x-1 transition-all" />
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-3">{card.title}</h3>
                        <div className="space-y-2">
                            {card.stats.map((stat, i) => (
                                <div key={i} className="flex items-center justify-between text-sm">
                                    <span className="text-gray-400">{stat.label}</span>
                                    <span className={`font-semibold ${stat.danger ? 'text-red-400' : stat.highlight ? 'text-amber-400' : 'text-white'}`}>
                                        {stat.value}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </Link>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="glass-card">
                <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <Link
                        to="/admin/bookings?status=pending"
                        className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 hover:bg-amber-500/20 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <Calendar className="w-5 h-5 text-amber-400" />
                            <div>
                                <p className="text-white font-medium">Pending Approvals</p>
                                <p className="text-amber-400 text-sm">{stats?.bookings?.pending || 0} waiting</p>
                            </div>
                        </div>
                    </Link>

                    <Link
                        to="/admin/auctions?status=active"
                        className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/30 hover:bg-purple-500/20 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <Trophy className="w-5 h-5 text-purple-400" />
                            <div>
                                <p className="text-white font-medium">Active Auctions</p>
                                <p className="text-purple-400 text-sm">{stats?.auctions?.active || 0} running</p>
                            </div>
                        </div>
                    </Link>

                    <Link
                        to="/admin/cars"
                        className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <Car className="w-5 h-5 text-emerald-400" />
                            <div>
                                <p className="text-white font-medium">Add New Car</p>
                                <p className="text-emerald-400 text-sm">Expand your fleet</p>
                            </div>
                        </div>
                    </Link>

                    <Link
                        to="/admin/users"
                        className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 hover:bg-blue-500/20 transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <TrendingUp className="w-5 h-5 text-blue-400" />
                            <div>
                                <p className="text-white font-medium">Trust Leaderboard</p>
                                <p className="text-blue-400 text-sm">View top drivers</p>
                            </div>
                        </div>
                    </Link>
                </div>
            </div>

            {/* Rides Active */}
            {stats?.rides?.active > 0 && (
                <div className="mt-6 p-4 rounded-xl bg-blue-500/10 border border-blue-500/30">
                    <div className="flex items-center gap-3">
                        <CheckCircle className="w-5 h-5 text-blue-400" />
                        <p className="text-blue-400">
                            <span className="font-semibold">{stats?.rides?.active}</span> ride(s) currently in progress
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
