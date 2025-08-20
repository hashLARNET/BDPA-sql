// Estructura específica de la obra Los Encinos
import { TORRES_SIN_NORTE } from '../types';

export interface EstructuraUnidades {
  [torre: string]: {
    [piso: number]: {
      [sector: string]: string[];
    };
  };
}

// Configuración específica de Los Encinos
export const ESTRUCTURA_LOS_ENCINOS: EstructuraUnidades = {
  A: {
    1: { Oriente: ['A101', 'A102', 'A103', 'A104', 'A105', 'A106', 'A107', 'A108', 'A109'] },
    3: { Oriente: ['A301', 'A302', 'A303', 'A304', 'A305', 'A306', 'A307', 'A308', 'A309'] }
  },
  B: {
    1: { 
      Poniente: ['B101', 'B102', 'B103', 'B104', 'B105'],
      Norte: ['B106', 'B107', 'B108', 'B109', 'B110'],
      Oriente: ['B111', 'B112', 'B113', 'B114', 'B115']
    },
    3: { 
      Poniente: ['B301', 'B302', 'B303', 'B304', 'B305'],
      Norte: ['B306', 'B307', 'B308', 'B309', 'B310'],
      Oriente: ['B311', 'B312', 'B313', 'B314', 'B315']
    }
  },
  C: {
    1: { 
      Poniente: ['C101', 'C102', 'C103', 'C104', 'C105', 'C106', 'C107'],
      Oriente: ['C108', 'C109', 'C110', 'C111', 'C112', 'C113', 'C114']
    },
    3: { 
      Poniente: ['C301', 'C302', 'C303', 'C304', 'C305', 'C306', 'C307'],
      Oriente: ['C308', 'C309', 'C310', 'C311', 'C312', 'C313', 'C314']
    }
  },
  D: {
    1: { 
      Poniente: ['D101', 'D102', 'D103', 'D104', 'D105'],
      Norte: ['D106', 'D107', 'D108', 'D109', 'D110'],
      Oriente: ['D111', 'D112', 'D113', 'D114', 'D115']
    },
    3: { 
      Poniente: ['D301', 'D302', 'D303', 'D304', 'D305'],
      Norte: ['D306', 'D307', 'D308', 'D309', 'D310'],
      Oriente: ['D311', 'D312', 'D313', 'D314', 'D315']
    }
  },
  E: {
    1: { 
      Poniente: ['E101', 'E102', 'E103', 'E104', 'E105'],
      Norte: ['E106', 'E107', 'E108', 'E109', 'E110'],
      Oriente: ['E111', 'E112', 'E113', 'E114', 'E115']
    },
    3: { 
      Poniente: ['E301', 'E302', 'E303', 'E304', 'E305'],
      Norte: ['E306', 'E307', 'E308', 'E309', 'E310'],
      Oriente: ['E311', 'E312', 'E313', 'E314', 'E315']
    }
  },
  F: {
    1: { 
      Poniente: ['F101', 'F102', 'F103', 'F104', 'F105'],
      Norte: ['F106', 'F107', 'F108', 'F109', 'F110'],
      Oriente: ['F111', 'F112', 'F113', 'F114', 'F115']
    },
    3: { 
      Poniente: ['F301', 'F302', 'F303', 'F304', 'F305'],
      Norte: ['F306', 'F307', 'F308', 'F309', 'F310'],
      Oriente: ['F311', 'F312', 'F313', 'F314', 'F315']
    }
  },
  G: {
    1: { 
      Poniente: ['G101', 'G102', 'G103', 'G104', 'G105'],
      Norte: ['G106', 'G107', 'G108', 'G109', 'G110'],
      Oriente: ['G111', 'G112', 'G113', 'G114', 'G115']
    },
    3: { 
      Poniente: ['G301', 'G302', 'G303', 'G304', 'G305'],
      Norte: ['G306', 'G307', 'G308', 'G309', 'G310'],
      Oriente: ['G311', 'G312', 'G313', 'G314', 'G315']
    }
  },
  H: {
    1: { 
      Poniente: ['H101', 'H102', 'H103', 'H104', 'H105', 'H106', 'H107'],
      Oriente: ['H108', 'H109', 'H110', 'H111', 'H112', 'H113', 'H114']
    },
    3: { 
      Poniente: ['H301', 'H302', 'H303', 'H304', 'H305', 'H306', 'H307'],
      Oriente: ['H308', 'H309', 'H310', 'H311', 'H312', 'H313', 'H314']
    }
  },
  I: {
    1: { 
      Poniente: ['I101', 'I102', 'I103', 'I104', 'I105'],
      Norte: ['I106', 'I107', 'I108', 'I109', 'I110'],
      Oriente: ['I111', 'I112', 'I113', 'I114', 'I115']
    },
    3: { 
      Poniente: ['I301', 'I302', 'I303', 'I304', 'I305'],
      Norte: ['I306', 'I307', 'I308', 'I309', 'I310'],
      Oriente: ['I311', 'I312', 'I313', 'I314', 'I315']
    }
  },
  J: {
    1: { Oriente: ['J101', 'J102', 'J103', 'J104', 'J105', 'J106', 'J107', 'J108', 'J109'] },
    3: { Oriente: ['J301', 'J302', 'J303', 'J304', 'J305', 'J306', 'J307', 'J308', 'J309'] }
  }
};

export function getSectoresDisponibles(torre: string): string[] {
  if (TORRES_SIN_NORTE.includes(torre as any)) {
    return ['Poniente', 'Oriente'];
  }
  return ['Norte', 'Poniente', 'Oriente'];
}

export function getPisosDisponibles(torre: string): number[] {
  return [1, 3];
}

export function getUnidadesDisponibles(torre: string, piso: number, sector: string): string[] {
  return ESTRUCTURA_LOS_ENCINOS[torre]?.[piso]?.[sector] || [];
}

export function getTotalUnidades(): number {
  let total = 0;
  Object.values(ESTRUCTURA_LOS_ENCINOS).forEach(torre => {
    Object.values(torre).forEach(piso => {
      Object.values(piso).forEach(unidades => {
        total += unidades.length;
      });
    });
  });
  return total;
}

export function getUnidadesPorTorre(torre: string): number {
  let total = 0;
  const torreData = ESTRUCTURA_LOS_ENCINOS[torre];
  if (torreData) {
    Object.values(torreData).forEach(piso => {
      Object.values(piso).forEach(unidades => {
        total += unidades.length;
      });
    });
  }
  return total;
}