import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Usuario } from '../types';

interface AuthState {
  user: Usuario | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setUser: (user: Usuario | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user,
        error: null 
      }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      clearError: () => set({ error: null }),

      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          // TODO: Implementar lógica de autenticación
          // 1. Intentar login con Supabase
          // 2. Si falla, verificar credenciales locales
          // 3. Crear sesión y guardar usuario
          
          // Simulación temporal
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          const mockUser: Usuario = {
            id: '1',
            username,
            nombre: 'Usuario Demo',
            rol: 'Tecnico',
            activo: true,
            createdAt: new Date(),
            updatedAt: new Date()
          };

          set({ 
            user: mockUser, 
            isAuthenticated: true, 
            isLoading: false 
          });
          
          return true;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Error de autenticación',
            isLoading: false 
          });
          return false;
        }
      },

      logout: () => {
        set({ 
          user: null, 
          isAuthenticated: false, 
          error: null 
        });
      }
    }),
    {
      name: 'bdpa-auth',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      })
    }
  )
);