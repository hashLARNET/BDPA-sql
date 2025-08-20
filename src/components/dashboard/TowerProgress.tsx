import React from 'react';
import { TORRES } from '../../utils/estructura-obra';

const TowerProgress: React.FC = () => {
  // TODO: Obtener datos reales de progreso por torre
  const towerData = TORRES.map(torre => ({
    torre,
    progreso: Math.floor(Math.random() * 100), // Datos simulados
    unidades: Math.floor(Math.random() * 50) + 10
  }));

  return (
    <div className="space-y-3">
      {towerData.map(({ torre, progreso, unidades }) => (
        <div key={torre} className="flex items-center space-x-4">
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-sm font-semibold text-primary-700">
              {torre}
            </span>
          </div>
          
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-900">
                Torre {torre}
              </span>
              <span className="text-sm text-gray-600">
                {progreso}%
              </span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${progreso}%` }}
              />
            </div>
            
            <div className="flex items-center justify-between mt-1">
              <span className="text-xs text-gray-500">
                {unidades} unidades
              </span>
              <span className="text-xs text-gray-500">
                {Math.floor((progreso / 100) * unidades)} completadas
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TowerProgress;