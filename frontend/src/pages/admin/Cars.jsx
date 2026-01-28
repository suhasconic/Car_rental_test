import { useState, useEffect } from 'react';
import {
    Car, Plus, Edit, Trash2, X, Check,
    IndianRupee, Users, Fuel, Cog
} from 'lucide-react';
import { carsAPI, adminAPI } from '../../services/api';
import LoadingSpinner from '../../components/LoadingSpinner';

export default function AdminCars() {
    const [cars, setCars] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingCar, setEditingCar] = useState(null);
    const [saving, setSaving] = useState(false);
    const [formData, setFormData] = useState({
        model: '',
        number_plate: '',
        daily_price: '',
        deposit: '',
        seats: 5,
        transmission: 'automatic',
        fuel_type: 'petrol',
        image_url: '',
        description: '',
    });

    useEffect(() => {
        fetchCars();
    }, []);

    const fetchCars = async () => {
        setLoading(true);
        try {
            const response = await carsAPI.list();
            setCars(response.data);
        } catch (err) {
            console.error('Failed to fetch cars:', err);
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setFormData({
            model: '',
            number_plate: '',
            daily_price: '',
            deposit: '',
            seats: 5,
            transmission: 'automatic',
            fuel_type: 'petrol',
            image_url: '',
            description: '',
        });
        setEditingCar(null);
        setShowForm(false);
    };

    const handleEdit = (car) => {
        setFormData({
            model: car.model,
            number_plate: car.number_plate,
            daily_price: car.daily_price,
            deposit: car.deposit,
            seats: car.seats,
            transmission: car.transmission,
            fuel_type: car.fuel_type,
            image_url: car.image_url || '',
            description: car.description || '',
        });
        setEditingCar(car);
        setShowForm(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);

        try {
            const data = {
                ...formData,
                daily_price: parseFloat(formData.daily_price),
                deposit: parseFloat(formData.deposit),
                seats: parseInt(formData.seats),
            };

            if (editingCar) {
                await adminAPI.updateCar(editingCar.id, data);
            } else {
                await adminAPI.addCar(data);
            }

            await fetchCars();
            resetForm();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to save car');
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (carId) => {
        if (!confirm('Are you sure you want to delete this car?')) return;

        try {
            await adminAPI.deleteCar(carId);
            await fetchCars();
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to delete car');
        }
    };

    const handleToggleActive = async (car) => {
        try {
            await adminAPI.updateCar(car.id, { is_active: !car.is_active });
            await fetchCars();
        } catch (err) {
            alert('Failed to update car status');
        }
    };

    if (loading) return <LoadingSpinner text="Loading cars..." />;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">Fleet Management</h1>
                    <p className="text-gray-400 mt-1">Manage your car inventory</p>
                </div>
                <button
                    onClick={() => setShowForm(true)}
                    className="btn-primary text-white flex items-center gap-2"
                >
                    <Plus className="w-5 h-5" />
                    Add Car
                </button>
            </div>

            {/* Car Form Modal */}
            {showForm && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                    <div className="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-white">
                                {editingCar ? 'Edit Car' : 'Add New Car'}
                            </h2>
                            <button onClick={resetForm} className="p-2 hover:bg-white/10 rounded-lg">
                                <X className="w-5 h-5 text-gray-400" />
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Model Name</label>
                                    <input
                                        type="text"
                                        value={formData.model}
                                        onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                                        className="input-field"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Number Plate</label>
                                    <input
                                        type="text"
                                        value={formData.number_plate}
                                        onChange={(e) => setFormData({ ...formData, number_plate: e.target.value })}
                                        className="input-field"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="grid sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Daily Price (₹)</label>
                                    <input
                                        type="number"
                                        value={formData.daily_price}
                                        onChange={(e) => setFormData({ ...formData, daily_price: e.target.value })}
                                        className="input-field"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Deposit (₹)</label>
                                    <input
                                        type="number"
                                        value={formData.deposit}
                                        onChange={(e) => setFormData({ ...formData, deposit: e.target.value })}
                                        className="input-field"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="grid sm:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Seats</label>
                                    <input
                                        type="number"
                                        value={formData.seats}
                                        onChange={(e) => setFormData({ ...formData, seats: e.target.value })}
                                        className="input-field"
                                        min="2"
                                        max="12"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Transmission</label>
                                    <select
                                        value={formData.transmission}
                                        onChange={(e) => setFormData({ ...formData, transmission: e.target.value })}
                                        className="input-field"
                                    >
                                        <option value="automatic">Automatic</option>
                                        <option value="manual">Manual</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-400 mb-2">Fuel Type</label>
                                    <select
                                        value={formData.fuel_type}
                                        onChange={(e) => setFormData({ ...formData, fuel_type: e.target.value })}
                                        className="input-field"
                                    >
                                        <option value="petrol">Petrol</option>
                                        <option value="diesel">Diesel</option>
                                        <option value="electric">Electric</option>
                                        <option value="hybrid">Hybrid</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-2">Image URL</label>
                                <input
                                    type="url"
                                    value={formData.image_url}
                                    onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                                    className="input-field"
                                    placeholder="https://..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-2">Description</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="input-field"
                                    rows="3"
                                />
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    type="submit"
                                    disabled={saving}
                                    className="btn-primary text-white flex items-center gap-2"
                                >
                                    {saving ? 'Saving...' : editingCar ? 'Update Car' : 'Add Car'}
                                </button>
                                <button type="button" onClick={resetForm} className="btn-ghost text-white">
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Cars Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cars.map((car) => (
                    <div key={car.id} className={`glass-card ${!car.is_active ? 'opacity-60' : ''}`}>
                        <div className="relative h-40 -mx-6 -mt-6 mb-4 overflow-hidden">
                            <img
                                src={car.image_url || 'https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=800'}
                                alt={car.model}
                                className="w-full h-full object-cover"
                            />
                            {!car.is_active && (
                                <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                                    <span className="text-white font-semibold">Inactive</span>
                                </div>
                            )}
                        </div>

                        <h3 className="text-lg font-semibold text-white mb-1">{car.model}</h3>
                        <p className="text-gray-400 text-sm mb-4">{car.number_plate}</p>

                        <div className="flex flex-wrap gap-3 mb-4 text-sm">
                            <span className="flex items-center gap-1 text-gray-400">
                                <IndianRupee className="w-4 h-4" />
                                {parseFloat(car.daily_price).toLocaleString()}/day
                            </span>
                            <span className="flex items-center gap-1 text-gray-400">
                                <Users className="w-4 h-4" />
                                {car.seats}
                            </span>
                            <span className="flex items-center gap-1 text-gray-400">
                                <Cog className="w-4 h-4" />
                                {car.transmission}
                            </span>
                        </div>

                        <div className="flex gap-2">
                            <button
                                onClick={() => handleEdit(car)}
                                className="flex-1 btn-ghost text-white flex items-center justify-center gap-2 text-sm py-2"
                            >
                                <Edit className="w-4 h-4" />
                                Edit
                            </button>
                            <button
                                onClick={() => handleToggleActive(car)}
                                className={`flex-1 btn-ghost flex items-center justify-center gap-2 text-sm py-2 ${car.is_active ? 'text-amber-400' : 'text-emerald-400'}`}
                            >
                                {car.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                            <button
                                onClick={() => handleDelete(car.id)}
                                className="p-2 hover:bg-red-500/20 rounded-lg text-red-400"
                            >
                                <Trash2 className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
