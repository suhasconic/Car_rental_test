import { useState, useEffect } from 'react';
import { Trophy, Users, IndianRupee, Clock, Gavel } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';
import { adminAPI } from '../../services/api';
import StatusBadge from '../../components/StatusBadge';
import TrustBadge from '../../components/TrustBadge';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function AdminAuctions() {
    const [auctions, setAuctions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('active');
    const [closing, setClosing] = useState(null);

    useEffect(() => {
        fetchAuctions();
    }, [filter]);

    const fetchAuctions = async () => {
        setLoading(true);
        try {
            const response = await adminAPI.listAuctions(filter || null);
            setAuctions(response.data);
        } catch (err) {
            console.error('Failed to fetch auctions:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCloseAuction = async (auctionId) => {
        if (!confirm('Are you sure you want to close this auction? This will determine the winner.')) return;

        setClosing(auctionId);
        try {
            const response = await adminAPI.closeAuction(auctionId);
            alert(response.data.winner_id ? 'Auction closed! Winner selected.' : 'Auction closed with no winner.');
            await fetchAuctions();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to close auction');
        } finally {
            setClosing(null);
        }
    };

    if (loading) return <LoadingSpinner text="Loading auctions..." />;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">Auction Control</h1>
                    <p className="text-gray-400 mt-1">Manage and close auctions</p>
                </div>

                <div className="flex gap-2">
                    {[{ value: 'active', label: 'Active' }, { value: 'closed', label: 'Closed' }, { value: '', label: 'All' }].map(opt => (
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

            {auctions.length === 0 ? (
                <div className="glass-card text-center py-12">
                    <Trophy className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">No auctions found</p>
                </div>
            ) : (
                <div className="space-y-6">
                    {auctions.map((auction) => {
                        const highestBid = auction.bids?.reduce((max, b) =>
                            parseFloat(b.offer_price) > parseFloat(max?.offer_price || 0) ? b : max
                            , null);

                        return (
                            <div key={auction.id} className="glass-card">
                                {/* Header */}
                                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                                    <div className="flex items-center gap-4">
                                        <div className="w-16 h-16 rounded-xl overflow-hidden">
                                            <img
                                                src={auction.car?.image_url || 'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=200'}
                                                alt={auction.car?.model}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-white">{auction.car?.model}</h3>
                                            <div className="flex items-center gap-2 mt-1">
                                                <StatusBadge status={auction.status} />
                                                <span className="text-gray-400 text-sm flex items-center gap-1">
                                                    <Users className="w-4 h-4" />
                                                    {auction.bid_count} bidders
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4">
                                        <div className="text-right">
                                            <p className="text-gray-400 text-sm">Rental Period</p>
                                            <p className="text-white">
                                                {format(new Date(auction.start_time), 'MMM dd')} - {format(new Date(auction.end_time), 'MMM dd')}
                                            </p>
                                        </div>

                                        {auction.auction_end && (
                                            <div className="text-right">
                                                <p className="text-gray-400 text-sm">
                                                    {auction.status === 'active' ? 'Ends' : 'Ended'}
                                                </p>
                                                <p className="text-white flex items-center gap-1">
                                                    <Clock className="w-4 h-4" />
                                                    {auction.status === 'active'
                                                        ? formatDistanceToNow(new Date(auction.auction_end), { addSuffix: true })
                                                        : format(new Date(auction.auction_end), 'MMM dd, HH:mm')
                                                    }
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Winner Display (if closed) */}
                                {auction.status === 'closed' && auction.winner && (
                                    <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
                                        <div className="flex items-center gap-3">
                                            <Trophy className="w-6 h-6 text-emerald-400" />
                                            <div>
                                                <p className="text-emerald-400 font-medium">Winner: {auction.winner.name}</p>
                                                <TrustBadge score={auction.winner.trust_score} size="sm" />
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* All Bids */}
                                <div className="mb-6">
                                    <h4 className="text-sm font-medium text-gray-400 mb-3">All Bids (Ranked)</h4>
                                    {auction.bids?.length > 0 ? (
                                        <div className="space-y-2">
                                            {auction.bids
                                                .sort((a, b) => {
                                                    // Sort by final_score if available, otherwise by offer_price
                                                    if (a.final_score && b.final_score) {
                                                        return parseFloat(b.final_score) - parseFloat(a.final_score);
                                                    }
                                                    return parseFloat(b.offer_price) - parseFloat(a.offer_price);
                                                })
                                                .map((bid, index) => (
                                                    <div
                                                        key={bid.id}
                                                        className={`flex items-center justify-between p-3 rounded-xl ${index === 0 ? 'bg-amber-500/10 border border-amber-500/30' : 'bg-white/5'
                                                            }`}
                                                    >
                                                        <div className="flex items-center gap-3">
                                                            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${index === 0 ? 'bg-amber-500 text-white' : 'bg-white/10 text-gray-400'
                                                                }`}>
                                                                {index + 1}
                                                            </span>
                                                            <span className="text-white">{bid.user?.name || 'User'}</span>
                                                            <TrustBadge score={bid.trust_score_snapshot} size="sm" />
                                                        </div>
                                                        <div className="flex items-center gap-4">
                                                            {bid.final_score && (
                                                                <span className="text-gray-400 text-sm">
                                                                    Score: {parseFloat(bid.final_score).toFixed(3)}
                                                                </span>
                                                            )}
                                                            <span className="text-white font-semibold flex items-center gap-1">
                                                                <IndianRupee className="w-4 h-4" />
                                                                {parseFloat(bid.offer_price).toLocaleString()}
                                                            </span>
                                                        </div>
                                                    </div>
                                                ))
                                            }
                                        </div>
                                    ) : (
                                        <p className="text-gray-400 text-sm">No bids yet</p>
                                    )}
                                </div>

                                {/* Actions */}
                                {auction.status === 'active' && (
                                    <div className="pt-4 border-t border-white/10 flex justify-end">
                                        <button
                                            onClick={() => handleCloseAuction(auction.id)}
                                            disabled={closing === auction.id}
                                            className="btn-secondary text-white flex items-center gap-2"
                                        >
                                            {closing === auction.id ? (
                                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            ) : (
                                                <Gavel className="w-5 h-5" />
                                            )}
                                            Close Auction
                                        </button>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
