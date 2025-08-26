import React from 'react';
import { RefreshCw, X } from 'lucide-react';
import { usePWA } from '../hooks/usePWA';

const PWAUpdatePrompt: React.FC = () => {
  const { updateAvailable, updateApp } = usePWA();
  const [showPrompt, setShowPrompt] = React.useState(false);

  React.useEffect(() => {
    if (updateAvailable) {
      setShowPrompt(true);
    }
  }, [updateAvailable]);

  const handleUpdate = () => {
    updateApp();
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
  };

  if (!showPrompt || !updateAvailable) {
    return null;
  }

  return (
    <div className="fixed top-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm z-50">
      <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 animate-slide-up">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="bg-primary-100 p-2 rounded-lg">
              <RefreshCw className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <h3 className="font-semibold text-primary-900">Actualización Disponible</h3>
              <p className="text-sm text-primary-700">Nueva versión de BDPA lista</p>
            </div>
          </div>
          <button
            onClick={handleDismiss}
            className="text-primary-400 hover:text-primary-600 p-1"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <p className="text-sm text-primary-700 mb-4">
          Hay mejoras y correcciones disponibles. Actualiza para obtener la mejor experiencia.
        </p>

        <div className="flex space-x-2">
          <button
            onClick={handleUpdate}
            className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            Actualizar Ahora
          </button>
          <button
            onClick={handleDismiss}
            className="px-4 py-2 text-primary-600 text-sm font-medium hover:text-primary-800 transition-colors"
          >
            Más tarde
          </button>
        </div>
      </div>
    </div>
  );
};

export default PWAUpdatePrompt;