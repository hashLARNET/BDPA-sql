import React from 'react';
import { 
  RefreshCw, 
  Wifi, 
  WifiOff, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  X
} from 'lucide-react';
import { useSyncStore } from '../../store/sync.store';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const SyncStatus: React.FC = () => {
  const { 
    isOnline, 
    isSyncing, 
    lastSync, 
    queue, 
    errors, 
    processQueue,
    clearErrors,
    removeFromQueue
  } = useSyncStore();

  const pendingItems = queue.filter(item => item.status === 'pending');
  const failedItems = queue.filter(item => item.status === 'failed');
  const processingItems = queue.filter(item => item.status === 'processing');

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4 text-warning-500" />;
      case 'processing': return <RefreshCw className="h-4 w-4 text-primary-500 animate-spin" />;
      case 'completed': return <CheckCircle className="h-4 w-4 text-success-500" />;
      case 'failed': return <AlertTriangle className="h-4 w-4 text-error-500" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-warning-100 text-warning-800';
      case 'processing': return 'bg-primary-100 text-primary-800';
      case 'completed': return 'bg-success-100 text-success-800';
      case 'failed': return 'bg-error-100 text-error-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'avance': return 'Avance';
      case 'medicion': return 'Medición';
      case 'foto': return 'Foto';
      default: return type;
    }
  };

  const getActionLabel = (action: string) => {
    switch (action) {
      case 'create': return 'Crear';
      case 'update': return 'Actualizar';
      case 'delete': return 'Eliminar';
      default: return action;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Estado de Sincronización</h2>
          <p className="text-gray-600">Monitoreo de sincronización y cola de operaciones</p>
        </div>
        
        <div className="flex items-center space-x-3">
          {errors.length > 0 && (
            <button
              onClick={clearErrors}
              className="btn-secondary text-sm"
            >
              Limpiar Errores
            </button>
          )}
          
          <button
            onClick={processQueue}
            disabled={!isOnline || isSyncing || pendingItems.length === 0}
            className="btn-primary"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? 'Sincronizando...' : 'Sincronizar Ahora'}
          </button>
        </div>
      </div>

      {/* Connection Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              {isOnline ? (
                <Wifi className="h-5 w-5 text-success-500" />
              ) : (
                <WifiOff className="h-5 w-5 text-error-500" />
              )}
              <span className="font-medium text-gray-900">
                {isOnline ? 'Conectado' : 'Sin conexión'}
              </span>
            </div>
            
            {lastSync && (
              <div className="text-sm text-gray-600">
                Última sincronización: {format(lastSync, 'dd/MM/yyyy HH:mm:ss', { locale: es })}
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">{pendingItems.length}</div>
              <div className="text-xs text-gray-600">Pendientes</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-semibold text-error-600">{failedItems.length}</div>
              <div className="text-xs text-gray-600">Fallidos</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-semibold text-primary-600">{processingItems.length}</div>
              <div className="text-xs text-gray-600">Procesando</div>
            </div>
          </div>
        </div>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="bg-error-50 border border-error-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-error-800">
              Errores de Sincronización ({errors.length})
            </h3>
            <button
              onClick={clearErrors}
              className="text-error-600 hover:text-error-700"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="space-y-2">
            {errors.slice(0, 5).map((error, index) => (
              <div key={index} className="text-sm text-error-700 bg-error-100 rounded p-2">
                {error}
              </div>
            ))}
            {errors.length > 5 && (
              <div className="text-sm text-error-600">
                ... y {errors.length - 5} errores más
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sync Queue */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Cola de Sincronización ({queue.length})
          </h3>
        </div>
        
        {queue.length === 0 ? (
          <div className="p-6 text-center">
            <CheckCircle className="mx-auto h-12 w-12 text-success-500 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Todo sincronizado
            </h3>
            <p className="text-gray-600">
              No hay elementos pendientes en la cola de sincronización.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {queue.map((item) => (
              <div key={item.id} className="p-6 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(item.status)}
                  
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">
                        {getActionLabel(item.action)} {getTypeLabel(item.type)}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                        {item.status}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-600 mt-1">
                      ID: {item.itemId.substring(0, 8)}...
                      {item.attempts > 0 && (
                        <span className="ml-2">
                          Intentos: {item.attempts}
                        </span>
                      )}
                      {item.lastAttempt && (
                        <span className="ml-2">
                          Último intento: {format(item.lastAttempt, 'HH:mm:ss', { locale: es })}
                        </span>
                      )}
                    </div>
                    
                    {item.error && (
                      <div className="text-sm text-error-600 mt-1 bg-error-50 rounded p-2">
                        {item.error}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {item.status === 'failed' && (
                    <button
                      onClick={() => {
                        // Reintentar item
                        const updatedItem = { ...item, status: 'pending' as const, attempts: 0, error: undefined };
                        // TODO: Actualizar item en store
                      }}
                      className="text-primary-600 hover:text-primary-700 text-sm"
                    >
                      Reintentar
                    </button>
                  )}
                  
                  <button
                    onClick={() => removeFromQueue(item.id)}
                    className="text-error-600 hover:text-error-700 p-1"
                    title="Eliminar de la cola"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Sync Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total en Cola</p>
              <p className="text-2xl font-bold text-gray-900">{queue.length}</p>
            </div>
            <RefreshCw className="h-8 w-8 text-gray-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Elementos Fallidos</p>
              <p className="text-2xl font-bold text-error-600">{failedItems.length}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-error-400" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tasa de Éxito</p>
              <p className="text-2xl font-bold text-success-600">
                {queue.length > 0 
                  ? Math.round(((queue.length - failedItems.length) / queue.length) * 100)
                  : 100
                }%
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-success-400" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SyncStatus;