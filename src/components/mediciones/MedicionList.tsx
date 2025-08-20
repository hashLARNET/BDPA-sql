import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  Calendar,
  Activity,
  AlertTriangle,
  CheckCircle,
  Download,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { Medicion } from '../../types';
import { useMedicionesStore } from '../../store/mediciones.store';
import { useSyncStore } from '../../store/sync.store';
import MedicionForm from './MedicionForm';

const MedicionList: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTorre, setSelectedTorre] = useState('');
  const [selectedTipo, setSelectedTipo] = useState('');
  const [selectedEstado, setSelectedEstado] = useState('');
  
  const { 
    mediciones, 
    isLoading, 
    loadMediciones, 
    deleteMedicion,
    exportToExcel 
  } = useMedicionesStore();
  
  const { isOnline } = useSyncStore();

  useEffect(() => {
    loadMediciones();
  }, [loadMediciones]);

  const filteredMediciones = mediciones.filter(medicion => {
    const matchesSearch = !searchTerm || 
      medicion.identificador.toLowerCase().includes(searchTerm.toLowerCase()) ||
      medicion.observaciones?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesTorre = !selectedTorre || medicion.torre === selectedTorre;
    const matchesTipo = !selectedTipo || medicion.tipoMedicion === selectedTipo;
    const matchesEstado = !selectedEstado || medicion.estado === selectedEstado;
    
    return matchesSearch && matchesTorre && matchesTipo && matchesEstado;
  });

  const handleDelete = async (id: string) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar esta medición?')) {
      await deleteMedicion(id);
    }
  };

  const handleExport = async () => {
    try {
      await exportToExcel(filteredMediciones);
    } catch (error) {
      console.error('Error exportando:', error);
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'OK': return 'text-success-700 bg-success-100';
      case 'ADVERTENCIA': return 'text-warning-700 bg-warning-100';
      case 'FALLA': return 'text-error-700 bg-error-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case 'OK': return <CheckCircle className="h-4 w-4" />;
      case 'ADVERTENCIA': return <AlertTriangle className="h-4 w-4" />;
      case 'FALLA': return <AlertTriangle className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const formatValores = (medicion: Medicion) => {
    const { valores, tipoMedicion } = medicion;
    
    switch (tipoMedicion) {
      case 'alambrico-t1':
        return valores.alambricoT1 ? `${valores.alambricoT1} dBμV` : '-';
      case 'alambrico-t2':
        return valores.alambricoT2 ? `${valores.alambricoT2} dBμV` : '-';
      case 'coaxial':
        return valores.coaxial ? `${valores.coaxial} dBμV` : '-';
      case 'fibra':
        return `TX: ${valores.potenciaTx || '-'} dBm, RX: ${valores.potenciaRx || '-'} dBm`;
      case 'wifi':
        return valores.wifi ? `${valores.wifi} dBm` : '-';
      case 'certificacion':
        return valores.certificacion || '-';
      default:
        return '-';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mediciones</h1>
          <p className="text-gray-600">
            Gestión de mediciones técnicas - {filteredMediciones.length} registros
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={handleExport}
            className="btn-secondary"
            disabled={filteredMediciones.length === 0}
          >
            <Download className="h-4 w-4 mr-2" />
            Exportar Excel
          </button>
          
          <button
            onClick={() => setShowForm(true)}
            className="btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nueva Medición
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
                placeholder="Unidad, observaciones..."
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
              {Array.from(new Set(mediciones.map(m => m.torre))).sort().map(torre => (
                <option key={torre} value={torre}>Torre {torre}</option>
              ))}
            </select>
          </div>

          {/* Tipo */}
          <div>
            <label className="form-label">Tipo</label>
            <select
              value={selectedTipo}
              onChange={(e) => setSelectedTipo(e.target.value)}
              className="form-input"
            >
              <option value="">Todos</option>
              <option value="alambrico-t1">Alámbrico T1</option>
              <option value="alambrico-t2">Alámbrico T2</option>
              <option value="coaxial">Coaxial</option>
              <option value="fibra">Fibra Óptica</option>
              <option value="wifi">WiFi</option>
              <option value="certificacion">Certificación</option>
            </select>
          </div>

          {/* Estado */}
          <div>
            <label className="form-label">Estado</label>
            <select
              value={selectedEstado}
              onChange={(e) => setSelectedEstado(e.target.value)}
              className="form-input"
            >
              <option value="">Todos</option>
              <option value="OK">OK</option>
              <option value="ADVERTENCIA">Advertencia</option>
              <option value="FALLA">Falla</option>
            </select>
          </div>
        </div>

        {/* Clear Filters */}
        {(searchTerm || selectedTorre || selectedTipo || selectedEstado) && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedTorre('');
                setSelectedTipo('');
                setSelectedEstado('');
              }}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Limpiar filtros
            </button>
          </div>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Mediciones</p>
              <p className="text-2xl font-bold text-gray-900">{mediciones.length}</p>
            </div>
            <Activity className="h-8 w-8 text-primary-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Con Fallas</p>
              <p className="text-2xl font-bold text-error-600">
                {mediciones.filter(m => m.estado === 'FALLA').length}
              </p>
            </div>
            <AlertTriangle className="h-8 w-8 text-error-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Aprobadas</p>
              <p className="text-2xl font-bold text-success-600">
                {mediciones.filter(m => m.estado === 'OK').length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-success-500" />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin h-8 w-8 border border-primary-500 border-t-transparent rounded-full" />
          </div>
        ) : filteredMediciones.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No hay mediciones registradas
            </h3>
            <p className="text-gray-600 mb-4">
              Comienza registrando la primera medición.
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Registrar Medición
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
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valores
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
                {filteredMediciones.map((medicion) => (
                  <tr key={medicion.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span>
                          {format(medicion.fecha, 'dd/MM/yyyy', { locale: es })}
                        </span>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {medicion.identificador}
                      </div>
                      <div className="text-sm text-gray-500">
                        Torre {medicion.torre} - Piso {medicion.piso}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 capitalize">
                        {medicion.tipoMedicion.replace('-', ' ')}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatValores(medicion)}
                      </div>
                    </td>
                    
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoColor(medicion.estado)}`}>
                        {getEstadoIcon(medicion.estado)}
                        <span className="ml-1">{medicion.estado}</span>
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
                          onClick={() => handleDelete(medicion.id)}
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
        <MedicionForm
          onClose={() => setShowForm(false)}
          onSuccess={() => loadMediciones()}
        />
      )}
    </div>
  );
};

export default MedicionList;