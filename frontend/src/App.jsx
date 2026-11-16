import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './routes/PrivateRoute';
import Login from './pages/Login';
import Home from './pages/Home';
import EventDetails from './pages/EventDetails';
import AdminEventsPage from './pages/AdminEventsPage';
import EventCreatePage from './pages/EventCreatePage';
import EventEditPage from './pages/EventEditPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/eventos/:id" element={<EventDetails />} />
          <Route path="/admin" element={<PrivateRoute><AdminEventsPage /></PrivateRoute>} />
          <Route path="/admin/events" element={<PrivateRoute><AdminEventsPage /></PrivateRoute>} />
          <Route path="/admin/events/new" element={<PrivateRoute><EventCreatePage /></PrivateRoute>} />
          <Route path="/admin/events/:id/edit" element={<PrivateRoute><EventEditPage /></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}