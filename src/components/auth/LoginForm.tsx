import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Eye, EyeOff, Wifi, WifiOff, Building2 } from 'lucide-react';
import { useAuthStore } from '../../store/auth.store';
import { useSyncStore } from '../../store/sync.store';

interface LoginFormData {
  username: string;
  password: string;
}

const LoginForm: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const { login, isLoading, error, clearError } = useAuthStore();
  const { isOnline } = useSyncStore();
  
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    clearError();
    await login(data.username, data.password);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center mb-4">
            <Building2 className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900">BDPA</h2>
          <p className="mt-2 text-sm text-gray-600">
            Sistema de Gestión de Obras de Telecomunicaciones
          </p>
          <p className="text-sm font-medium text-primary-600">
            Los Encinos
          </p>
        </div>

        {/* Connection Status */}
        <div className={`
          flex items-center justify-center space-x-2 px-4 py-2 rounded-lg
          ${isOnline 
            ? 'bg-success-50 text-success-700' 
            : 'bg-warning-50 text-warning-700'
          }
        `}>
          {isOnline ? (
            <Wifi className="h-4 w-4" />
          ) : (
            <WifiOff className="h-4 w-4" />
          )}
          <span className="text-sm font-medium">
            {isOnline ? 'Conectado - Sincronización automática' : 'Sin conexión - Modo offline'}
          </span>
        </div>

        {/* Login Form */}
        <div className="bg-white py-8 px-6 shadow-xl rounded-xl">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Usuario
              </label>
              <div className="mt-1">
                <input
                  {...register('username', { 
                    required: 'El usuario es requerido',
                    minLength: { value: 3, message: 'Mínimo 3 caracteres' }
                  })}
                  type="text"
                  autoComplete="username"
                  className={`
                    appearance-none block w-full px-3 py-2 border rounded-md shadow-sm 
                    placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500
                    ${errors.username ? 'border-error-300' : 'border-gray-300'}
                  `}
                  placeholder="Ingresa tu usuario"
                />
                {errors.username && (
                  <p className="mt-1 text-sm text-error-600">{errors.username.message}</p>
                )}
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Contraseña
              </label>
              <div className="mt-1 relative">
                <input
                  {...register('password', { 
                    required: 'La contraseña es requerida',
                    minLength: { value: 6, message: 'Mínimo 6 caracteres' }
                  })}
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  className={`
                    appearance-none block w-full px-3 py-2 pr-10 border rounded-md shadow-sm 
                    placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500
                    ${errors.password ? 'border-error-300' : 'border-gray-300'}
                  `}
                  placeholder="Ingresa tu contraseña"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-error-600">{errors.password.message}</p>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-error-50 border border-error-200 rounded-md p-3">
                <p className="text-sm text-error-600">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className={`
                  group relative w-full flex justify-center py-2 px-4 border border-transparent 
                  text-sm font-medium rounded-md text-white transition-colors
                  ${isLoading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
                  }
                `}
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin h-4 w-4 border border-white border-t-transparent rounded-full" />
                    <span>Iniciando sesión...</span>
                  </div>
                ) : (
                  'Iniciar Sesión'
                )}
              </button>
            </div>
          </form>

          {/* Offline Notice */}
          {!isOnline && (
            <div className="mt-4 p-3 bg-warning-50 border border-warning-200 rounded-md">
              <p className="text-xs text-warning-700 text-center">
                Modo offline activo. Los datos se sincronizarán cuando se restablezca la conexión.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            © 2024 BDPA - Sistema de Gestión de Obras
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;