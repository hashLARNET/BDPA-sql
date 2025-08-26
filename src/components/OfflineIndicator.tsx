import React from 'react';
import { WifiOff, Wifi } from 'lucide-react';
import { usePWA } from '../hooks/usePWA';

const OfflineIndicator: React.FC = () => {
  const { isOnline } = usePWA();
  const [showOfflineMessage, setShowOfflineMessage] = React.useState(false);
  const [wasOffline, setWasOffline] = React.useState(false);

  React.useEffect(() => {
    if (!isOnline) {
      setShowOfflineMessage(true);
      setWasOffline(true);
    } else if (wasOffline) {
      // Mostrar mensaje de reconexión brevemente
      setShowOfflineMessage(true);
      const timer = setTimeout(() => {
        setShowOfflineMessage(false);
        setWasOffline(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isOnline, wasOffline]);

  if (!showOfflineMessage) {
    return null;
  }

  return (
    <div className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 animate-slide-up`}>
      <div className={`
        flex items-center space-x-2 px-4 py-2 rounded-lg shadow-lg text-sm font-medium
        ${isOnline 
          ? 'bg-success-100 text-success-800 border border-success-200' 
          : 'bg-warning-100 text-warning-800 border border-warning-200'
        }
      `}>
        {isOnline ? (
          <>
            <Wifi className="h-4 w-4" />
            <span>Conexión restablecida</span>
          </>
        ) : (
          <>
            <WifiOff className="h-4 w-4" />
            <span>Sin conexión - Modo offline activo</span>
          </>
        )}
      </div>
    </div>
  );
};

export default OfflineIndicator;