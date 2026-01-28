import { Link } from 'react-router-dom';
import { Users, Fuel, Cog, IndianRupee } from 'lucide-react';

export default function CarCard({ car }) {
    return (
        <Link to={`/cars/${car.id}`} className="block group">
            <div className="glass-card overflow-hidden hover:scale-[1.02] transition-transform duration-300">
                {/* Car Image */}
                <div className="relative h-48 -mx-6 -mt-6 mb-4 overflow-hidden">
                    <img
                        src={car.image_url || 'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800'}
                        alt={car.model}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-dark-900/80 to-transparent" />

                    {/* Price badge */}
                    <div className="absolute bottom-4 right-4 glass px-4 py-2 rounded-xl">
                        <div className="flex items-center gap-1 text-white font-bold">
                            <IndianRupee className="w-4 h-4" />
                            <span>{parseFloat(car.daily_price).toLocaleString()}</span>
                            <span className="text-gray-400 font-normal text-sm">/day</span>
                        </div>
                    </div>
                </div>

                {/* Car Info */}
                <div>
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-primary-400 transition-colors">
                        {car.model}
                    </h3>

                    <p className="text-gray-400 text-sm mb-4">{car.number_plate}</p>

                    {/* Features */}
                    <div className="flex flex-wrap gap-3">
                        <div className="flex items-center gap-1.5 text-gray-400 text-sm">
                            <Users className="w-4 h-4" />
                            <span>{car.seats} Seats</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-gray-400 text-sm">
                            <Cog className="w-4 h-4" />
                            <span className="capitalize">{car.transmission}</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-gray-400 text-sm">
                            <Fuel className="w-4 h-4" />
                            <span className="capitalize">{car.fuel_type}</span>
                        </div>
                    </div>

                    {/* Deposit info */}
                    <div className="mt-4 pt-4 border-t border-white/10">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Security Deposit</span>
                            <span className="text-white font-semibold flex items-center gap-1">
                                <IndianRupee className="w-3 h-3" />
                                {parseFloat(car.deposit).toLocaleString()}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    );
}
