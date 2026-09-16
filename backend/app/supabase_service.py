import logging
from uuid import uuid4
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

try:
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception as e:
    logger.warning(f"Ошибка инициализации клиента Supabase: {e}")
    supabase = None

def upload_image(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Загружает изображение в бакет Supabase и возвращает публичный URL."""
    if not supabase:
        raise Exception("Supabase клиент не инициализирован")
    try:
        file_path = f"{uuid4()}/{filename}"
        supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        public_url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)
        return public_url
    except Exception as e:
        logger.error(f"Ошибка при загрузке изображения в Supabase: {e}")
        raise e

def save_analysis(result: dict, image_url: str, image_path: str) -> str:
    """Сохраняет результаты анализа в БД Supabase."""
    if not supabase:
        raise Exception("Supabase клиент не инициализирован")
    try:
        record = result.copy()
        record["image_url"] = image_url
        record["image_path"] = image_path
        
        response = supabase.table("analysis_history").insert(record).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
        return ""
    except Exception as e:
        logger.error(f"Ошибка при сохранении результатов анализа: {e}")
        raise e

def get_history(limit: int = 20) -> list[dict]:
    """Возвращает историю анализов."""
    if not supabase:
        logger.warning("Supabase клиент не инициализирован, история недоступна")
        return []
    try:
        response = supabase.table("analysis_history").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        raise e
