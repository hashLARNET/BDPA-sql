// Estructura de las torres y configuración del proyecto Los Encinos

export const TORRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] as const;
export const PISOS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] as const;

export type Torre = typeof TORRES[number];
export type Piso = typeof PISOS[number];

// Configuración de sectores por torre
const SECTORES_POR_TORRE: Record<Torre, string[]> = {
  'A': ['Norte', 'Poniente', 'Oriente'],
  'B': ['Norte', 'Poniente', 'Oriente'],
  'C': ['Poniente', 'Oriente'], // Torre C no tiene sector Norte
  'D': ['Norte', 'Poniente', 'Oriente'],
  'E': ['Norte', 'Poniente', 'Oriente'],
  'F': ['Norte', 'Poniente', 'Oriente'],
  'G': ['Norte', 'Poniente', 'Oriente'],
  'H': ['Poniente', 'Oriente'] // Torre H no tiene sector Norte
};

// Configuración de unidades por sector
const UNIDADES_POR_SECTOR = {
  'Norte': ['01', '02', '03', '04', '05', '06'],
  'Poniente': ['07', '08', '09', '10', '11', '12'],
  'Oriente': ['13', '14', '15', '16', '17', '18']
};

/**
 * Obtiene los sectores disponibles para una torre específica
 */
export function getSectoresDisponibles(torre: Torre): string[] {
  return SECTORES_POR_TORRE[torre] || [];
}

/**
 * Obtiene las unidades disponibles para una torre, piso y sector específicos
 */
export function getUnidadesDisponibles(torre: Torre, piso: Piso, sector: string): string[] {
  if (!SECTORES_POR_TORRE[torre]?.includes(sector)) {
    return [];
  }
  
  const unidades = UNIDADES_POR_SECTOR[sector as keyof typeof UNIDADES_POR_SECTOR] || [];
  return unidades.map(unidad => `${torre}${piso.toString().padStart(2, '0')}${unidad}`);
}

/**
 * Valida si una ubicación es válida según la estructura del proyecto
 */
export function validarUbicacion(torre: Torre, piso: Piso, sector: string, unidad: string): boolean {
  const sectoresDisponibles = getSectoresDisponibles(torre);
  if (!sectoresDisponibles.includes(sector)) {
    return false;
  }
  
  const unidadesDisponibles = getUnidadesDisponibles(torre, piso, sector);
  return unidadesDisponibles.includes(unidad);
}

/**
 * Genera el identificador completo de una unidad
 */
export function generarIdentificadorUnidad(torre: Torre, piso: Piso, numeroUnidad: string): string {
  return `${torre}${piso.toString().padStart(2, '0')}${numeroUnidad}`;
}

/**
 * Parsea un identificador de unidad y extrae sus componentes
 */
export function parsearIdentificadorUnidad(identificador: string): {
  torre: Torre;
  piso: Piso;
  numeroUnidad: string;
} | null {
  const match = identificador.match(/^([A-H])(\d{2})(\d{2})$/);
  if (!match) return null;
  
  const [, torre, pisoStr, numeroUnidad] = match;
  const piso = parseInt(pisoStr, 10);
  
  if (!TORRES.includes(torre as Torre) || !PISOS.includes(piso as Piso)) {
    return null;
  }
  
  return {
    torre: torre as Torre,
    piso: piso as Piso,
    numeroUnidad
  };
}