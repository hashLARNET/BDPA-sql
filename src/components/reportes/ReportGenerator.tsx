import React, { useState } from 'react';
import { 
  BarChart3, 
  Download, 
  Calendar,
  Building2,
  TrendingUp,
  Activity,
  FileText,
  Printer
} from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { useAvancesStore } from '../../store/avances.store';
import { useMedicionesStore } from '../../store/mediciones.store';
import { TORRES } from '../../utils/estructura-obra';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';

const ReportGenerator: React.FC = () => {
  const [reportType, setReportType] = useState<'avances' | 'mediciones' | 'general'>('general');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [selectedTorres, setSelectedTorres] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const { avances, exportToExcel: exportAvances } = useAvancesStore();
  const { mediciones, exportToExcel: exportMediciones } = useMedicionesStore();

  const generateGeneralReport = async () => {
    setIsGenerating(true);
    try {
      // Calcular estadísticas generales
      const totalUnidades = 1247;
      const avancesCompletados = avances.filter(a => a.porcentaje === 100).length;
      const medicionesOK = mediciones.filter(m => m.estado === 'OK').length;
      const medicionesFalla = mediciones.filter(m => m.estado === 'FALLA').length;

      // Progreso por torre
      const progresoTorres = TORRES.map(torre => {
        const avancesTorre = avances.filter(a => a.torre === torre);
        const promedioProgreso = avancesTorre.length > 0 
          ? avancesTorre.reduce((sum, a) => sum + a.porcentaje, 0) / avancesTorre.length 
          : 0;
        return { torre, progreso: promedioProgreso, avances: avancesTorre.length };
      });

      // Crear Excel con múltiples hojas
      const workbook = XLSX.utils.book_new();

      // Hoja 1: Resumen General
      const resumenData = [
        ['REPORTE GENERAL - LOS ENCINOS', ''],
        ['Fecha de Generación', new Date().toLocaleDateString('es-CL')],
        ['', ''],
        ['ESTADÍSTICAS GENERALES', ''],
        ['Total Unidades', totalUnidades],
        ['Avances Registrados', avances.length],
        ['Avances Completados (100%)', avancesCompletados],
        ['Porcentaje General', `${((avancesCompletados / totalUnidades) * 100).toFixed(1)}%`],
        ['', ''],
        ['MEDICIONES', ''],
        ['Total Mediciones', mediciones.length],
        ['Mediciones OK', medicionesOK],
        ['Mediciones con Falla', medicionesFalla],
        ['Tasa de Éxito', `${((medicionesOK / mediciones.length) * 100).toFixed(1)}%`]
      ];

      const resumenSheet = XLSX.utils.aoa_to_sheet(resumenData);
      XLSX.utils.book_append_sheet(workbook, resumenSheet, 'Resumen General');

      // Hoja 2: Progreso por Torre
      const torreData = [
        ['Torre', 'Avances Registrados', 'Progreso Promedio', 'Estado'],
        ...progresoTorres.map(t => [
          `Torre ${t.torre}`,
          t.avances,
          `${t.progreso.toFixed(1)}%`,
          t.progreso >= 80 ? 'Avanzado' : t.progreso >= 50 ? 'En Progreso' : 'Inicial'
        ])
      ];

      const torreSheet = XLSX.utils.aoa_to_sheet(torreData);
      XLSX.utils.book_append_sheet(workbook, torreSheet, 'Progreso por Torre');

      // Hoja 3: Avances Detallados
      if (avances.length > 0) {
        const avancesData = [
          ['Fecha', 'Torre', 'Piso', 'Sector', 'Ubicación', 'Categoría', 'Porcentaje', 'Observaciones'],
          ...avances.map(a => [
            format(a.fecha, 'dd/MM/yyyy', { locale: es }),
            a.torre,
            a.piso,
            a.sector || '',
            a.ubicacion,
            a.categoria,
            `${a.porcentaje}%`,
            a.observaciones || ''
          ])
        ];

        const avancesSheet = XLSX.utils.aoa_to_sheet(avancesData);
        XLSX.utils.book_append_sheet(workbook, avancesSheet, 'Avances Detallados');
      }

      // Hoja 4: Mediciones Detalladas
      if (mediciones.length > 0) {
        const medicionesData = [
          ['Fecha', 'Torre', 'Piso', 'Unidad', 'Tipo', 'Estado', 'Valores', 'Observaciones'],
          ...mediciones.map(m => [
            format(m.fecha, 'dd/MM/yyyy', { locale: es }),
            m.torre,
            m.piso,
            m.identificador,
            m.tipoMedicion,
            m.estado,
            JSON.stringify(m.valores),
            m.observaciones || ''
          ])
        ];

        const medicionesSheet = XLSX.utils.aoa_to_sheet(medicionesData);
        XLSX.utils.book_append_sheet(workbook, medicionesSheet, 'Mediciones Detalladas');
      }

      // Guardar archivo
      const fileName = `reporte_general_los_encinos_${format(new Date(), 'yyyy-MM-dd')}.xlsx`;
      XLSX.writeFile(workbook, fileName);

    } catch (error) {
      console.error('Error generando reporte:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const generatePDFReport = async () => {
    setIsGenerating(true);
    try {
      const pdf = new jsPDF();
      
      // Título
      pdf.setFontSize(20);
      pdf.text('REPORTE DE OBRA - LOS ENCINOS', 20, 30);
      
      pdf.setFontSize(12);
      pdf.text(`Fecha: ${format(new Date(), 'dd/MM/yyyy', { locale: es })}`, 20, 45);
      
      // Estadísticas generales
      pdf.setFontSize(16);
      pdf.text('RESUMEN GENERAL', 20, 65);
      
      pdf.setFontSize(12);
      const stats = [
        `Total Unidades: 1,247`,
        `Avances Registrados: ${avances.length}`,
        `Mediciones Realizadas: ${mediciones.length}`,
        `Progreso General: ${((avances.filter(a => a.porcentaje === 100).length / 1247) * 100).toFixed(1)}%`
      ];
      
      stats.forEach((stat, index) => {
        pdf.text(stat, 20, 80 + (index * 10));
      });

      // Progreso por torre
      pdf.setFontSize(16);
      pdf.text('PROGRESO POR TORRE', 20, 130);
      
      pdf.setFontSize(10);
      TORRES.forEach((torre, index) => {
        const avancesTorre = avances.filter(a => a.torre === torre);
        const progreso = avancesTorre.length > 0 
          ? (avancesTorre.reduce((sum, a) => sum + a.porcentaje, 0) / avancesTorre.length).toFixed(1)
          : '0.0';
        
        pdf.text(`Torre ${torre}: ${progreso}% (${avancesTorre.length} avances)`, 20, 145 + (index * 8));
      });

      const fileName = `reporte_los_encinos_${format(new Date(), 'yyyy-MM-dd')}.pdf`;
      pdf.save(fileName);

    } catch (error) {
      console.error('Error generando PDF:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reportes</h1>
          <p className="text-gray-600">Generación de reportes y análisis de datos</p>
        </div>
      </div>

      {/* Report Configuration */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuración de Reporte</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Tipo de Reporte */}
          <div>
            <label className="form-label">Tipo de Reporte</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value as any)}
              className="form-input"
            >
              <option value="general">Reporte General</option>
              <option value="avances">Solo Avances</option>
              <option value="mediciones">Solo Mediciones</option>
            </select>
          </div>

          {/* Rango de Fechas */}
          <div>
            <label className="form-label">Fecha Desde</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              className="form-input"
            />
          </div>

          <div>
            <label className="form-label">Fecha Hasta</label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
              className="form-input"
            />
          </div>
        </div>

        {/* Torres Selection */}
        <div className="mt-6">
          <label className="form-label">Torres a Incluir</label>
          <div className="grid grid-cols-5 gap-3">
            {TORRES.map(torre => (
              <label key={torre} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={selectedTorres.includes(torre)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedTorres(prev => [...prev, torre]);
                    } else {
                      setSelectedTorres(prev => prev.filter(t => t !== torre));
                    }
                  }}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm">Torre {torre}</span>
              </label>
            ))}
          </div>
          <button
            onClick={() => setSelectedTorres(selectedTorres.length === TORRES.length ? [] : [...TORRES])}
            className="mt-2 text-sm text-primary-600 hover:text-primary-700"
          >
            {selectedTorres.length === TORRES.length ? 'Deseleccionar Todas' : 'Seleccionar Todas'}
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Avances</p>
              <p className="text-2xl font-bold text-gray-900">{avances.length}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-primary-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Mediciones</p>
              <p className="text-2xl font-bold text-gray-900">{mediciones.length}</p>
            </div>
            <Activity className="h-8 w-8 text-warning-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completados</p>
              <p className="text-2xl font-bold text-success-600">
                {avances.filter(a => a.porcentaje === 100).length}
              </p>
            </div>
            <Building2 className="h-8 w-8 text-success-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Progreso General</p>
              <p className="text-2xl font-bold text-primary-600">
                {((avances.filter(a => a.porcentaje === 100).length / 1247) * 100).toFixed(1)}%
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-primary-500" />
          </div>
        </div>
      </div>

      {/* Report Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Generar Reportes</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={generateGeneralReport}
            disabled={isGenerating}
            className="btn-primary flex items-center justify-center"
          >
            <Download className="h-4 w-4 mr-2" />
            Excel Completo
          </button>

          <button
            onClick={generatePDFReport}
            disabled={isGenerating}
            className="btn-secondary flex items-center justify-center"
          >
            <FileText className="h-4 w-4 mr-2" />
            PDF Resumen
          </button>

          <button
            onClick={() => exportAvances()}
            disabled={isGenerating}
            className="btn-secondary flex items-center justify-center"
          >
            <TrendingUp className="h-4 w-4 mr-2" />
            Solo Avances
          </button>

          <button
            onClick={() => exportMediciones()}
            disabled={isGenerating}
            className="btn-secondary flex items-center justify-center"
          >
            <Activity className="h-4 w-4 mr-2" />
            Solo Mediciones
          </button>
        </div>

        {isGenerating && (
          <div className="mt-4 flex items-center justify-center text-primary-600">
            <div className="animate-spin h-5 w-5 border border-primary-500 border-t-transparent rounded-full mr-2" />
            <span>Generando reporte...</span>
          </div>
        )}
      </div>

      {/* Report Templates */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Plantillas de Reportes</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Reporte Diario</h4>
            <p className="text-sm text-gray-600 mb-3">
              Avances y mediciones del día actual
            </p>
            <button className="btn-secondary text-sm">
              <Calendar className="h-4 w-4 mr-1" />
              Generar
            </button>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Reporte Semanal</h4>
            <p className="text-sm text-gray-600 mb-3">
              Resumen de progreso de los últimos 7 días
            </p>
            <button className="btn-secondary text-sm">
              <BarChart3 className="h-4 w-4 mr-1" />
              Generar
            </button>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Reporte por Torre</h4>
            <p className="text-sm text-gray-600 mb-3">
              Análisis detallado por torre específica
            </p>
            <button className="btn-secondary text-sm">
              <Building2 className="h-4 w-4 mr-1" />
              Generar
            </button>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Reporte de Calidad</h4>
            <p className="text-sm text-gray-600 mb-3">
              Mediciones y certificaciones técnicas
            </p>
            <button className="btn-secondary text-sm">
              <Printer className="h-4 w-4 mr-1" />
              Generar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportGenerator;