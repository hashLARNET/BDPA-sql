import { create } from 'zustand';
import { Medicion, TipoMedicion, ValoresMedicion } from '../types';
import { prisma } from '../services/database';
import { useSyncStore } from './sync.store';
import { useAuthStore } from './auth.store';
import * as XLSX from 'xlsx';

interface CreateMedicionData {
  torre: string;
  piso: number;
  identificador: string;
  tipoMedicion: TipoMedicion;
  valores: ValoresMedicion;
  estado: 'OK' | 'ADVERTENCIA' | 'FALLA';
  observaciones?: string;
  fecha: Date;
}

interface MedicionesState {
  mediciones: Medicion[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  loadMediciones: () => Promise<void>;
  createMedicion: (data: CreateMedicionData) => Promise<void>;
  updateMedicion: (id: string, data: Partial<Medicion>) => Promise<void>;
  deleteMedicion: (id: string) => Promise<void>;
  exportToExcel: (mediciones?: Medicion[]) => Promise<void>;
  clearError: () => void;
}

export const useMedicionesStore = create<MedicionesState>((set, get) => ({
  mediciones: [],
  isLoading: false,
  error: null,

  loadMediciones: async () => {
    set({ isLoading: true, error: null });
    
    try {
      const mediciones = await prisma.medicion.findMany({
        include: {
          usuario: {
            select: {
              id: true,
              nombre: true,
              username: true
            }
          }
        },
        orderBy: {
          fecha: 'desc'
        }
      });

      const mappedMediciones: Medicion[] = mediciones.map(medicion => ({
        id: medicion.id,
        obraId: medicion.obraId,
        fecha: medicion.fecha,
        torre: medicion.torre,
        piso: medicion.piso,
        identificador: medicion.identificador,
        tipoMedicion: medicion.tipoMedicion as TipoMedicion,
        valores: JSON.parse(medicion.valores) as ValoresMedicion,
        estado: medicion.estado as any,
        usuarioId: medicion.usuarioId,
        observaciones: medicion.observaciones,
        syncStatus: medicion.syncStatus as any,
        createdAt: medicion.createdAt,
        updatedAt: medicion.updatedAt
      }));

      set({ mediciones: mappedMediciones, isLoading: false });
    } catch (error) {
      console.error('Error cargando mediciones:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Error cargando mediciones',
        isLoading: false 
      });
    }
  },

  createMedicion: async (data: CreateMedicionData) => {
    set({ isLoading: true, error: null });
    
    try {
      const { user } = useAuthStore.getState();
      if (!user) throw new Error('Usuario no autenticado');

      const medicion = await prisma.medicion.create({
        data: {
          obraId: 'los-encinos-001',
          fecha: data.fecha,
          torre: data.torre,
          piso: data.piso,
          identificador: data.identificador,
          tipoMedicion: data.tipoMedicion,
          valores: JSON.stringify(data.valores),
          estado: data.estado,
          usuarioId: user.id,
          observaciones: data.observaciones,
          syncStatus: 'local'
        }
      });

      // Agregar a cola de sincronización
      const { addToQueue } = useSyncStore.getState();
      addToQueue({
        type: 'medicion',
        action: 'create',
        itemId: medicion.id,
        data: medicion
      });

      await get().loadMediciones();
      set({ isLoading: false });
    } catch (error) {
      console.error('Error creando medición:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Error creando medición',
        isLoading: false 
      });
      throw error;
    }
  },

  updateMedicion: async (id: string, data: Partial<Medicion>) => {
    set({ isLoading: true, error: null });
    
    try {
      await prisma.medicion.update({
        where: { id },
        data: {
          ...data,
          valores: data.valores ? JSON.stringify(data.valores) : undefined,
          updatedAt: new Date(),
          syncStatus: 'local'
        }
      });

      const { addToQueue } = useSyncStore.getState();
      addToQueue({
        type: 'medicion',
        action: 'update',
        itemId: id,
        data
      });

      await get().loadMediciones();
      set({ isLoading: false });
    } catch (error) {
      console.error('Error actualizando medición:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Error actualizando medición',
        isLoading: false 
      });
      throw error;
    }
  },

  deleteMedicion: async (id: string) => {
    set({ isLoading: true, error: null });
    
    try {
      await prisma.medicion.delete({
        where: { id }
      });

      const { addToQueue } = useSyncStore.getState();
      addToQueue({
        type: 'medicion',
        action: 'delete',
        itemId: id,
        data: {}
      });

      await get().loadMediciones();
      set({ isLoading: false });
    } catch (error) {
      console.error('Error eliminando medición:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Error eliminando medición',
        isLoading: false 
      });
      throw error;
    }
  },

  exportToExcel: async (mediciones?: Medicion[]) => {
    try {
      const dataToExport = mediciones || get().mediciones;
      
      const excelData = dataToExport.map(medicion => {
        const valores = medicion.valores;
        return {
          'Fecha': medicion.fecha.toLocaleDateString('es-CL'),
          'Torre': medicion.torre,
          'Piso': medicion.piso,
          'Unidad': medicion.identificador,
          'Tipo Medición': medicion.tipoMedicion,
          'Alámbrico T1': valores.alambricoT1 || '',
          'Alámbrico T2': valores.alambricoT2 || '',
          'Coaxial': valores.coaxial || '',
          'Potencia TX': valores.potenciaTx || '',
          'Potencia RX': valores.potenciaRx || '',
          'Atenuación': valores.atenuacion || '',
          'WiFi': valores.wifi || '',
          'Certificación': valores.certificacion || '',
          'Estado': medicion.estado,
          'Observaciones': medicion.observaciones || '',
          'Estado Sync': medicion.syncStatus,
          'Creado': medicion.createdAt.toLocaleDateString('es-CL')
        };
      });

      const worksheet = XLSX.utils.json_to_sheet(excelData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Mediciones');

      // Ajustar ancho de columnas
      const colWidths = [
        { wch: 12 }, // Fecha
        { wch: 8 },  // Torre
        { wch: 8 },  // Piso
        { wch: 12 }, // Unidad
        { wch: 15 }, // Tipo Medición
        { wch: 12 }, // Alámbrico T1
        { wch: 12 }, // Alámbrico T2
        { wch: 12 }, // Coaxial
        { wch: 12 }, // Potencia TX
        { wch: 12 }, // Potencia RX
        { wch: 12 }, // Atenuación
        { wch: 12 }, // WiFi
        { wch: 15 }, // Certificación
        { wch: 12 }, // Estado
        { wch: 30 }, // Observaciones
        { wch: 12 }, // Estado Sync
        { wch: 12 }  // Creado
      ];
      worksheet['!cols'] = colWidths;

      const fileName = `mediciones_los_encinos_${new Date().toISOString().split('T')[0]}.xlsx`;
      XLSX.writeFile(workbook, fileName);
    } catch (error) {
      console.error('Error exportando a Excel:', error);
      throw error;
    }
  },

  clearError: () => set({ error: null })
}));