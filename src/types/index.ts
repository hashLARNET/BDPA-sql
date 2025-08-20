// Tipos principales del sistema BDPA
export interface Usuario {
  id: string;
  username: string;
  email?: string;
  nombre: string;
  rol: 'Admin' | 'Supervisor' | 'Tecnico' | 'Ayudante';
  activo: boolean;
  ultimoAcceso?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface Avance {
  id: string;
  obraId: string;
  fecha: Date;
  torre: string; // A, B, C, D, E, F, G, H, I, J
  piso?: number; // 1, 3
  sector?: 'Norte' | 'Poniente' | 'Oriente';
  tipoEspacio: 'unidad' | 'sotu' | 'shaft' | 'lateral' | 'antena';
  ubicacion: string; // Identificador específico (ej: "A101", "SOTU-A1")
  categoria: CategoriaAvance;
  porcentaje: number; // 0-100
  fotoPath?: string; // Ruta local de la foto
  fotoUrl?: string; // URL en Supabase Storage
  observaciones?: string;
  usuarioId: string;
  syncStatus: 'local' | 'syncing' | 'synced' | 'conflict';
  lastSync?: Date;
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date;
}

export type CategoriaAvance = 
  // Para unidades
  | 'Cableado alámbrico T1'
  | 'Cableado inalámbrico T1/T2'
  | 'Instalación PAU'
  | 'Conexión PAU'
  | 'Fibra Óptica'
  // Para SOTU
  | 'Instalación de dispositivos'
  | 'Conexiones de entrada'
  | 'Conexiones de salida'
  | 'Configuración'
  | 'Certificación'
  // Para Shaft
  | 'Tendido de troncales'
  | 'Instalación de derivadores'
  | 'Conexiones a SOTU'
  | 'Sellado y seguridad'
  // Para Lateral
  | 'Tendido coaxial PAU-SOTU'
  | 'Tendido F.O. PAU-SOTU'
  | 'Protección y acabados'
  // Para Antena
  | 'Instalación física'
  | 'Orientación y ajuste'
  | 'Cableado de bajada'
  | 'Pruebas de señal';

export interface Medicion {
  id: string;
  obraId: string;
  fecha: Date;
  torre: string;
  piso: number;
  identificador: string; // Unidad específica
  tipoMedicion: TipoMedicion;
  valores: ValoresMedicion;
  estado: 'OK' | 'ADVERTENCIA' | 'FALLA';
  usuarioId: string;
  observaciones?: string;
  syncStatus: 'local' | 'synced';
  createdAt: Date;
  updatedAt: Date;
}

export type TipoMedicion = 
  | 'alambrico-t1'
  | 'alambrico-t2'
  | 'coaxial'
  | 'fibra'
  | 'wifi'
  | 'certificacion';

export interface ValoresMedicion {
  alambricoT1?: number; // dBμV
  alambricoT2?: number; // dBμV
  coaxial?: number; // dBμV
  potenciaTx?: number; // dBm
  potenciaRx?: number; // dBm
  atenuacion?: number; // dB
  wifi?: number; // dBm
  certificacion?: 'APROBADO' | 'APROBADO_CON_OBSERVACIONES' | 'RECHAZADO';
}

export interface DashboardData {
  resumenGeneral: {
    totalUnidades: number;
    unidadesCompletadas: number;
    porcentajeGeneral: number;
    diasRestantes: number;
  };
  progresoTorres: Map<string, number>; // Torre -> Porcentaje
  ultimosAvances: Avance[];
  alertas: Alerta[];
}

export interface Alerta {
  id: string;
  tipo: 'error' | 'warning' | 'info';
  titulo: string;
  mensaje: string;
  fecha: Date;
  leida: boolean;
}

export interface SyncItem {
  id: string;
  type: 'avance' | 'medicion' | 'foto';
  action: 'create' | 'update' | 'delete';
  itemId: string;
  data: any;
  attempts: number;
  lastAttempt?: Date;
  error?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface AppConfig {
  id: string;
  lastSync?: Date;
  isOnline: boolean;
  settings: {
    syncInterval: number;
    autoSync: boolean;
    compressionLevel: number;
    maxRetries: number;
  };
}

// Constantes de la obra Los Encinos
export const TORRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'] as const;
export const PISOS = [1, 3] as const;
export const SECTORES = ['Norte', 'Poniente', 'Oriente'] as const;

// Torres sin sector Norte
export const TORRES_SIN_NORTE = ['C', 'H'] as const;

export const RANGOS_MEDICION = {
  ALAMBRICO: { min: 45, max: 75, unidad: 'dBμV' },
  COAXIAL: { min: 45, max: 75, unidad: 'dBμV' },
  FIBRA_POTENCIA: { min: -30, max: -8, unidad: 'dBm' },
  FIBRA_ATENUACION: { max: 0.5, unidad: 'dB/km' },
  WIFI: { min: -80, max: -30, unidad: 'dBm' }
} as const;