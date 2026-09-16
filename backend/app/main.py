import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalyzeResponse, HistoryItem
from app.ai_service import analyze_image
from app.supabase_service import upload_image, save_analysis, get_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BioScan API",
    version="1.0.0",
    description="API бэкенда для анализа заболеваний растений на основе ИИ (Google Gemini)."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Проверка статуса сервиса."""
    return {"status": "ok"}

@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    """Анализирует загруженное изображение на наличие болезней растений."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением.")

    try:
        file_bytes = await file.read()
        
        # 1. Анализ изображения через Gemini
        analysis_result = await analyze_image(file_bytes, file.content_type)
        
        image_url = None
        analysis_id = None
        
        # 2. Загрузка в Supabase (если доступно)
        try:
            image_url = upload_image(file_bytes, file.filename, file.content_type)
            
            result_dict = analysis_result.model_dump()
            result_dict["visual_markers"] = [m.model_dump() for m in analysis_result.visual_markers]
            
            analysis_id = save_analysis(result_dict, image_url, file.filename)
        except Exception as sb_err:
            logger.warning(f"Ошибка интеграции с Supabase: {sb_err}")

        return AnalyzeResponse(
            result=analysis_result,
            image_url=image_url,
            analysis_id=analysis_id
        )
    except Exception as e:
        logger.error(f"Внутренняя ошибка сервера: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обработке изображения")

@app.get("/api/v1/history", response_model=list[HistoryItem])
async def history(limit: int = 20):
    """Возвращает историю ранее проведенных анализов."""
    try:
        items = get_history(limit)
        return items
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении истории")
