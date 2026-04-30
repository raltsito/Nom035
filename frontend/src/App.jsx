import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import MainLayout from './components/layout/MainLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Empresas from './pages/Empresas';
import Trabajadores from './pages/Trabajadores';
import Cuestionarios from './pages/Cuestionarios';
import Responder from './pages/Responder';
import Resultados from './pages/Resultados';
import Comite from './pages/Comite';
import Calculadora from './pages/Calculadora';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="nom-loading-screen" />;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="nom-loading-screen" />;
  if (user) return <Navigate to="/dashboard" replace />;
  return children;
}

function SuperAdminRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="nom-loading-screen" />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.rol !== 'super_admin') return <Navigate to="/dashboard" replace />;
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/responder/:token" element={<Responder />} />
      <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard"    element={<Dashboard />} />
        <Route path="empresas"     element={<SuperAdminRoute><Empresas /></SuperAdminRoute>} />
        <Route path="comite"        element={<Comite />} />
        <Route path="trabajadores" element={<Trabajadores />} />
        <Route path="cuestionarios" element={<Cuestionarios />} />
        <Route path="resultados"    element={<Resultados />} />
        <Route path="calculadora"   element={<Calculadora />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
