import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  Calendar,
  MapPin,
  TrendingUp,
  Eye,
  Edit,
  Trash2,
  Download,
  RefreshCw
} from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { Avance } from '../../types';
import { useAvancesStore } from '../../store/avances.store';
import { useSyncStore } from '../../store/sync.store';
import AvanceForm from './AvanceForm';

const AvanceList: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTorre, setSelectedTorre] = useState('');
  const [selectedPiso, setSelectedPiso] = useState('');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  
  const { 
    avances, 
    isLoading, 
    loadAvances, 
    deleteAvance,
    exportToExcel 
  } = useAvancesStore();
  
  const { isOnline, isSyncing } = useSyncStore();

  useEffect(() => {
    loadAvances();
  }, [loadAvances]);

  const filteredAvances = avances.filter(avance => {
    const matchesSearch = !searchTerm || 
      avance.ubicacion.toLowerCase().includes(searchTerm.toLowerCase()) ||
      avance.categoria.toLowerCase().includes(searchTerm.toLowerCase()) ||
      avance.observaciones?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesTorre = !selectedTorre || avance.torre === selectedTorre;
    const matchesPiso = !selectedPiso || avance.piso?.toString() === selectedPiso;
    
    const matchesDateRange = (!dateRange.start || avance.fecha >= new Date(dateRange.start)) &&
                            (!dateRange.end || avance.fecha <= new Date(dateRange.end));
    
    return matchesSearch && matchesTorre && matchesPiso && matchesDateRange;
  });

  const handleDelete = async (id: string) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este avance?')) {
      await deleteAvance(id);
    }
  };

  const handleExport = async () => {
    try {
      await exportToExcel(filteredAvances);
    } catch (error) {
      console.error('Error exportando:', error);
    }
  };

  const getSyncStatusColor = (status: string) => {
    switch (status) {
      case 'synced': return 'text-success-600 bg-success-100';
      case 'syncing': return 'text-warning-600 bg-warning-100';
      case 'local': return 'text-gray-600 bg-gray-100';
      case 'conflict': return 'text-error-600 bg-error-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSyncStatusText = (status: string) => {
    switch (status) {
      case 'synced': return 'Sincronizado';
      case 'syncing': return 'Sincronizando';
      case 'local': return 'Local';
      case 'conflict': return 'Conflicto';
      default: return 'Desconocido';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Avances</h1>
          <p className="text-gray-600">
            Gestión de avances de obra - {filteredAvances.length} registros
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={handleExport}
            className="btn-secondary"
            disabled={filteredAvances.length === 0}
          >
            <Download className="h-4 w-4 mr-2" />
            Exportar Excel
          </button>
          
          <button
            onClick={() => setShowForm(true)}
            className="btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nuevo Avance
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <label className="form-label">Buscar</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Ubicación, categoría, observaciones..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input pl-10"
              />
            </div>
          </div>

          {/* Torre */}
          <div>
            <label className="form-label">Torre</label>
            <select
              value={selectedTorre}
              onChange={(e) => setSelectedTorre(e.target.value)}
              className="form-input"
            >
              <option value="">Todas</option>
              {Array.from(new Set(avances.map(a => a.torre))).sort().map(torre => (
                <option key={torre} value={torre}>Torre {torre}</option>
              ))}
            </select>
          </div>

          {/* Piso */}
          <div>
            <label className="form-label">Piso</label>
            <select
              value={selectedPiso}
              onChange={(e) => setSelectedPiso(e.target.value)}
              className="form-input"
            >
              <option value="">Todos</option>
              <option value="1">Piso 1</option>
              <option value="3">Piso 3</option>
            </select>
          </div>

          {/* Date Range */}
          <div>
            <label className="form-label">Fecha Desde</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              className="form-input"
            />
          </div>
        </div>

        {/* Clear Filters */}
        {(searchTerm || selectedTorre || selectedPiso || dateRange.start) && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedTorre('');
                setSelectedPiso('');
                setDateRange({ start: '', end: '' });
              }}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Limpiar filtros
            </button>
          </div>
        )}
      </div>

      {/* Sync Status */}
      {!isOnline && (
        <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <RefreshCw className="h-5 w-5 text-warning-600" />
            <div>
              <h3 className="text-sm font-medium text-warning-800">
                Modo Offline
              </h3>
              <p className="text-sm text-warning-700">
                Los cambios se sincronizarán automáticamente cuando se restablezca la conexión.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin h-8 w-8 border border-primary-500 border-t-transparent rounded-full" />
          </div>
        ) : filteredAvances.length === 0 ? (
          <div className="text-center py-12">
            <TrendingUp className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No hay avances registrados
            </h3>
            <p className="text-gray-600 mb-4">
              Comienza registrando el primer avance de la obra.
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Registrar Avance
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ubicación
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Categoría
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progreso
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAvances.map((avance) => (
                  <tr key={avance.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span>
                          {format(avance.fecha, 'dd/MM/yyyy', { locale: es })}
                        </span>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <MapPin className="h-4 w-4 text-gray-400" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {avance.ubicacion}
                          </div>
                          <div className="text-sm text-gray-500">
                            Torre {avance.torre} - Piso {avance.piso}
                            {avance.sector && ` - ${avance.sector}`}
                          </div>
                        </div>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{avance.categoria}</div>
                      <div className="text-sm text-gray-500 capitalize">{avance.tipoEspacio}</div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-3">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${avance.porcentaje}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-900">
                          {avance.porcentaje}%
                        </span>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSyncStatusColor(avance.syncStatus)}`}>
                        {getSyncStatusText(avance.syncStatus)}
                      </span>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          className="text-primary-600 hover:text-primary-700 p-1"
                          title="Ver detalles"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          className="text-gray-600 hover:text-gray-700 p-1"
                          title="Editar"
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(avance.id)}
                          className="text-error-600 hover:text-error-700 p-1"
                          title="Eliminar"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Form Modal */}
      {showForm && (
        <AvanceForm
          onClose={() => setShowForm(false)}
          onSuccess={() => loadAvances()}
        />
      )}
    </div>
  );
};

export default AvanceList;