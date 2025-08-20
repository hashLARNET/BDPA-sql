import { PrismaClient } from '@prisma/client';

// Singleton para la conexión a la base de datos
class DatabaseService {
  private static instance: DatabaseService;
  private prisma: PrismaClient;

  private constructor() {
    this.prisma = new PrismaClient({
      log: ['error', 'warn'],
      errorFormat: 'pretty'
    });
  }

  public static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  public getClient(): PrismaClient {
    return this.prisma;
  }

  public async connect(): Promise<void> {
    try {
      await this.prisma.$connect();
      console.log('✅ Conectado a la base de datos SQLite');
    } catch (error) {
      console.error('❌ Error conectando a la base de datos:', error);
      throw error;
    }
  }

  public async disconnect(): Promise<void> {
    try {
      await this.prisma.$disconnect();
      console.log('✅ Desconectado de la base de datos');
    } catch (error) {
      console.error('❌ Error desconectando de la base de datos:', error);
    }
  }

  // Método para verificar la salud de la base de datos
  public async healthCheck(): Promise<boolean> {
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      return true;
    } catch (error) {
      console.error('❌ Health check falló:', error);
      return false;
    }
  }

  // Método para obtener estadísticas de la base de datos
  public async getStats() {
    try {
      const [usuarios, avances, mediciones, syncQueue] = await Promise.all([
        this.prisma.usuario.count(),
        this.prisma.avance.count(),
        this.prisma.medicion.count(),
        this.prisma.syncQueue.count({ where: { status: 'pending' } })
      ]);

      return {
        usuarios,
        avances,
        mediciones,
        pendingSyncs: syncQueue
      };
    } catch (error) {
      console.error('❌ Error obteniendo estadísticas:', error);
      return null;
    }
  }
}

export const db = DatabaseService.getInstance();
export const prisma = db.getClient();