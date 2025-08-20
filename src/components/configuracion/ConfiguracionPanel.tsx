import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Save, 
  RefreshCw, 
  Database, 
  Wifi, 
  Bell,
  Shield,
  Download,
  Upload,
  Trash2,
  AlertTriangle
} from 'lucide-react';
import { useAuthStore } from '../../store/auth.store';
import { useSyncStore } from '../../store/sync.store';

interface ConfiguracionApp {
  syncInterval: number;
  autoSync: boolean;
  compressionLevel: number;
  maxRetries: number;
  notificaciones: boolean;
  backupAutomatico: boolean;
  intervalBackup: number;
}

const ConfiguracionPanel: React.FC = () => {
  const { user } = useAuthStore();
  const { isOnline, lastSync, queue, processQueue } = useSyncStore();
  
  const [config, setConfig] = useState<ConfiguracionApp>({
    syncInterval: 30000,
    autoSync: true,
    compressionLevel: 80,
    maxRetries: 3,
    notificaciones: true,
    backupAutomatico: true,
    intervalBackup: 24
  });

  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    // Cargar configuración guardada
    const savedConfig = localStorage.getItem('bdpa-config');
    if (savedConfig) {
      setConfig(JSON.parse(savedConfig));
    }
  }, []);

  const saveConfig = async () => {
    setIsLoading(true);
    try {
      localStorage.setItem('bdpa-config', JSON.stringify(config));
      // TODO: Sincronizar con Supabase si está online
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulación
    } catch (error) {
      console.error('Error guardando configuración:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resetConfig = () => {
    setConfig({
      syncInterval: 30000,
      autoSync: true,
      compressionLevel: 80,
      maxRetries: 3,
      notificaciones: true,
      backupAutomatico: true,
      intervalBackup: 24
    });
  };

  const exportBackup = async () => {
    try {
      // TODO: Implementar exportación completa de datos
      const backup = {
        timestamp: new Date().toISOString(),
        config,
        user: user?.username,
        version: '1.0.0'
      };
      
      const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bdpa_backup_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exportando backup:', error);
    }
  };

  const clearLocalData = async () => {
    if (window.confirm('¿Estás seguro de que deseas limpiar todos los datos locales? Esta acción no se puede deshacer.')) {
      try {
        localStorage.clear();
        // TODO: Limpiar base de datos SQLite
        window.location.reload();
      } catch (error) {
        console.error('Error limpiando datos:', error);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
          <p className="text-gray-600">Ajustes de la aplicación y sincronización</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => processQueue()}
            disabled={!isOnline || queue.length === 0}
            className="btn-secondary"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Sincronizar Ahora
          </button>
          
          <button
            onClick={saveConfig}
            disabled={isLoading}
            className="btn-primary"
          >
            <Save className="h-4 w-4 mr-2" />
            Guardar Cambios
          </button>
        </div>
      </div>

      {/* Estado del Sistema */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Database className="h-5 w-5 mr-2" />
          Estado del Sistema
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-success-500' : 'bg-error-500'}`} />
            <div>
              <p className="text-sm font-medium text-gray-900">Conexión</p>
              <p className="text-sm text-gray-600">{isOnline ? 'En línea' : 'Sin conexión'}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <RefreshCw className="h-5 w-5 text-primary-500" />
            <div>
              <p className="text-sm font-medium text-gray-900">Última Sincronización</p>
              <p className="text-sm text-gray-600">
                {lastSync ? lastSync.toLocaleString('es-CL') : 'Nunca'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 rounded-full bg-warning-500" />
            <div>
              <p className="text-sm font-medium text-gray-900">Cola de Sincronización</p>
              <p className="text-sm text-gray-600">{queue.length} elementos pendientes</p>
            </div>
          </div>
        </div>
      </div>

      {/* Configuración de Sincronización */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Wifi className="h-5 w-5 mr-2" />
          Sincronización
        </h3>
        
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">Sincronización Automática</label>
              <p className="text-sm text-gray-600">Sincronizar datos automáticamente cuando hay conexión</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.autoSync}
                onChange={(e) => setConfig(prev => ({ ...prev, autoSync: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div>
            <label className="form-label">Intervalo de Sincronización (segundos)</label>
            <select
              value={config.syncInterval}
              onChange={(e) => setConfig(prev => ({ ...prev, syncInterval: parseInt(e.target.value) }))}
              className="form-input"
            >
              <option value={15000}>15 segundos</option>
              <option value={30000}>30 segundos</option>
              <option value={60000}>1 minuto</option>
              <option value={300000}>5 minutos</option>
              <option value={600000}>10 minutos</option>
            </select>
          </div>

          <div>
            <label className="form-label">Máximo de Reintentos</label>
            <input
              type="number"
              min="1"
              max="10"
              value={config.maxRetries}
              onChange={(e) => setConfig(prev => ({ ...prev, maxRetries: parseInt(e.target.value) }))}
              className="form-input"
            />
          </div>
        </div>
      </div>

      {/* Configuración de Notificaciones */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Bell className="h-5 w-5 mr-2" />
          Notificaciones
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">Notificaciones del Sistema</label>
              <p className="text-sm text-gray-600">Recibir notificaciones sobre sincronización y errores</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.notificaciones}
                onChange={(e) => setConfig(prev => ({ ...prev, notificaciones: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Configuración de Backup */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Shield className="h-5 w-5 mr-2" />
          Backup y Seguridad
        </h3>
        
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-900">Backup Automático</label>
              <p className="text-sm text-gray-600">Crear backups automáticos de los datos</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.backupAutomatico}
                onChange={(e) => setConfig(prev => ({ ...prev, backupAutomatico: e.target.checked }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div>
            <label className="form-label">Intervalo de Backup (horas)</label>
            <select
              value={config.intervalBackup}
              onChange={(e) => setConfig(prev => ({ ...prev, intervalBackup: parseInt(e.target.value) }))}
              className="form-input"
              disabled={!config.backupAutomatico}
            >
              <option value={6}>6 horas</option>
              <option value={12}>12 horas</option>
              <option value={24}>24 horas</option>
              <option value={168}>1 semana</option>
            </select>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={exportBackup}
              className="btn-secondary flex-1"
            >
              <Download className="h-4 w-4 mr-2" />
              Exportar Backup
            </button>
            
            <button className="btn-secondary flex-1">
              <Upload className="h-4 w-4 mr-2" />
              Importar Backup
            </button>
          </div>
        </div>
      </div>

      {/* Configuración Avanzada */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Configuración Avanzada
          </h3>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            {showAdvanced ? 'Ocultar' : 'Mostrar'}
          </button>
        </div>
        
        {showAdvanced && (
          <div className="space-y-6">
            <div>
              <label className="form-label">Nivel de Compresión de Imágenes (%)</label>
              <input
                type="range"
                min="10"
                max="100"
                value={config.compressionLevel}
                onChange={(e) => setConfig(prev => ({ ...prev, compressionLevel: parseInt(e.target.value) }))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-sm text-gray-600 mt-1">
                <span>Máxima compresión</span>
                <span>{config.compressionLevel}%</span>
                <span>Sin compresión</span>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6">
              <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
                <AlertTriangle className="h-4 w-4 mr-2 text-warning-500" />
                Zona de Peligro
              </h4>
              
              <div className="space-y-4">
                <button
                  onClick={resetConfig}
                  className="btn-secondary w-full"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Restaurar Configuración por Defecto
                </button>
                
                <button
                  onClick={clearLocalData}
                  className="btn-error w-full"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Limpiar Todos los Datos Locales
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Información del Usuario */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Información del Usuario</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="form-label">Nombre de Usuario</label>
            <input
              type="text"
              value={user?.username || ''}
              disabled
              className="form-input bg-gray-50"
            />
          </div>
          
          <div>
            <label className="form-label">Nombre Completo</label>
            <input
              type="text"
              value={user?.nombre || ''}
              disabled
              className="form-input bg-gray-50"
            />
          </div>
          
          <div>
            <label className="form-label">Rol</label>
            <input
              type="text"
              value={user?.rol || ''}
              disabled
              className="form-input bg-gray-50"
            />
          </div>
          
          <div>
            <label className="form-label">Último Acceso</label>
            <input
              type="text"
              value={user?.ultimoAcceso?.toLocaleString('es-CL') || 'N/A'}
              disabled
              className="form-input bg-gray-50"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfiguracionPanel;