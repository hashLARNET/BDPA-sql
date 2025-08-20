import { create } from 'zustand';
import { SyncItem } from '../types';

interface SyncState {
  isOnline: boolean;
  isSyncing: boolean;
  lastSync: Date | null;
  queue: SyncItem[];
  errors: string[];
  
  // Actions
  setOnlineStatus: (isOnline: boolean) => void;
  setSyncing: (isSyncing: boolean) => void;
  setLastSync: (date: Date) => void;
  addToQueue: (item: Omit<SyncItem, 'id' | 'attempts' | 'status'>) => void;
  removeFromQueue: (id: string) => void;
  updateQueueItem: (id: string, updates: Partial<SyncItem>) => void;
  clearQueue: () => void;
  addError: (error: string) => void;
  clearErrors: () => void;
  processQueue: () => Promise<void>;
}

export const useSyncStore = create<SyncState>((set, get) => ({
  isOnline: navigator.onLine,
  isSyncing: false,
  lastSync: null,
  queue: [],
  errors: [],

  setOnlineStatus: (isOnline) => set({ isOnline }),

  setSyncing: (isSyncing) => set({ isSyncing }),

  setLastSync: (lastSync) => set({ lastSync }),

  addToQueue: (item) => {
    const newItem: SyncItem = {
      ...item,
      id: crypto.randomUUID(),
      attempts: 0,
      status: 'pending'
    };
    
    set((state) => ({
      queue: [...state.queue, newItem]
    }));
  },

  removeFromQueue: (id) => {
    set((state) => ({
      queue: state.queue.filter(item => item.id !== id)
    }));
  },

  updateQueueItem: (id, updates) => {
    set((state) => ({
      queue: state.queue.map(item => 
        item.id === id ? { ...item, ...updates } : item
      )
    }));
  },

  clearQueue: () => set({ queue: [] }),

  addError: (error) => {
    set((state) => ({
      errors: [...state.errors, error]
    }));
  },

  clearErrors: () => set({ errors: [] }),

  processQueue: async () => {
    const { queue, isOnline, isSyncing } = get();
    
    if (!isOnline || isSyncing || queue.length === 0) {
      return;
    }

    set({ isSyncing: true });

    try {
      const pendingItems = queue.filter(item => item.status === 'pending');
      
      for (const item of pendingItems) {
        try {
          // Actualizar estado a processing
          get().updateQueueItem(item.id, { 
            status: 'processing',
            lastAttempt: new Date()
          });

          // TODO: Implementar lógica de sincronización según el tipo
          await new Promise(resolve => setTimeout(resolve, 1000)); // Simulación

          // Marcar como completado
          get().updateQueueItem(item.id, { status: 'completed' });
          
        } catch (error) {
          const attempts = item.attempts + 1;
          const maxRetries = 3;
          
          if (attempts >= maxRetries) {
            get().updateQueueItem(item.id, { 
              status: 'failed',
              attempts,
              error: error instanceof Error ? error.message : 'Error desconocido'
            });
            get().addError(`Error sincronizando ${item.type}: ${error}`);
          } else {
            get().updateQueueItem(item.id, { 
              status: 'pending',
              attempts,
              error: error instanceof Error ? error.message : 'Error desconocido'
            });
          }
        }
      }

      // Limpiar items completados
      set((state) => ({
        queue: state.queue.filter(item => item.status !== 'completed'),
        lastSync: new Date()
      }));

    } finally {
      set({ isSyncing: false });
    }
  }
}));

// Configurar listeners para detectar cambios de conectividad
window.addEventListener('online', () => {
  useSyncStore.getState().setOnlineStatus(true);
  useSyncStore.getState().processQueue();
});

window.addEventListener('offline', () => {
  useSyncStore.getState().setOnlineStatus(false);
});