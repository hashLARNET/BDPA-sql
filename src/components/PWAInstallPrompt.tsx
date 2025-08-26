import React from 'react';
import { Download, X, Smartphone, Monitor } from 'lucide-react';
import { usePWA } from '../hooks/usePWA';

const PWAInstallPrompt: React.FC = () => {
  const { isInstallable, isInstalled, installApp } = usePWA();
  const [showPrompt, setShowPrompt] = React.useState(false);
  const [dismissed, setDismissed] = React.useState(false);

  React.useEffect(() => {
    // Mostrar prompt después de 30 segundos si es instalable y no está instalada
    if (isInstallable && !isInstalled && !dismissed) {
      const timer = setTimeout(() => {
        setShowPrompt(true);
      }, 30000);

      return () => clearTimeout(timer);
    }
  }, [isInstallable, isInstalled, dismissed]);

  const handleInstall = async () => {
    try {
      await installApp();
      setShowPrompt(false);
    } catch (error) {
      console.error('Error installing app:', error);
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    setDismissed(true);
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  // No mostrar si ya está instalada o no es instalable
  if (!isInstallable || isInstalled || !showPrompt) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm z-50">
      <div className="bg-white rounded-lg shadow-xl border border-gray-200 p-4 animate-slide-up">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="bg-primary-100 p-2 rounded-lg">
              <Download className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Instalar BDPA</h3>
              <p className="text-sm text-gray-600">Acceso rápido desde tu escritorio</p>
            </div>
          </div>
          <button
            onClick={handleDismiss}
            className="text-gray-400 hover:text-gray-600 p-1"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="space-y-3">
          <div className="flex items-center space-x-3 text-sm text-gray-600">
            <Monitor className="h-4 w-4" />
            <span>Funciona como una aplicación nativa</span>
          </div>
          <div className="flex items-center space-x-3 text-sm text-gray-600">
            <Smartphone className="h-4 w-4" />
            <span>Disponible sin conexión a internet</span>
          </div>
        </div>

        <div className="flex space-x-2 mt-4">
          <button
            onClick={handleInstall}
            className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            Instalar Ahora
          </button>
          <button
            onClick={handleDismiss}
            className="px-4 py-2 text-gray-600 text-sm font-medium hover:text-gray-800 transition-colors"
          >
            Más tarde
          </button>
        </div>
      </div>
    </div>
  );
};

export default PWAInstallPrompt;