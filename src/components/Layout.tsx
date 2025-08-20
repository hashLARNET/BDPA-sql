import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  TrendingUp, 
  Activity, 
  BarChart3, 
  Settings, 
  Wifi, 
  WifiOff,
  User,
  LogOut
} from 'lucide-react';
import { useAuthStore } from '../store/auth.store';
import { useSyncStore } from '../store/sync.store';

const Layout: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { isOnline, isSyncing, queue } = useSyncStore();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Avances', href: '/avances', icon: TrendingUp },
    { name: 'Mediciones', href: '/mediciones', icon: Activity },
    { name: 'Reportes', href: '/reportes', icon: BarChart3 },
    { name: 'Configuración', href: '/configuracion', icon: Settings },
  ];

  const pendingSync = queue.filter(item => item.status === 'pending').length;

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">BDPA</h1>
          <p className="text-sm text-gray-600">Los Encinos</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                  ${isActive 
                    ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-500' 
                    : 'text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Status Bar */}
        <div className="p-4 border-t border-gray-200 space-y-3">
          {/* Connection Status */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {isOnline ? (
                <Wifi className="h-4 w-4 text-success-500" />
              ) : (
                <WifiOff className="h-4 w-4 text-error-500" />
              )}
              <span className="text-xs text-gray-600">
                {isOnline ? 'En línea' : 'Sin conexión'}
              </span>
            </div>
            
            {/* Sync Status */}
            {(isSyncing || pendingSync > 0) && (
              <div className="flex items-center space-x-1">
                {isSyncing && (
                  <div className="animate-spin h-3 w-3 border border-primary-500 border-t-transparent rounded-full" />
                )}
                {pendingSync > 0 && (
                  <span className="text-xs bg-warning-100 text-warning-700 px-2 py-1 rounded-full">
                    {pendingSync}
                  </span>
                )}
              </div>
            )}
          </div>

          {/* User Info */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <User className="h-4 w-4 text-gray-500" />
              <div className="flex flex-col">
                <span className="text-xs font-medium text-gray-900">
                  {user?.nombre}
                </span>
                <span className="text-xs text-gray-500">
                  {user?.rol}
                </span>
              </div>
            </div>
            
            <button
              onClick={logout}
              className="p-1 text-gray-500 hover:text-error-500 transition-colors"
              title="Cerrar sesión"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-gray-900">
              {navigation.find(item => item.href === location.pathname)?.name || 'BDPA'}
            </h2>
            
            <div className="flex items-center space-x-4">
              {/* Sync Indicator */}
              {isSyncing && (
                <div className="flex items-center space-x-2 text-sm text-primary-600">
                  <div className="animate-spin h-4 w-4 border border-primary-500 border-t-transparent rounded-full" />
                  <span>Sincronizando...</span>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;