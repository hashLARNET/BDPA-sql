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
  LogOut,
  RefreshCw
} from 'lucide-react';
import { useAuthStore } from '../store/auth.store';
import { useSyncStore } from '../store/sync.store';
import SyncStatus from './sync/SyncStatus';

const Layout: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { isOnline, isSyncing, queue, processQueue } = useSyncStore();
  const [showSyncStatus, setShowSyncStatus] = useState(false);

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
                <button
                  onClick={() => setShowSyncStatus(true)}
                  className="text-xs bg-warning-100 text-warning-700 px-2 py-1 rounded-full hover:bg-warning-200 transition-colors"
                  title="Ver cola de sincronización"
              
              {/* Quick Sync Button */}
              {isOnline && !isSyncing && queue.length > 0 && (
                <button
                  onClick={processQueue}
                  className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700 transition-colors"
                  title="Sincronizar ahora"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Sincronizar ({queue.length})</span>
                </button>
              )}
                >
                  <span>Sincronizando...</span>
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
      
      {/* Sync Status Modal */}
      {showSyncStatus && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Estado de Sincronización</h2>
              <button
                onClick={() => setShowSyncStatus(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>
            <div className="p-6">
              <SyncStatus />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Layout;