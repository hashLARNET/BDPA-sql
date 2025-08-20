import React, { useEffect, useState } from 'react';
import { 
  Building2, 
  TrendingUp, 
  Users, 
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity
} from 'lucide-react';
import { getTotalUnidades, TORRES } from '../../utils/estructura-obra';
import ProgressChart from './ProgressChart';
import TowerProgress from './TowerProgress';

interface DashboardStats {
  totalUnidades: number;
  unidadesCompletadas: number;
  porcentajeGeneral: number;
  avancesHoy: number;
  medicionesHoy: number;
  alertasPendientes: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalUnidades: getTotalUnidades(),
    unidadesCompletadas: 0,
    porcentajeGeneral: 0,
    avancesHoy: 0,
    medicionesHoy: 0,
    alertasPendientes: 0
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Cargar datos reales desde la base de datos
    const loadDashboardData = async () => {
      try {
        // Simulación de carga de datos
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setStats({
          totalUnidades: getTotalUnidades(),
          unidadesCompletadas: 156,
          porcentajeGeneral: 12.5,
          avancesHoy: 8,
          medicionesHoy: 3,
          alertasPendientes: 2
        });
      } catch (error) {
        console.error('Error cargando datos del dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const statCards = [
    {
      name: 'Total Unidades',
      value: stats.totalUnidades.toLocaleString(),
      icon: Building2,
      color: 'bg-primary-500',
      change: null
    },
    {
      name: 'Completadas',
      value: stats.unidadesCompletadas.toLocaleString(),
      icon: CheckCircle,
      color: 'bg-success-500',
      change: `${stats.porcentajeGeneral.toFixed(1)}%`
    },
    {
      name: 'Avances Hoy',
      value: stats.avancesHoy.toString(),
      icon: TrendingUp,
      color: 'bg-primary-500',
      change: '+12%'
    },
    {
      name: 'Mediciones Hoy',
      value: stats.medicionesHoy.toString(),
      icon: Activity,
      color: 'bg-warning-500',
      change: '+5%'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Resumen general del progreso de la obra</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">Última actualización</p>
          <p className="text-sm font-medium text-gray-900">
            {new Date().toLocaleString('es-CL')}
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <div key={stat.name} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                {stat.change && (
                  <p className="text-sm text-success-600 font-medium">
                    {stat.change}
                  </p>
                )}
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Alerts */}
      {stats.alertasPendientes > 0 && (
        <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="h-5 w-5 text-warning-600" />
            <div>
              <h3 className="text-sm font-medium text-warning-800">
                Tienes {stats.alertasPendientes} alertas pendientes
              </h3>
              <p className="text-sm text-warning-700">
                Revisa las mediciones que requieren atención.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Progress Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Progreso General
            </h3>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary-600">
                {stats.porcentajeGeneral.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500">Completado</p>
            </div>
          </div>
          <ProgressChart percentage={stats.porcentajeGeneral} />
        </div>

        {/* Tower Progress */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Progreso por Torre
          </h3>
          <TowerProgress />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Actividad Reciente
          </h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {/* TODO: Cargar actividad real */}
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <CheckCircle className="h-5 w-5 text-success-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  <span className="font-medium">Juan Pérez</span> completó el cableado alámbrico T1 en A101
                </p>
                <p className="text-xs text-gray-500">Hace 2 horas</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <Activity className="h-5 w-5 text-primary-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  <span className="font-medium">María González</span> registró medición en B205
                </p>
                <p className="text-xs text-gray-500">Hace 4 horas</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <Clock className="h-5 w-5 text-warning-500" />
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">
                  <span className="font-medium">Carlos Ruiz</span> inició instalación PAU en C308
                </p>
                <p className="text-xs text-gray-500">Hace 6 horas</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;