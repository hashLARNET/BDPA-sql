import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Activity, 
  Save, 
  X, 
  AlertTriangle,
  CheckCircle,
  Zap,
  Wifi,
  Cable
} from 'lucide-react';
import { TipoMedicion, ValoresMedicion, RANGOS_MEDICION } from '../../types';
import { getUnidadesDisponibles, TORRES, PISOS } from '../../utils/estructura-obra';
import { useMedicionesStore } from '../../store/mediciones.store';

const medicionSchema = z.object({
  torre: z.string().min(1, 'Selecciona una torre'),
  piso: z.number().min(1, 'Selecciona un piso'),
  identificador: z.string().min(1, 'Selecciona una unidad'),
  tipoMedicion: z.enum(['alambrico-t1', 'alambrico-t2', 'coaxial', 'fibra', 'wifi', 'certificacion']),
  valores: z.object({
    alambricoT1: z.number().optional(),
    alambricoT2: z.number().optional(),
    coaxial: z.number().optional(),
    potenciaTx: z.number().optional(),
    potenciaRx: z.number().optional(),
    atenuacion: z.number().optional(),
    wifi: z.number().optional(),
    certificacion: z.enum(['APROBADO', 'APROBADO_CON_OBSERVACIONES', 'RECHAZADO']).optional()
  }),
  observaciones: z.string().optional()
});

type MedicionFormData = z.infer<typeof medicionSchema>;

interface MedicionFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

const TIPOS_MEDICION: { value: TipoMedicion; label: string; icon: React.ComponentType<any> }[] = [
  { value: 'alambrico-t1', label: 'Alámbrico T1', icon: Cable },
  { value: 'alambrico-t2', label: 'Alámbrico T2', icon: Cable },
  { value: 'coaxial', label: 'Coaxial', icon: Cable },
  { value: 'fibra', label: 'Fibra Óptica', icon: Zap },
  { value: 'wifi', label: 'WiFi', icon: Wifi },
  { value: 'certificacion', label: 'Certificación', icon: CheckCircle }
];

const MedicionForm: React.FC<MedicionFormProps> = ({ onClose, onSuccess }) => {
  const [selectedSector, setSelectedSector] = useState('');
  const { createMedicion, isLoading } = useMedicionesStore();

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors }
  } = useForm<MedicionFormData>({
    resolver: zodResolver(medicionSchema),
    defaultValues: {
      torre: '',
      piso: 1,
      identificador: '',
      tipoMedicion: 'alambrico-t1',
      valores: {},
      observaciones: ''
    }
  });

  const watchedValues = watch();
  const unidadesDisponibles = watchedValues.torre && watchedValues.piso && selectedSector
    ? getUnidadesDisponibles(watchedValues.torre, watchedValues.piso, selectedSector)
    : [];

  const validateValue = (value: number, tipo: string): 'OK' | 'ADVERTENCIA' | 'FALLA' => {
    const rangos = RANGOS_MEDICION;
    
    switch (tipo) {
      case 'alambrico':
      case 'coaxial':
        if (value < rangos.ALAMBRICO.min || value > rangos.ALAMBRICO.max) return 'FALLA';
        if (value < rangos.ALAMBRICO.min + 5 || value > rangos.ALAMBRICO.max - 5) return 'ADVERTENCIA';
        return 'OK';
      
      case 'fibra-potencia':
        if (value < rangos.FIBRA_POTENCIA.min || value > rangos.FIBRA_POTENCIA.max) return 'FALLA';
        if (value < rangos.FIBRA_POTENCIA.min + 3 || value > rangos.FIBRA_POTENCIA.max - 3) return 'ADVERTENCIA';
        return 'OK';
      
      case 'wifi':
        if (value < rangos.WIFI.min || value > rangos.WIFI.max) return 'FALLA';
        if (value < rangos.WIFI.min + 10 || value > rangos.WIFI.max - 10) return 'ADVERTENCIA';
        return 'OK';
      
      default:
        return 'OK';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'OK': return <CheckCircle className="h-4 w-4 text-success-500" />;
      case 'ADVERTENCIA': return <AlertTriangle className="h-4 w-4 text-warning-500" />;
      case 'FALLA': return <AlertTriangle className="h-4 w-4 text-error-500" />;
      default: return null;
    }
  };

  const calculateOverallStatus = (valores: ValoresMedicion, tipo: TipoMedicion): 'OK' | 'ADVERTENCIA' | 'FALLA' => {
    const statuses: ('OK' | 'ADVERTENCIA' | 'FALLA')[] = [];

    switch (tipo) {
      case 'alambrico-t1':
        if (valores.alambricoT1) statuses.push(validateValue(valores.alambricoT1, 'alambrico'));
        break;
      case 'alambrico-t2':
        if (valores.alambricoT2) statuses.push(validateValue(valores.alambricoT2, 'alambrico'));
        break;
      case 'coaxial':
        if (valores.coaxial) statuses.push(validateValue(valores.coaxial, 'coaxial'));
        break;
      case 'fibra':
        if (valores.potenciaTx) statuses.push(validateValue(valores.potenciaTx, 'fibra-potencia'));
        if (valores.potenciaRx) statuses.push(validateValue(valores.potenciaRx, 'fibra-potencia'));
        break;
      case 'wifi':
        if (valores.wifi) statuses.push(validateValue(valores.wifi, 'wifi'));
        break;
      case 'certificacion':
        if (valores.certificacion === 'RECHAZADO') return 'FALLA';
        if (valores.certificacion === 'APROBADO_CON_OBSERVACIONES') return 'ADVERTENCIA';
        return 'OK';
    }

    if (statuses.includes('FALLA')) return 'FALLA';
    if (statuses.includes('ADVERTENCIA')) return 'ADVERTENCIA';
    return 'OK';
  };

  const onSubmit = async (data: MedicionFormData) => {
    try {
      const estado = calculateOverallStatus(data.valores, data.tipoMedicion);
      
      await createMedicion({
        ...data,
        fecha: new Date(),
        estado
      });
      
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Error creando medición:', error);
    }
  };

  const renderValueInputs = () => {
    const tipo = watchedValues.tipoMedicion;
    const valores = watchedValues.valores;

    switch (tipo) {
      case 'alambrico-t1':
        return (
          <div>
            <label className="form-label">Nivel Alámbrico T1 (dBμV)</label>
            <div className="flex items-center space-x-3">
              <Controller
                name="valores.alambricoT1"
                control={control}
                render={({ field }) => (
                  <input
                    {...field}
                    type="number"
                    step="0.1"
                    placeholder="45.0 - 75.0"
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || undefined)}
                    className="form-input flex-1"
                  />
                )}
              />
              {valores.alambricoT1 && getStatusIcon(validateValue(valores.alambricoT1, 'alambrico'))}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Rango normal: {RANGOS_MEDICION.ALAMBRICO.min} - {RANGOS_MEDICION.ALAMBRICO.max} dBμV
            </p>
          </div>
        );

      case 'alambrico-t2':
        return (
          <div>
            <label className="form-label">Nivel Alámbrico T2 (dBμV)</label>
            <div className="flex items-center space-x-3">
              <Controller
                name="valores.alambricoT2"
                control={control}
                render={({ field }) => (
                  <input
                    {...field}
                    type="number"
                    step="0.1"
                    placeholder="45.0 - 75.0"
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || undefined)}
                    className="form-input flex-1"
                  />
                )}
              />
              {valores.alambricoT2 && getStatusIcon(validateValue(valores.alambricoT2, 'alambrico'))}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Rango normal: {RANGOS_MEDICION.ALAMBRICO.min} - {RANGOS_MEDICION.ALAMBRICO.max} dBμV
            </p>
          </div>
        );

      case 'coaxial':
        return (
          <div>
            <label className="form-label">Nivel Coaxial (dBμV)</label>
            <div className="flex items-center space-x-3">
              <Controller
                name="valores.coaxial"
                control={control}
                render={({ field }) => (
                  <input
                    {...field}
                    type="number"
                    step="0.1"
                    placeholder="45.0 - 75.0"
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || undefined)}
                    className="form-input flex-1"
                  />
                )}
              />
              {valores.coaxial && getStatusIcon(validateValue(valores.coaxial, 'coaxial'))}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Rango normal: {RANGOS_MEDICION.COAXIAL.min} - {RANGOS_MEDICION.COAXIAL.max} dBμV
            </p>
          </div>
        );

      case 'fibra':
        return (
          <div className="space-y-4">
            <div>
              <label className="form-label">Potencia TX (dBm)</label>
              <div className="flex items-center space-x-3">
                <Controller
                  name="valores.potenciaTx"
                  control={control}
                  render={({ field }) => (
                    <input
                      {...field}
                      type="number"
                      step="0.1"
                      placeholder="-30.0 - -8.0"
                      onChange={(e) => field.onChange(parseFloat(e.target.value) || undefined)}
                      className="form-input flex-1"
                    />
                  )}
                />
                {valores.potenciaTx && getStatusIcon(validateValue(valores.potenciaTx, 'fibra-potencia'))}
              </div>
            </div>
            
            <div>
              <label className="form-label">Potencia RX (dBm)</label>
              <div className="flex items-center space-x-3">
                <Controller
                  name="valores.potenciaRx"
                  control={control}
                  render={({ field }) => (
                    <input
                      {...field}
                      type="number"
                      step="0.1"
                      placeholder="-30.0 - -8.0"
                      onChange={(e) => field.onChange(parseFloat(e.target.value) || undefined)}
                      className="form-input flex-1"
                    />
                  )}
                />
                {valores.potenciaRx && getStatusIcon(validateValue(valores.potenciaRx, 'fibra-potencia'))}
              </div>
            </div>
            
            <div>
              <label className="form-label">Atenuación (dB)</label>
              <Controller
                name="valores.atenuacion"
                control={control}
                render={({ field }) => (
                  <input
                    {...field}
                    type="number"
                    step="0.01"
                    placeholder="0.00 - 0.50"
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || undefined)}
                    className="form-input"
                  />
                )}
              />
              <p className="text-xs text-gray-500 mt-1">
                Máximo recomendado: {RANGOS_MEDICION.FIBRA_ATENUACION.max} dB/km
              </p>
            </div>
          </div>
        );

      case 'wifi':
        return (
          <div>
            <label className="form-label">Nivel WiFi (dBm)</label>
            <div className="flex items-center space-x-3">
              <Controller
                name="valores.wifi"
                control={control}
                render={({ field }) => (
                  <input
                    {...field}
                    type="number"
                    step="1"
                    placeholder="-80 - -30"
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || undefined)}
                    className="form-input flex-1"
                  />
                )}
              />
              {valores.wifi && getStatusIcon(validateValue(valores.wifi, 'wifi'))}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Rango normal: {RANGOS_MEDICION.WIFI.min} - {RANGOS_MEDICION.WIFI.max} dBm
            </p>
          </div>
        );

      case 'certificacion':
        return (
          <div>
            <label className="form-label">Estado de Certificación</label>
            <Controller
              name="valores.certificacion"
              control={control}
              render={({ field }) => (
                <select {...field} className="form-input">
                  <option value="">Seleccionar...</option>
                  <option value="APROBADO">Aprobado</option>
                  <option value="APROBADO_CON_OBSERVACIONES">Aprobado con Observaciones</option>
                  <option value="RECHAZADO">Rechazado</option>
                </select>
              )}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Activity className="h-6 w-6 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Registrar Medición
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {/* Ubicación */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="form-label">Torre</label>
              <Controller
                name="torre"
                control={control}
                render={({ field }) => (
                  <select
                    {...field}
                    className={`form-input ${errors.torre ? 'form-input-error' : ''}`}
                    onChange={(e) => {
                      field.onChange(e.target.value);
                      setSelectedSector('');
                      setValue('identificador', '');
                    }}
                  >
                    <option value="">Seleccionar...</option>
                    {TORRES.map(torre => (
                      <option key={torre} value={torre}>Torre {torre}</option>
                    ))}
                  </select>
                )}
              />
              {errors.torre && <p className="form-error">{errors.torre.message}</p>}
            </div>

            <div>
              <label className="form-label">Piso</label>
              <Controller
                name="piso"
                control={control}
                render={({ field }) => (
                  <select
                    {...field}
                    value={field.value.toString()}
                    onChange={(e) => {
                      field.onChange(parseInt(e.target.value));
                      setValue('identificador', '');
                    }}
                    className="form-input"
                  >
                    {PISOS.map(piso => (
                      <option key={piso} value={piso}>Piso {piso}</option>
                    ))}
                  </select>
                )}
              />
            </div>

            <div>
              <label className="form-label">Unidad</label>
              <Controller
                name="identificador"
                control={control}
                render={({ field }) => (
                  <select
                    {...field}
                    className={`form-input ${errors.identificador ? 'form-input-error' : ''}`}
                    disabled={!selectedSector}
                  >
                    <option value="">Seleccionar...</option>
                    {unidadesDisponibles.map(unidad => (
                      <option key={unidad} value={unidad}>{unidad}</option>
                    ))}
                  </select>
                )}
              />
              {errors.identificador && <p className="form-error">{errors.identificador.message}</p>}
            </div>
          </div>

          {/* Sector Selection Helper */}
          {watchedValues.torre && (
            <div>
              <label className="form-label">Sector</label>
              <div className="flex space-x-2">
                {['Norte', 'Poniente', 'Oriente'].map(sector => (
                  <button
                    key={sector}
                    type="button"
                    onClick={() => {
                      setSelectedSector(sector);
                      setValue('identificador', '');
                    }}
                    className={`px-3 py-2 text-sm rounded-md border transition-colors ${
                      selectedSector === sector
                        ? 'bg-primary-100 border-primary-300 text-primary-700'
                        : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                    disabled={watchedValues.torre === 'C' || watchedValues.torre === 'H' ? sector === 'Norte' : false}
                  >
                    {sector}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Tipo de Medición */}
          <div>
            <label className="form-label">Tipo de Medición</label>
            <Controller
              name="tipoMedicion"
              control={control}
              render={({ field }) => (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {TIPOS_MEDICION.map(({ value, label, icon: Icon }) => (
                    <button
                      key={value}
                      type="button"
                      onClick={() => {
                        field.onChange(value);
                        setValue('valores', {});
                      }}
                      className={`p-3 text-sm rounded-lg border transition-colors flex items-center space-x-2 ${
                        field.value === value
                          ? 'bg-primary-100 border-primary-300 text-primary-700'
                          : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      <span>{label}</span>
                    </button>
                  ))}
                </div>
              )}
            />
          </div>

          {/* Valores de Medición */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Valores de Medición
            </h3>
            {renderValueInputs()}
          </div>

          {/* Observaciones */}
          <div>
            <label className="form-label">Observaciones (Opcional)</label>
            <Controller
              name="observaciones"
              control={control}
              render={({ field }) => (
                <textarea
                  {...field}
                  rows={3}
                  placeholder="Comentarios adicionales sobre la medición..."
                  className="form-input resize-none"
                />
              )}
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
              disabled={isLoading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin h-4 w-4 border border-white border-t-transparent rounded-full" />
                  <span>Guardando...</span>
                </div>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Guardar Medición
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MedicionForm;