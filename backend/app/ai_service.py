import logging
from google import genai
from google.genai import types
from app.config import settings
from app.schemas import HealthAnalysisResult

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """Сіз - тәжірибелі фитопатолог және биологсыз. Сіздің міндетіңіз - өсімдік (жапырақ, сабақ, жеміс, тамыр) немесе биологиялық үлгі суретін талдау.

Бұл нысанның сау немесе ауру екенін анықтаңыз. Егер нысан ауру болса, нақты ауруды немесе мәселені атаңыз.
Мәселенің ауырлық деңгейін бағалаңыз.
Суретте көрінетін аурудың визуалды белгілерін атап өтіңіз.

ВИЗУАЛДЫ МАРКЕРЛЕРГЕ СИПАТТАМА БЕРУ ШАРТТАРЫ (ӨТЕ МҮҚИЯТ ОРЫНДАҢЫЗ):
Проблемалық аймақтардың (визуалды маркерлердің) координаталарын 0-ден 1000-ға дейінгі масштабта [ymin, xmin, ymax, xmax] форматында көрсетіңіз.
ӘР БІР маркерге (label / description) ТЕК ЖАЛПЫ СӨЗДЕРДІ ("Дөңгелек дақ", "Дақ") ҚАЙТАЛАМАЙ, нақты визуалды ерекшелігін сипаттаңыз:
- Мысалы: "ортасы ақшыл-сұр дақ", "қызыл-қоңыр жиекті зақым", "жапырақ жиегінің шіруі", "ірі концентрический ошақ", "ұсақ некротикалық нүкте".
- Түрлі маркерлерге ТҮРЛІ нақты сипаттама беріңіз!

Емдеу немесе күтім жасау бойынша практикалық ұсыныстар беріңіз.
Қысқаша түйіндеме жазыңыз.

Егер суретте өсімдік ЕМЕС және биологиялық үлгі ЕМЕС болса, келесідей жауап қайтарыңыз:
is_healthy = True
condition_name = "Өсімдік емес"
confidence = 0.0
severity = "Сау"
visual_signs = []
visual_markers = []
recommendations = []
summary = "Сурет өсімдік немесе биологиялық үлгі ретінде танылмады."
"""

async def analyze_image(image_bytes: bytes, mime_type: str) -> HealthAnalysisResult:
    """Суретті Google Gemini көмегімен талдайды."""
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
        logger.error(f"Суретті талдау кезінде қате орын алды: {e}")
        raise e
