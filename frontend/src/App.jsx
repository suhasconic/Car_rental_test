import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';

// Layouts
import Navbar from './components/Navbar';

// Public pages
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Cars from './pages/Cars';
import CarDetails from './pages/CarDetails';

// User pages
import MyBookings from './pages/MyBookings';
import MyAuctions from './pages/MyAuctions';
import Profile from './pages/Profile';

// Admin pages
import AdminDashboard from './pages/admin/Dashboard';
import AdminCars from './pages/admin/Cars';
import AdminBookings from './pages/admin/Bookings';
import AdminAuctions from './pages/admin/Auctions';
import AdminUsers from './pages/admin/Users';

// Protected Route wrapper
const ProtectedRoute = ({ children, adminOnly = false }) => {
    const { user, token } = useAuthStore();

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    if (adminOnly && user?.role !== 'admin') {
        return <Navigate to="/" replace />;
    }

    return children;
};

function App() {
    return (
        <Router>
            <div className="min-h-screen">
                <Navbar />
                <main className="pt-20">
                    <Routes>
                        {/* Public routes */}
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/signup" element={<Signup />} />
                        <Route path="/cars" element={<Cars />} />
                        <Route path="/cars/:id" element={<CarDetails />} />

                        {/* User routes */}
                        <Route path="/my-bookings" element={
                            <ProtectedRoute><MyBookings /></ProtectedRoute>
                        } />
                        <Route path="/my-auctions" element={
                            <ProtectedRoute><MyAuctions /></ProtectedRoute>
                        } />
                        <Route path="/profile" element={
                            <ProtectedRoute><Profile /></ProtectedRoute>
                        } />

                        {/* Admin routes */}
                        <Route path="/admin" element={
                            <ProtectedRoute adminOnly><AdminDashboard /></ProtectedRoute>
                        } />
                        <Route path="/admin/cars" element={
                            <ProtectedRoute adminOnly><AdminCars /></ProtectedRoute>
                        } />
                        <Route path="/admin/bookings" element={
                            <ProtectedRoute adminOnly><AdminBookings /></ProtectedRoute>
                        } />
                        <Route path="/admin/auctions" element={
                            <ProtectedRoute adminOnly><AdminAuctions /></ProtectedRoute>
                        } />
                        <Route path="/admin/users" element={
                            <ProtectedRoute adminOnly><AdminUsers /></ProtectedRoute>
                        } />

                        {/* Catch all */}
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
