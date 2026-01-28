import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Car, IndianRupee, Clock, Trophy, XCircle } from 'lucide-react';
import { format } from 'date-fns';
import { bookingsAPI } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

export default function MyBookings() {
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');
    const [cancelling, setCancelling] = useState(null);

    useEffect(() => {
        fetchBookings();
    }, [filter]);

    const fetchBookings = async () => {
        setLoading(true);
        try {
            const response = await bookingsAPI.getMy(filter || null);
            setBookings(response.data);
        } catch (err) {
            console.error('Failed to fetch bookings:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCancel = async (bookingId) => {
        if (!confirm('Are you sure you want to cancel this booking? Late cancellations may affect your trust score.')) {
            return;
        }

        setCancelling(bookingId);
        try {
            await bookingsAPI.cancel(bookingId);
            fetchBookings();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to cancel booking');
        } finally {
            setCancelling(null);
        }
    };

    const filterOptions = [
        { value: '', label: 'All' },
        { value: 'pending', label: 'Pending' },
        { value: 'competing', label: 'In Auction' },
        { value: 'confirmed', label: 'Confirmed' },
        { value: 'completed', label: 'Completed' },
        { value: 'rejected', label: 'Rejected' },
        { value: 'cancelled', label: 'Cancelled' },
    ];

    return (
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">My Bookings</h1>
                    <p className="text-gray-400 mt-1">Track all your car rental bookings</p>
                </div>

                <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="input-field w-full md:w-48"
                >
                    {filterOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                </select>
            </div>

            {loading ? (
                <LoadingSpinner text="Loading bookings..." />
            ) : bookings.length === 0 ? (
                <div className="glass-card text-center py-12">
                    <Calendar className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No bookings yet</h3>
                    <p className="text-gray-400 mb-6">Start exploring our fleet and make your first booking!</p>
                    <Link to="/cars" className="btn-primary text-white inline-flex items-center gap-2">
                        <Car className="w-5 h-5" />
                        Browse Cars
                    </Link>
                </div>
            ) : (
                <div className="space-y-4">
                    {bookings.map((booking) => (
                        <div key={booking.id} className="glass-card">
                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                {/* Car Info */}
                                <div className="flex items-center gap-4">
                                    <div className="w-20 h-20 rounded-xl overflow-hidden flex-shrink-0">
                                        <img
                                            src={booking.car?.image_url || 'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=200'}
                                            alt={booking.car?.model}
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-semibold text-white">
                                            {booking.car?.model || 'Car'}
                                        </h3>
                                        <p className="text-gray-400 text-sm">{booking.car?.number_plate}</p>
                                        <StatusBadge status={booking.status} />
                                    </div>
                                </div>

                                {/* Dates */}
                                <div className="flex items-center gap-6 text-sm">
                                    <div>
                                        <p className="text-gray-400 mb-1">From</p>
                                        <p className="text-white font-medium flex items-center gap-1">
                                            <Clock className="w-4 h-4 text-primary-400" />
                                            {format(new Date(booking.start_time), 'MMM dd, yyyy')}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-gray-400 mb-1">To</p>
                                        <p className="text-white font-medium flex items-center gap-1">
                                            <Clock className="w-4 h-4 text-primary-400" />
                                            {format(new Date(booking.end_time), 'MMM dd, yyyy')}
                                        </p>
                                    </div>
                                </div>

                                {/* Price */}
                                <div className="text-right">
                                    <p className="text-gray-400 text-sm mb-1">Your Offer</p>
                                    <p className="text-xl font-bold text-white flex items-center justify-end gap-1">
                                        <IndianRupee className="w-5 h-5" />
                                        {parseFloat(booking.offer_price).toLocaleString()}
                                        <span className="text-gray-400 text-sm font-normal">/day</span>
                                    </p>
                                </div>
                            </div>

                            {/* Status specific content */}
                            {booking.status === 'competing' && (
                                <div className="mt-4 p-4 rounded-xl bg-purple-500/10 border border-purple-500/30">
                                    <div className="flex items-center gap-2 text-purple-400 text-sm">
                                        <Trophy className="w-4 h-4" />
                                        <span>This booking is in an active auction. You can update your offer via the Auctions tab.</span>
                                    </div>
                                </div>
                            )}

                            {/* Actions */}
                            {['pending', 'competing', 'confirmed'].includes(booking.status) && (
                                <div className="mt-4 pt-4 border-t border-white/10 flex justify-end">
                                    <button
                                        onClick={() => handleCancel(booking.id)}
                                        disabled={cancelling === booking.id}
                                        className="btn-ghost text-red-400 flex items-center gap-2 text-sm"
                                    >
                                        {cancelling === booking.id ? (
                                            <div className="w-4 h-4 border-2 border-red-400/30 border-t-red-400 rounded-full animate-spin" />
                                        ) : (
                                            <XCircle className="w-4 h-4" />
                                        )}
                                        Cancel Booking
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
