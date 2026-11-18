import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './routes/PrivateRoute';
import AdminLayout from './components/AdminLayout';
import Login from './pages/Login';
import Home from './pages/Home';
import EventDetails from './pages/EventDetails';
import AdminEventsPage from './pages/AdminEventsPage';
import EventCreatePage from './pages/EventCreatePage';
import EventEditPage from './pages/EventEditPage';
import ExtractionStatusPage from './pages/ExtractionStatusPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/eventos/:id" element={<EventDetails />} />
          <Route path="/admin" element={<PrivateRoute><AdminLayout /></PrivateRoute>}>
            <Route index element={<Navigate to="events" replace />} />
            <Route path="events" element={<AdminEventsPage />} />
            <Route path="events/new" element={<EventCreatePage />} />
            <Route path="events/:id/edit" element={<EventEditPage />} />
            <Route path="extraction" element={<ExtractionStatusPage />} />
            <Route path="*" element={<Navigate to="/admin/events" replace />} />
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}