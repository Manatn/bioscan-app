import logging
from google import genai
from google.genai import types
from app.config import settings
from app.schemas import HealthAnalysisResult

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """Вы - опытный фитопатолог и биолог. Ваша задача - проанализировать фотографию растения (листа, стебля, плода, корня) или биологического образца.
Определите, здоровый это объект или больной. Если объект болен, назовите конкретное заболевание или проблему.
Оцените степень тяжести проблемы.
Перечислите визуальные признаки болезни, которые вы видите на фото.
Укажите координаты проблемных зон (визуальных маркеров) в формате [ymin, xmin, ymax, xmax] в масштабе от 0 до 1000 и дайте им описание.
Дайте практические рекомендации по лечению или уходу.
Напишите краткое резюме.

Если на изображении НЕ растение и НЕ биологический образец, верните ответ, в котором:
is_healthy = True
condition_name = "Не является растением"
confidence = 0.0
severity = "Здоров"
visual_signs = []
visual_markers = []
recommendations = []
summary = "Изображение не распознано как растение или биологический образец."
"""

async def analyze_image(image_bytes: bytes, mime_type: str) -> HealthAnalysisResult:
    """Анализирует изображение с помощью Google Gemini."""
    try:
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[SYSTEM_PROMPT, image_part],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=HealthAnalysisResult,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        return response.parsed
    except Exception as e:
        logger.error(f"Ошибка при анализе изображения: {e}")
        raise e
