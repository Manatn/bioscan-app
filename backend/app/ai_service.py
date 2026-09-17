import asyncio
import logging
import random
import re

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.config import settings
from app.schemas import HealthAnalysisResult

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """Сіз — халықаралық деңгейдегі жоғары білікті фитопатолог, ботаник және агрономсыз.
Сіздің басты міндетіңіз — өсімдіктердің (жапырақ, сабақ, тамыр, жеміс) ауруларын асқан дәлдікпен
визуалды диагностикалау және нәтижені қатаң түрде ҚАЗАҚ ТІЛІНДЕ, академиялық стильде, толық
сөйлемдермен қайтару.

=====================================================
1-БӨЛІМ. ТІЛ МЕН ТЕРМИНОЛОГИЯ (ЕҢ МАҢЫЗДЫСЫ)
=====================================================

1.1. Барлық мәтін (condition_name, visual_signs, recommendations, summary) — таза, грамматикалық
     тұрғыдан дұрыс, толық құрылымды ҚАЗАҚ ТІЛІНДЕ жазылады. Бір сөйлем ішінде қазақ және ағылшын
     сөздерін араластыруға (мыс.: "Cercospora ауруы бар дақтар") ТЫЙЫМ САЛЫНАДЫ.

1.2. Латын тілі ТЕК қоздырғыштың ғылыми биномиалды атауы үшін қолданылады (мыс.: "Cercospora
     beticola қоздырған"), және ол әрқашан қазақша сөйлемнің ІШІНДЕ, қосымша ретінде беріледі —
     бүкіл ауру атауының орнына емес. Ағылшын тілінде термин қалдыруға МҮЛДЕМ ТЫЙЫМ САЛЫНАДЫ.

1.3. Ауру атауының (condition_name) форматы қатаң түрде: "Өсімдік атауы + Ауру атауы"
     (мыс.: "Қызылша церкоспорозы", "Алма паршасы").

1.4. Егер дәл қазақша ғылыми термин табылмаса — ойдан жаңа сөз құрастырмаңыз (мыс., "ботритация"
     деген жоқ сөз жасамаңыз) және ағылшыншаны сол күйі де қалдырмаңыз. Оның орнына сипаттамалық
     қазақша баламаны қолданыңыз: аурудың тобын/сипатын атаңыз (мыс.: "жапырақ дағы ауруы",
     "тамыр шірігі", "ұнтақты форма ауруы") + жақшада қоздырғыштың латынша атауы.

1.5. Инфекциялық емес себептер (күнге күю, ылғал жетіспеушілігі, механикалық зақым, қоректік
     заттар тапшылығы) үшін ағылшын сөзіне қазақша жалғау жалғауға (мыс., "сунбюрні") ҚАТАҢ
     ТЫЙЫМ САЛЫНАДЫ. Тек дайын қазақша баламалар қолданылады:
       - Sunburn → "Күнге күю"
       - Overwatering → "Артық суару салдары"
       - Underwatering / drought stress → "Ылғал жетіспеушілігі"
       - Nutrient deficiency → "Қоректік заттар тапшылығы"
     Бұл жағдайларда condition_name өрісінде "Экологиялық стресс" немесе "Физикалық зақым" деген
     жалпы санатты нақтылаңыз (мыс.: "Хойяның күнге күюі").

     ❌ ҚАТЕ мысал: "Свекла ботқасы" (сөзбе-сөз, мағынасыз аударма)
     ✅ ДҰРЫС мысал: "Қызылша церкоспорозы"

=====================================================
2-БӨЛІМ. ВИЗУАЛДЫ МАРКЕРЛЕР (BOUNDING BOXES)
=====================================================

2.1. Координаталар [ymin, xmin, ymax, xmax] форматында, 0–1000 масштабында беріледі.

2.2. Әрбір маркердің сипаттамасы (label) БІРЕГЕЙ (UNIQUE) болуы ШАРТ. Бір сарынды жалпы
     сөздерді ("Қоңыр дақ", "Дөңгелек дақ") барлық маркерге қайталауға ТЫЙЫМ САЛЫНАДЫ.

2.3. Әр сипаттамада міндетті түрде көрсетіледі: дақтың ӨЛШЕМІ, ТҮСІ, ПІШІНІ немесе ЖАПЫРАҚТАҒЫ
     ОРНАЛАСУ АЙМАҒЫ. Кемінде екі белгі бір сипаттамада болуы керек.

     Дұрыс мысалдар:
       - "Жапырақ ұшындағы ірі қара қоңыр некроз"
       - "Ортасы ақшыл, шеті қызыл кішкентай дақ"
       - "Жапырақ жиегіндегі кеуіп кеткен аймақ"
       - "Сары жиекті (хлороз) орташа дақ"
       - "Жапырақ ортасындағы ұсақ тесікті зақым"

=====================================================
3-БӨЛІМ. ТАЛДАУ ҚҰРЫЛЫМЫ
=====================================================

3.1. severity — тек мына мәндердің бірі: "Төмен", "Орташа", "Жоғары", "Өте ауыр".

3.2. visual_signs — симптомдарды ғылыми тілде, нақты әрі толық сөйлеммен тізіп жазыңыз.

3.3. recommendations — агротехникалық, биологиялық немесе химиялық күрес шараларын нақты
     кезеңдермен, практикалық тұрғыда жазыңыз (мыс.: "1-кезең: зақымдалған жапырақтарды жойыңыз...").

3.4. summary — 1–3 сөйлемнен тұратын қорытынды, толық грамматикалық құрылыммен.

=====================================================
4-БӨЛІМ. ЭТАЛОН ПРИМЕРЛЕР (FEW-SHOT)
=====================================================

Мысал А — инфекциялық ауру:
{
  "is_healthy": false,
  "condition_name": "Қызылша церкоспорозы",
  "confidence": 0.92,
  "severity": "Орташа",
  "visual_signs": [
    "Жапырақ бетінде ортасы сұр-ақшыл, жиегі қызыл-қоңыр дөңгелек дақтар байқалады",
    "Дақтардың саны жапырақтың төменгі бөлігінде көбірек шоғырланған"
  ],
  "visual_markers": [
    {"box": [120, 340, 210, 430], "label": "Ортасы ақшыл, қызыл жиекті орташа дақ"},
    {"box": [500, 100, 580, 190], "label": "Жапырақ жиегіндегі бірігіп кеткен ірі дақ"}
  ],
  "recommendations": [
    "1-кезең: ауру таралған жапырақтарды дереу жинап, өртеп жойыңыз",
    "2-кезең: мыс құрамды фунгицидпен (Cercospora beticola қоздырғышына қарсы) 10-14 күн аралықпен өңдеу жүргізіңіз",
    "3-кезең: егіс алмасу схемасын сақтап, қызылшаны бір алаңға 3 жылдан ерте қайта екпеңіз"
  ],
  "summary": "Жапырақта Cercospora beticola қоздырған церкоспороз белгілері анықталды, ауру орташа деңгейде таралған."
}

Мысал Б — инфекциялық емес себеп:
{
  "is_healthy": false,
  "condition_name": "Хойяның күнге күюі",
  "confidence": 0.88,
  "severity": "Төмен",
  "visual_signs": [
    "Жапырақтың күнге тура қараған бетінде ағарған, қуарған дақтар пайда болған",
    "Дақтардың пішіні тұрақсыз, жиектері анық шектелмеген"
  ],
  "visual_markers": [
    {"box": [80, 200, 160, 300], "label": "Жапырақ ортасындағы ағарған күйік дағы"}
  ],
  "recommendations": [
    "1-кезең: өсімдікті тікелей түскен күн сәулесінен қорғап, жарық-көлеңке аймаққа көшіріңіз",
    "2-кезең: зақымдалған жапырақтарды кесіп алмай, өсімдіктің қалпына келуін бақылаңыз"
  ],
  "summary": "Анықталған белгілер инфекциялық емес, тікелей күн сәулесінен болған физикалық зақымға тән."
}

Мысал В — өсімдік жоқ сурет:
{
  "is_healthy": true,
  "condition_name": "Өсімдік емес",
  "confidence": 0.0,
  "severity": "Сау",
  "visual_signs": [],
  "visual_markers": [],
  "recommendations": [],
  "summary": "Сурет өсімдік немесе биологиялық үлгі ретінде танылмады."
}

=====================================================
5-БӨЛІМ. ЕГЕР СУРЕТТЕ ӨСІМДІК НЕМЕСЕ БИОЛОГИЯЛЫҚ ҮЛГІ БОЛМАСА
=====================================================

Дәл осы мәндерді қайтарыңыз: is_healthy=True, condition_name="Өсімдік емес", confidence=0.0,
severity="Сау", visual_signs=[], visual_markers=[], recommendations=[],
summary="Сурет өсімдік немесе биологиялық үлгі ретінде танылмады."
"""

# Бір рет қана қайта сұрау жіберу үшін қосымша нұсқау (тіл ережесі бұзылған кезде).
CORRECTION_INSTRUCTION_TEMPLATE = """Сіздің алдыңғы жауабыңызда тіл ережесі бұзылған сөздер табылды:
{flagged}

Бұл — ағылшын мен қазақ тілін бір сөз/сөйлем ішінде араластыру (мыс., ағылшын сөзіне қазақша
жалғау жалғау) немесе бүкіл терминді ағылшынша қалдыру. 1.1–1.5 ережелерін қатаң сақтап, ТЕК
осы бұзылған өрістерді қазақша дұрыс нұсқаға түзетіп, толық JSON жауапты қайта беріңіз."""


# ---------------------------------------------------------------------------
# Тіл валидациясы: биология/лингвистика білімін талап етпейді, тек script-
# (кирилл/латын) деңгейінде тексереді. Бұл дәлдікке 100% кепілдік бермейді,
# бірақ ең сорақы калькаларды (мыс., "sunburn"+"і") және ағылшынша қалып
# кеткен сөздерді автоматты түрде ұстайды.
# ---------------------------------------------------------------------------

_CYRILLIC = "а-яәғқңөұүһі"
_LATIN = "a-zA-Z"

# Кирилл мен латынды бір сөз ішінде араластыратын токендер (мыс. "сунбюрні").
_MIXED_SCRIPT_RE = re.compile(
    rf"\b(?=[{_CYRILLIC}{_LATIN}]*[{_CYRILLIC}])(?=[{_CYRILLIC}{_LATIN}]*[{_LATIN}])[{_CYRILLIC}{_LATIN}]+\b",
    re.IGNORECASE,
)

# Толық латынша сөз (ағылшын термині болуы мүмкін). Ғылыми биномиалды атау
# (мыс. "Cercospora beticola") — Бас әріппен басталатын, кемінде екі сөзден
# тұратын тіркес түрінде келеді деп есептеп, оны бөлек ескереміз.
_LATIN_WORD_RE = re.compile(r"\b[A-Za-z]+\b")
_BINOMIAL_RE = re.compile(r"\b[A-Z][a-z]+ [a-z]+\b")


def _find_language_issues(result: HealthAnalysisResult) -> list[str]:
    """Модель жауабындағы мәтін өрістерінен тіл ережесін бұзатын сөздерді іздейді.

    Бұл дәлме-дәл лингвистикалық талдау емес, script-деңгейіндегі эвристика:
    - кирилл+латын аралас сөздер (мыс. "сунбюрні") әрдайым флагталады
    - жалғыз тұрған латынша сөздер флагталады, БІРАҚ егер олар ғылыми
      биномиалды атаудың (Genus species) бөлігі болса — рұқсат етіледі
    """
    texts: list[str] = []
    if result.condition_name:
        texts.append(result.condition_name)
    if getattr(result, "summary", None):
        texts.append(result.summary)
    texts.extend(getattr(result, "visual_signs", None) or [])
    texts.extend(getattr(result, "recommendations", None) or [])
    for marker in getattr(result, "visual_markers", None) or []:
        label = getattr(marker, "label", None) if not isinstance(marker, dict) else marker.get("label")
        if label:
            texts.append(label)

    flagged: set[str] = set()

    for text in texts:
        # Ғылыми биномиалды атаулар үшін орындарын уақытша "бос" етіп аламыз,
        # содан кейін қалған латынша сөздерді тексереміз.
        text_without_binomials = _BINOMIAL_RE.sub("", text)

        for match in _MIXED_SCRIPT_RE.finditer(text):
            token = match.group(0)
            has_cyr = re.search(f"[{_CYRILLIC}]", token, re.IGNORECASE)
            has_lat = re.search(f"[{_LATIN}]", token)
            if has_cyr and has_lat:
                flagged.add(token)

        for match in _LATIN_WORD_RE.finditer(text_without_binomials):
            word = match.group(0)
            if len(word) > 2:  # қысқа аббревиатураларды (мыс. "pH") елемейміз
                flagged.add(word)

    return sorted(flagged)


# 503 (моделге сұраныс тым көп) және 429 (rate limit) — уақытша қателер,
# қайталап көру арқылы шешіледі. Басқа қателер (400, 401, 404 т.б.) —
# сұраудың өзінде мәселе бар дегенді білдіреді, оларды қайталаудың мәні жоқ.
_RETRYABLE_STATUS_CODES = {429, 503}
_MAX_RETRIES = 3
_BASE_DELAY_SECONDS = 1.5


async def _call_gemini(contents: list) -> HealthAnalysisResult | None:
    last_error: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=HealthAnalysisResult,
                    # Аз да болса thinking budget: қатаң тілдік ережелер + құрылымды
                    # JSON бір мезгілде сақталуы моделге "ойлануға" орын қалдырғанда
                    # жақсарады.
                    thinking_config=types.ThinkingConfig(thinking_budget=256),
                ),
            )
            return response.parsed

        except genai_errors.APIError as e:
            status_code = getattr(e, "code", None)
            last_error = e

            if status_code not in _RETRYABLE_STATUS_CODES or attempt == _MAX_RETRIES:
                raise

            # Экспоненциалды backoff + jitter: барлық параллель сұраныстар бір
            # мезгілде қайталанып, Google жағын тағы да "ұрып" кетпеу үшін.
            delay = _BASE_DELAY_SECONDS * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            logger.warning(
                "Gemini %s қайтарды (әрекет %d/%d), %.1f секундтан кейін қайталанады: %s",
                status_code, attempt, _MAX_RETRIES, delay, e,
            )
            await asyncio.sleep(delay)

    # Бұл жерге теория жүзінде жетпеу керек, бірақ типтеуші үшін:
    if last_error:
        raise last_error
    return None


async def analyze_image(image_bytes: bytes, mime_type: str) -> HealthAnalysisResult:
    """Суретті Google Gemini көмегімен талдайды.

    Ағын:
      1. Негізгі сұрау (system prompt + сурет)
      2. Нәтижеге script-деңгейіндегі тіл валидациясы жүргізіледі
      3. Егер бұзушылық табылса — БІР РЕТ қана түзету сұрауы жіберіледі
      4. Екінші әрекеттен кейін де мәселе қалса — жауап сол күйі қайтарылады,
         бірақ WARNING деңгейінде логталады (кейін review үшін)
    """
    try:
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        parsed = await _call_gemini([image_part])
        if parsed is None:
            logger.error("Gemini жауабы схемаға сай келмеді (1-әрекет).")
            raise ValueError("Модель жауабы күтілетін схемаға сәйкес келмеді")

        issues = _find_language_issues(parsed)
        if issues:
            logger.warning("Тіл ережесі бұзылған сөздер табылды, түзету сұралады: %s", issues)

            correction_prompt = CORRECTION_INSTRUCTION_TEMPLATE.format(
                flagged=", ".join(issues)
            )
            retried = await _call_gemini(
                [
                    image_part,
                    types.Part.from_text(text=f"Алдыңғы JSON жауап: {parsed.model_dump_json()}"),
                    types.Part.from_text(text=correction_prompt),
                ]
            )

            if retried is not None:
                remaining_issues = _find_language_issues(retried)
                if remaining_issues:
                    logger.warning(
                        "Түзетуден кейін де тіл мәселесі қалды (қолмен тексеру қажет): %s",
                        remaining_issues,
                    )
                else:
                    logger.info("Тіл мәселесі түзетуден кейін сәтті жойылды.")
                parsed = retried
            else:
                logger.error("Түзету сұрауы кезінде schema parse сәтсіз аяқталды, бастапқы жауап қалдырылады.")

        return parsed

    except Exception as e:
        logger.error(f"Суретті талдау кезінде қате орын алды: {e}")
        raise