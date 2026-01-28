import { useState, useEffect } from 'react';
import { Users, Trophy, Ban, CheckCircle, Shield, AlertTriangle } from 'lucide-react';
import { adminAPI } from '../../services/api';
import TrustBadge from '../../components/TrustBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function AdminUsers() {
    const [users, setUsers] = useState([]);
    const [leaderboard, setLeaderboard] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showBlocked, setShowBlocked] = useState(false);

    useEffect(() => {
        fetchData();
    }, [showBlocked]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [usersRes, leaderboardRes] = await Promise.all([
                adminAPI.listUsers(showBlocked),
                adminAPI.getLeaderboard()
            ]);
            setUsers(usersRes.data);
            setLeaderboard(leaderboardRes.data);
        } catch (err) {
            console.error('Failed to fetch users:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleBlock = async (userId) => {
        if (!confirm('Are you sure you want to block this user?')) return;
        try {
            await adminAPI.blockUser(userId);
            await fetchData();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to block user');
        }
    };

    const handleUnblock = async (userId) => {
        try {
            await adminAPI.unblockUser(userId);
            await fetchData();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to unblock user');
        }
    };

    if (loading) return <LoadingSpinner text="Loading users..." />;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white">User Management</h1>
                <p className="text-gray-400 mt-1">View trust leaderboard and manage users</p>
            </div>

            {/* Leaderboard */}
            <div className="glass-card mb-8">
                <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-amber-400" />
                    Trust Leaderboard - Top 10
                </h2>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="text-left text-gray-400 text-sm border-b border-white/10">
                                <th className="pb-3 px-2">Rank</th>
                                <th className="pb-3 px-2">User</th>
                                <th className="pb-3 px-2">Trust Score</th>
                                <th className="pb-3 px-2">Rides</th>
                                <th className="pb-3 px-2">Avg Rating</th>
                                <th className="pb-3 px-2">Incidents</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {leaderboard.map((user, index) => (
                                <tr key={user.id} className="hover:bg-white/5">
                                    <td className="py-3 px-2">
                                        <span className={`w-8 h-8 rounded-full inline-flex items-center justify-center font-bold ${index === 0 ? 'bg-amber-500 text-white' :
                                                index === 1 ? 'bg-gray-400 text-white' :
                                                    index === 2 ? 'bg-amber-700 text-white' :
                                                        'bg-white/10 text-gray-400'
                                            }`}>
                                            {index + 1}
                                        </span>
                                    </td>
                                    <td className="py-3 px-2">
                                        <span className="text-white font-medium">{user.name}</span>
                                    </td>
                                    <td className="py-3 px-2">
                                        <TrustBadge score={user.trust_score} />
                                    </td>
                                    <td className="py-3 px-2 text-white">{user.total_rides}</td>
                                    <td className="py-3 px-2 text-white">{parseFloat(user.avg_rating).toFixed(1)}⭐</td>
                                    <td className="py-3 px-2">
                                        {user.damage_count > 0 || user.rash_count > 0 ? (
                                            <span className="text-red-400">
                                                {user.damage_count}D / {user.rash_count}R
                                            </span>
                                        ) : (
                                            <span className="text-emerald-400">Clean</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* All Users */}
            <div className="glass-card">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                        <Users className="w-5 h-5" />
                        All Users
                    </h2>
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={showBlocked}
                            onChange={(e) => setShowBlocked(e.target.checked)}
                            className="w-5 h-5 rounded bg-white/10 border-white/20"
                        />
                        <span className="text-gray-300 text-sm">Show only blocked</span>
                    </label>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="text-left text-gray-400 text-sm border-b border-white/10">
                                <th className="pb-3 px-2">User</th>
                                <th className="pb-3 px-2">Email</th>
                                <th className="pb-3 px-2">Trust Score</th>
                                <th className="pb-3 px-2">Stats</th>
                                <th className="pb-3 px-2">Status</th>
                                <th className="pb-3 px-2">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {users.map((user) => (
                                <tr key={user.id} className={`hover:bg-white/5 ${user.is_blocked ? 'opacity-60' : ''}`}>
                                    <td className="py-3 px-2">
                                        <span className="text-white font-medium">{user.name}</span>
                                    </td>
                                    <td className="py-3 px-2 text-gray-400 text-sm">{user.email}</td>
                                    <td className="py-3 px-2">
                                        <TrustBadge score={user.trust_score} />
                                    </td>
                                    <td className="py-3 px-2 text-sm">
                                        <span className="text-white">{user.total_rides} rides</span>
                                        <span className="text-gray-400 mx-2">•</span>
                                        <span className="text-white">{parseFloat(user.avg_rating).toFixed(1)}⭐</span>
                                        {(user.damage_count > 0 || user.rash_count > 0) && (
                                            <>
                                                <span className="text-gray-400 mx-2">•</span>
                                                <span className="text-red-400">{user.damage_count + user.rash_count} incidents</span>
                                            </>
                                        )}
                                    </td>
                                    <td className="py-3 px-2">
                                        {user.is_blocked ? (
                                            <span className="inline-flex items-center gap-1 text-red-400 text-sm">
                                                <Ban className="w-4 h-4" />
                                                Blocked
                                            </span>
                                        ) : parseFloat(user.trust_score) < 30 ? (
                                            <span className="inline-flex items-center gap-1 text-amber-400 text-sm">
                                                <AlertTriangle className="w-4 h-4" />
                                                Low Trust
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center gap-1 text-emerald-400 text-sm">
                                                <CheckCircle className="w-4 h-4" />
                                                Active
                                            </span>
                                        )}
                                    </td>
                                    <td className="py-3 px-2">
                                        {user.is_blocked ? (
                                            <button
                                                onClick={() => handleUnblock(user.id)}
                                                className="text-emerald-400 hover:text-emerald-300 text-sm font-medium"
                                            >
                                                Unblock
                                            </button>
                                        ) : (
                                            <button
                                                onClick={() => handleBlock(user.id)}
                                                className="text-red-400 hover:text-red-300 text-sm font-medium"
                                            >
                                                Block
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
