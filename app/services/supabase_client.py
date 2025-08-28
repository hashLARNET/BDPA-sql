from supabase import create_client, Client
from app.config import settings

# Cliente global de Supabase
supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)

# Cliente con privilegios de servicio (para operaciones administrativas)
supabase_service: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)