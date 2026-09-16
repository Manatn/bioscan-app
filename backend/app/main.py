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
    description="ЖИ (Google Gemini) негізінде өсімдік ауруларын талдауға арналған бэкенд API."
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
    """Сервис күйін тексеру."""
    return {"status": "ok"}

@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze(file: UploadFile = File(...)):
    """Жүктелген суретті өсімдік ауруларының бар-жоғына талдайды."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл сурет болуы керек.")

    try:
        file_bytes = await file.read()
        
        # 1. Суретті Gemini арқылы талдау
        analysis_result = await analyze_image(file_bytes, file.content_type)
        
        image_url = None
        analysis_id = None
        
        # 2. Supabase-ке жүктеу (егер қолжетімді болса)
        try:
            image_url = upload_image(file_bytes, file.filename, file.content_type)
            
            result_dict = analysis_result.model_dump()
            result_dict["visual_markers"] = [m.model_dump() for m in analysis_result.visual_markers]
            
            analysis_id = save_analysis(result_dict, image_url, file.filename)
        except Exception as sb_err:
            logger.warning(f"Supabase интеграциясының қатесі: {sb_err}")

        return AnalyzeResponse(
            result=analysis_result,
            image_url=image_url,
            analysis_id=analysis_id
        )
    except Exception as e:
        logger.error(f"Сервердің ішкі қатесі: {e}")
        raise HTTPException(status_code=500, detail="Суретті өңдеу кезінде қате орын алды")

@app.get("/api/v1/history", response_model=list[HistoryItem])
async def history(limit: int = 20):
    """Бұрын жүргізілген талдаулардың тарихын қайтарады."""
    try:
        items = get_history(limit)
        return items
    except Exception as e:
        logger.error(f"Тарихты алу кезінде қате орын алды: {e}")
        raise HTTPException(status_code=500, detail="Тарихты алу кезінде қате орын алды")
