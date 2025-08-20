import { create } from 'zustand';
import { Avance } from '../types';
import { prisma } from '../services/database';
import { useSyncStore } from './sync.store';
import { useAuthStore } from './auth.store';
import * as XLSX from 'xlsx';

interface CreateAvanceData {
  torre: string;
  piso: number;
  sector?: string;
  tipoEspacio: 'unidad' | 'sotu' | 'shaft' | 'lateral' | 'antena';
  ubicacion: string;
  categoria: string;
  porcentaje: number;
  observaciones?: string;
  fecha: Date;
  foto?: {
    file: File;
    path: string;
  };
}

interface AvancesState {
  avances: Avance[];
  isLoading: boolean;
  error: string | null;
  
  // Actions
  loadAvances: () => Promise<void>;
  createAvance: (data: CreateAvanceData) => Promise<void>;
  updateAvance: (id: string, data: Partial<Avance>) => Promise<void>;
  deleteAvance: (id: string) => Promise<void>;
  exportToExcel: (avances?: Avance[]) => Promise<void>;
  clearError: () => void;
}

export const useAvancesStore = create<AvancesState>((set, get) => ({
  avances: [],
  isLoading: false,
  error: null,

  loadAvances: async () => {
    set({ isLoading: true, error: null });
    
    try {
      const avances = await prisma.avance.findMany({
        where: {
          deletedAt: null
        },
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

      const mappedAvances: Avance[] = avances.map(avance => ({
        id: avance.id,
        obraId: avance.obraId,
        fecha: avance.fecha,
        torre: avance.torre,
        piso: avance.piso,
        sector: avance.sector as any,
        tipoEspacio: avance.tipoEspacio as any,
        ubicacion: avance.ubicacion,
        categoria: avance.categoria as any,
        porcentaje: avance.porcentaje,
        fotoPath: avance.fotoPath,
        fotoUrl: avance.fotoUrl,
        observaciones: avance.observaciones,
        usuarioId: avance.usuarioId,
        syncStatus: avance.syncStatus as any,
        lastSync: avance.lastSync,
        createdAt: avance.createdAt,
        updatedAt: avance.updatedAt,
        deletedAt: avance.deletedAt
      }));

      set({ avances: mappedAvances, isLoading: false });
    } catch (error) {
      console.error('Error cargando avances:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Error cargando avances',
        isLoading: false 
      });
    }
  },

  createAvance: async (data: CreateAvanceData) => {
    set({ isLoading: true, error: null });
    
    try {
      const { user } = useAuthStore.getState();
      if (!user) throw new Error('Usuario no autenticado');

      // Crear avance en base de datos local
      const avance = await prisma.avance.create({
        data: {
          obraId: 'los-encinos-001',
          fecha: data.fecha,
          torre: data.torre,
          piso: data.piso,
          sector: data.sector,
          tipoEspacio: data.tipoEspacio,
          ubicacion: data.ubicacion,
          categoria: data.categoria,
          porcentaje: data.porcentaje,
          observaciones: data.observaciones,
          usuarioId: user.id,
          fotoPath: data.foto?.path,
          syncStatus: 'local'
        }
      });

      // Agregar a cola de sincronización
      const { addToQueue } = useSyncStore.getState();
      addToQueue({
        type: 'avance',
        action: 'create',
        itemId: avance.id,
        data: {
          ...avance,
          foto: data.foto?.file
        }
      });

      // Si hay foto, agregarla también a la cola
      if (data.foto) {
        addToQueue({
          type: 'foto',
          action: 'create',
          itemId: avance.id,
          data: {
            file: data.foto.file,
            path: data.foto.path,
            avanceId: avance.id
          }
        });
      }

      // Recargar avances
      await get().loadAvances();
      
      set({ isLoading: false });
    } catch (error) {
      console.error('Error creando avance:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Error creando avance',
        isLoading: false 
      });
      throw error;
    }
  },

  updateAvance: async (id: string, data: Partial<Avance>) => {
    set({ isLoading: true, error: null });
    
    try {
      await prisma.avance.update({
        where: { id },
        data: {
          ...data,
          updatedAt: new Date(),
          syncStatus: 'local'
        }
      });

      // Agregar a cola de sincronización
      const { addToQueue } = useSyncStore.getState();
      addToQueue({
        type: 'avance',
        action: 'update',
        itemId: id,
        data
      });

      await get().loadAvances();
      set({ isLoading: false });
    } catch (error) {
      console.error('Error actualizando avance:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Error actualizando avance',
        isLoading: false 
      });
      throw error;
    }
  },

  deleteAvance: async (id: string) => {
    set({ isLoading: true, error: null });
    
    try {
      // Soft delete
      await prisma.avance.update({
        where: { id },
        data: {
          deletedAt: new Date(),
          syncStatus: 'local'
        }
      });

      // Agregar a cola de sincronización
      const { addToQueue } = useSyncStore.getState();
      addToQueue({
        type: 'avance',
        action: 'delete',
        itemId: id,
        data: { deletedAt: new Date() }
      });

      await get().loadAvances();
      set({ isLoading: false });
    } catch (error) {
      console.error('Error eliminando avance:', error);
      set({ 
        error: error instanceof Error ? error.message : 'Error eliminando avance',
        isLoading: false 
      });
      throw error;
    }
  },

  exportToExcel: async (avances?: Avance[]) => {
    try {
      const dataToExport = avances || get().avances;
      
      const excelData = dataToExport.map(avance => ({
        'Fecha': avance.fecha.toLocaleDateString('es-CL'),
        'Torre': avance.torre,
        'Piso': avance.piso,
        'Sector': avance.sector || '',
        'Tipo Espacio': avance.tipoEspacio,
        'Ubicación': avance.ubicacion,
        'Categoría': avance.categoria,
        'Porcentaje': avance.porcentaje,
        'Observaciones': avance.observaciones || '',
        'Estado Sync': avance.syncStatus,
        'Creado': avance.createdAt.toLocaleDateString('es-CL')
      }));

      const worksheet = XLSX.utils.json_to_sheet(excelData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Avances');

      // Ajustar ancho de columnas
      const colWidths = [
        { wch: 12 }, // Fecha
        { wch: 8 },  // Torre
        { wch: 8 },  // Piso
        { wch: 12 }, // Sector
        { wch: 15 }, // Tipo Espacio
        { wch: 15 }, // Ubicación
        { wch: 25 }, // Categoría
        { wch: 12 }, // Porcentaje
        { wch: 30 }, // Observaciones
        { wch: 12 }, // Estado Sync
        { wch: 12 }  // Creado
      ];
      worksheet['!cols'] = colWidths;

      const fileName = `avances_los_encinos_${new Date().toISOString().split('T')[0]}.xlsx`;
      XLSX.writeFile(workbook, fileName);
    } catch (error) {
      console.error('Error exportando a Excel:', error);
      throw error;
    }
  },

  clearError: () => set({ error: null })
}));