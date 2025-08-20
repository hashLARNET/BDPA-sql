import React, { useState, useRef } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Camera, 
  Upload, 
  Save, 
  X, 
  MapPin, 
  Calendar,
  Percent,
  FileText,
  Building2
} from 'lucide-react';
import { 
  TORRES, 
  PISOS, 
  getSectoresDisponibles, 
  getUnidadesDisponibles 
} from '../../utils/estructura-obra';
import { CategoriaAvance } from '../../types';
import { useAvancesStore } from '../../store/avances.store';

const avanceSchema = z.object({
  torre: z.string().min(1, 'Selecciona una torre'),
  piso: z.number().min(1, 'Selecciona un piso'),
  sector: z.string().optional(),
  tipoEspacio: z.enum(['unidad', 'sotu', 'shaft', 'lateral', 'antena']),
  ubicacion: z.string().min(1, 'Ingresa la ubicación'),
  categoria: z.string().min(1, 'Selecciona una categoría'),
  porcentaje: z.number().min(0).max(100, 'El porcentaje debe estar entre 0 y 100'),
  observaciones: z.string().optional()
});

type AvanceFormData = z.infer<typeof avanceSchema>;

interface AvanceFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

const CATEGORIAS_POR_TIPO: Record<string, CategoriaAvance[]> = {
  unidad: [
    'Cableado alámbrico T1',
    'Cableado inalámbrico T1/T2',
    'Instalación PAU',
    'Conexión PAU',
    'Fibra Óptica'
  ],
  sotu: [
    'Instalación de dispositivos',
    'Conexiones de entrada',
    'Conexiones de salida',
    'Configuración',
    'Certificación'
  ],
  shaft: [
    'Tendido de troncales',
    'Instalación de derivadores',
    'Conexiones a SOTU',
    'Sellado y seguridad'
  ],
  lateral: [
    'Tendido coaxial PAU-SOTU',
    'Tendido F.O. PAU-SOTU',
    'Protección y acabados'
  ],
  antena: [
    'Instalación física',
    'Orientación y ajuste',
    'Cableado de bajada',
    'Pruebas de señal'
  ]
};

const AvanceForm: React.FC<AvanceFormProps> = ({ onClose, onSuccess }) => {
  const [selectedPhoto, setSelectedPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { createAvance, isLoading } = useAvancesStore();

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors }
  } = useForm<AvanceFormData>({
    resolver: zodResolver(avanceSchema),
    defaultValues: {
      torre: '',
      piso: 1,
      sector: '',
      tipoEspacio: 'unidad',
      ubicacion: '',
      categoria: '',
      porcentaje: 0,
      observaciones: ''
    }
  });

  const watchedValues = watch();
  const sectoresDisponibles = watchedValues.torre ? getSectoresDisponibles(watchedValues.torre) : [];
  const unidadesDisponibles = watchedValues.torre && watchedValues.piso && watchedValues.sector 
    ? getUnidadesDisponibles(watchedValues.torre, watchedValues.piso, watchedValues.sector)
    : [];
  const categoriasDisponibles = CATEGORIAS_POR_TIPO[watchedValues.tipoEspacio] || [];

  const handlePhotoSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedPhoto(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = () => {
    setSelectedPhoto(null);
    setPhotoPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const onSubmit = async (data: AvanceFormData) => {
    try {
      await createAvance({
        ...data,
        fecha: new Date(),
        foto: selectedPhoto ? {
          file: selectedPhoto,
          path: `temp/${Date.now()}_${selectedPhoto.name}`
        } : undefined
      });
      
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Error creando avance:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Building2 className="h-6 w-6 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              Registrar Avance
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
                      setValue('sector', '');
                      setValue('ubicacion', '');
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
                      setValue('ubicacion', '');
                    }}
                    className={`form-input ${errors.piso ? 'form-input-error' : ''}`}
                  >
                    {PISOS.map(piso => (
                      <option key={piso} value={piso}>Piso {piso}</option>
                    ))}
                  </select>
                )}
              />
              {errors.piso && <p className="form-error">{errors.piso.message}</p>}
            </div>

            <div>
              <label className="form-label">Tipo de Espacio</label>
              <Controller
                name="tipoEspacio"
                control={control}
                render={({ field }) => (
                  <select
                    {...field}
                    className="form-input"
                    onChange={(e) => {
                      field.onChange(e.target.value);
                      setValue('categoria', '');
                    }}
                  >
                    <option value="unidad">Unidad</option>
                    <option value="sotu">SOTU</option>
                    <option value="shaft">Shaft</option>
                    <option value="lateral">Lateral</option>
                    <option value="antena">Antena</option>
                  </select>
                )}
              />
            </div>
          </div>

          {/* Sector y Ubicación */}
          {watchedValues.tipoEspacio === 'unidad' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="form-label">Sector</label>
                <Controller
                  name="sector"
                  control={control}
                  render={({ field }) => (
                    <select
                      {...field}
                      className="form-input"
                      onChange={(e) => {
                        field.onChange(e.target.value);
                        setValue('ubicacion', '');
                      }}
                      disabled={!watchedValues.torre}
                    >
                      <option value="">Seleccionar...</option>
                      {sectoresDisponibles.map(sector => (
                        <option key={sector} value={sector}>{sector}</option>
                      ))}
                    </select>
                  )}
                />
              </div>

              <div>
                <label className="form-label">Unidad</label>
                <Controller
                  name="ubicacion"
                  control={control}
                  render={({ field }) => (
                    <select
                      {...field}
                      className={`form-input ${errors.ubicacion ? 'form-input-error' : ''}`}
                      disabled={!watchedValues.sector}
                    >
                      <option value="">Seleccionar...</option>
                      {unidadesDisponibles.map(unidad => (
                        <option key={unidad} value={unidad}>{unidad}</option>
                      ))}
                    </select>
                  )}
                />
                {errors.ubicacion && <p className="form-error">{errors.ubicacion.message}</p>}
              </div>
            </div>
          )}

          {/* Ubicación manual para otros tipos */}
          {watchedValues.tipoEspacio !== 'unidad' && (
            <div>
              <label className="form-label">Ubicación</label>
              <Controller
                name="ubicacion"
                control={control}
                render={({ field }) => (
                  <input
                    {...field}
                    type="text"
                    placeholder="Ej: SOTU-A1, Shaft-Norte, etc."
                    className={`form-input ${errors.ubicacion ? 'form-input-error' : ''}`}
                  />
                )}
              />
              {errors.ubicacion && <p className="form-error">{errors.ubicacion.message}</p>}
            </div>
          )}

          {/* Categoría y Porcentaje */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="form-label">Categoría de Trabajo</label>
              <Controller
                name="categoria"
                control={control}
                render={({ field }) => (
                  <select
                    {...field}
                    className={`form-input ${errors.categoria ? 'form-input-error' : ''}`}
                  >
                    <option value="">Seleccionar...</option>
                    {categoriasDisponibles.map(categoria => (
                      <option key={categoria} value={categoria}>{categoria}</option>
                    ))}
                  </select>
                )}
              />
              {errors.categoria && <p className="form-error">{errors.categoria.message}</p>}
            </div>

            <div>
              <label className="form-label">Porcentaje de Avance</label>
              <div className="relative">
                <Controller
                  name="porcentaje"
                  control={control}
                  render={({ field }) => (
                    <input
                      {...field}
                      type="number"
                      min="0"
                      max="100"
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      className={`form-input pr-8 ${errors.porcentaje ? 'form-input-error' : ''}`}
                    />
                  )}
                />
                <Percent className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              </div>
              {errors.porcentaje && <p className="form-error">{errors.porcentaje.message}</p>}
            </div>
          </div>

          {/* Foto */}
          <div>
            <label className="form-label">Fotografía (Opcional)</label>
            <div className="space-y-4">
              {!photoPreview ? (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-sm text-gray-600 mb-4">
                    Selecciona una foto para documentar el avance
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoSelect}
                    className="hidden"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="btn-secondary"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Seleccionar Foto
                  </button>
                </div>
              ) : (
                <div className="relative">
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-full h-48 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={removePhoto}
                    className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
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
                  placeholder="Comentarios adicionales sobre el avance..."
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
                  Guardar Avance
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AvanceForm;