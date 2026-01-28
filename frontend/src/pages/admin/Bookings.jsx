import { useState, useEffect } from 'react';
import {
    Calendar, CheckCircle, XCircle, Play, Star,
    IndianRupee, Clock, Car
} from 'lucide-react';
import { format } from 'date-fns';
import { adminAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import TrustBadge from '../../components/TrustBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function AdminBookings() {
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('pending');
    const [ratingModal, setRatingModal] = useState(null);
    const [rating, setRating] = useState({ driving_rating: 5, damage_flag: false, rash_flag: false, notes: '' });

    useEffect(() => {
        fetchBookings();
    }, [filter]);

    const fetchBookings = async () => {
        setLoading(true);
        try {
            const response = await adminAPI.listBookings(filter || null);
            setBookings(response.data);
        } catch (err) {
            console.error('Failed to fetch bookings:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (bookingId) => {
        try {
            await adminAPI.approveBooking(bookingId);
            await fetchBookings();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to approve booking');
        }
    };

    const handleReject = async (bookingId) => {
        if (!confirm('Are you sure you want to reject this booking?')) return;
        try {
            await adminAPI.rejectBooking(bookingId);
            await fetchBookings();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to reject booking');
        }
    };

    const handleStartRide = async (bookingId) => {
        try {
            await adminAPI.startRide(bookingId);
            await fetchBookings();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to start ride');
        }
    };

    const handleCompleteRide = async (rideId) => {
        try {
            await adminAPI.completeRide(rideId);
            await fetchBookings();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to complete ride');
        }
    };

    const handleRateRide = async (rideId) => {
        try {
            await adminAPI.rateRide(rideId, rating);
            setRatingModal(null);
            setRating({ driving_rating: 5, damage_flag: false, rash_flag: false, notes: '' });
            await fetchBookings();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to rate ride');
        }
    };

    const filterOptions = [
        { value: 'pending', label: 'Pending' },
        { value: 'confirmed', label: 'Confirmed' },
        { value: 'completed', label: 'Completed' },
        { value: '', label: 'All' },
    ];

    if (loading) return <LoadingSpinner text="Loading bookings..." />;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">Booking Management</h1>
                    <p className="text-gray-400 mt-1">Approve, track, and rate bookings</p>
                </div>

                <div className="flex gap-2">
                    {filterOptions.map(opt => (
                        <button
                            key={opt.value}
                            onClick={() => setFilter(opt.value)}
                            className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${filter === opt.value
                                    ? 'bg-primary-500 text-white'
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                                }`}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Rating Modal */}
            {ratingModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                    <div className="glass-card w-full max-w-md">
                        <h2 className="text-xl font-bold text-white mb-6">Rate This Ride</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-2">Driving Rating (1-5)</label>
                                <div className="flex gap-2">
                                    {[1, 2, 3, 4, 5].map(num => (
                                        <button
                                            key={num}
                                            onClick={() => setRating({ ...rating, driving_rating: num })}
                                            className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${rating.driving_rating >= num
                                                    ? 'bg-yellow-500 text-white'
                                                    : 'bg-white/10 text-gray-400'
                                                }`}
                                        >
                                            <Star className="w-5 h-5" />
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={rating.damage_flag}
                                        onChange={(e) => setRating({ ...rating, damage_flag: e.target.checked })}
                                        className="w-5 h-5 rounded bg-white/10 border-white/20"
                                    />
                                    <span className="text-gray-300">Damage Reported</span>
                                </label>

                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={rating.rash_flag}
                                        onChange={(e) => setRating({ ...rating, rash_flag: e.target.checked })}
                                        className="w-5 h-5 rounded bg-white/10 border-white/20"
                                    />
                                    <span className="text-gray-300">Rash Driving</span>
                                </label>
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-2">Notes (Optional)</label>
                                <textarea
                                    value={rating.notes}
                                    onChange={(e) => setRating({ ...rating, notes: e.target.value })}
                                    className="input-field"
                                    rows="3"
                                />
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    onClick={() => handleRateRide(ratingModal)}
                                    className="btn-primary text-white"
                                >
                                    Submit Rating
                                </button>
                                <button onClick={() => setRatingModal(null)} className="btn-ghost text-white">
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Bookings List */}
            {bookings.length === 0 ? (
                <div className="glass-card text-center py-12">
                    <Calendar className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">No bookings found</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {bookings.map((booking) => (
                        <div key={booking.id} className="glass-card">
                            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                                {/* Booking Info */}
                                <div className="flex items-center gap-4">
                                    <div className="w-16 h-16 rounded-xl overflow-hidden">
                                        <img
                                            src={booking.car?.image_url || 'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=200'}
                                            alt={booking.car?.model}
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-semibold text-white">{booking.car?.model}</h3>
                                        <div className="flex items-center gap-3 mt-1">
                                            <StatusBadge status={booking.status} />
                                            <span className="text-gray-400 text-sm">
                                                {format(new Date(booking.start_time), 'MMM dd')} - {format(new Date(booking.end_time), 'MMM dd')}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* User Info */}
                                <div className="flex items-center gap-4">
                                    <div>
                                        <p className="text-white font-medium">{booking.user?.name}</p>
                                        <div className="flex items-center gap-2">
                                            <TrustBadge score={booking.user?.trust_score} size="sm" />
                                            <span className="text-gray-400 text-sm">
                                                {booking.user?.total_rides || 0} rides
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Price */}
                                <div className="text-right">
                                    <p className="text-xl font-bold text-white flex items-center gap-1 justify-end">
                                        <IndianRupee className="w-5 h-5" />
                                        {parseFloat(booking.offer_price).toLocaleString()}
                                        <span className="text-gray-400 text-sm font-normal">/day</span>
                                    </p>
                                </div>

                                {/* Actions */}
                                <div className="flex gap-2">
                                    {booking.status === 'pending' && (
                                        <>
                                            <button
                                                onClick={() => handleApprove(booking.id)}
                                                className="btn-primary text-white flex items-center gap-2 text-sm py-2"
                                            >
                                                <CheckCircle className="w-4 h-4" />
                                                Approve
                                            </button>
                                            <button
                                                onClick={() => handleReject(booking.id)}
                                                className="btn-ghost text-red-400 flex items-center gap-2 text-sm py-2"
                                            >
                                                <XCircle className="w-4 h-4" />
                                                Reject
                                            </button>
                                        </>
                                    )}

                                    {booking.status === 'confirmed' && !booking.ride && (
                                        <button
                                            onClick={() => handleStartRide(booking.id)}
                                            className="btn-secondary text-white flex items-center gap-2 text-sm py-2"
                                        >
                                            <Play className="w-4 h-4" />
                                            Start Ride
                                        </button>
                                    )}

                                    {booking.ride?.status === 'active' && (
                                        <button
                                            onClick={() => handleCompleteRide(booking.ride.id)}
                                            className="btn-primary text-white flex items-center gap-2 text-sm py-2"
                                        >
                                            <CheckCircle className="w-4 h-4" />
                                            Complete Ride
                                        </button>
                                    )}

                                    {booking.ride?.status === 'completed' && !booking.ride?.rating && (
                                        <button
                                            onClick={() => setRatingModal(booking.ride.id)}
                                            className="btn-secondary text-white flex items-center gap-2 text-sm py-2"
                                        >
                                            <Star className="w-4 h-4" />
                                            Rate Driver
                                        </button>
                                    )}

                                    {booking.ride?.rating && (
                                        <div className="flex items-center gap-2 text-emerald-400">
                                            <CheckCircle className="w-5 h-5" />
                                            <span className="text-sm">Rated {booking.ride.rating.driving_rating}★</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
