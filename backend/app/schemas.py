from pydantic import BaseModel, Field
from typing import Literal

class VisualMarker(BaseModel):
    """Суреттегі визуалды маркерге (bounding box) арналған модель."""
    box_2d: list[int] = Field(
        min_length=4,
        max_length=4,
        description="Төртбұрыш координаталары [ymin, xmin, ymax, xmax] форматында, 0-ден 1000-ға дейінгі мәндер."
    )
    label: str = Field(description="Белгіленген аймақтың атауы/сипаттамасы (мысалы, 'дақ', 'зең').")

class HealthAnalysisResult(BaseModel):
    """Өсімдік денсаулығын талдау нәтижесі."""
    is_healthy: bool = Field(description="Өсімдіктің сау екенін көрсетеді.")
    condition_name: str = Field(description="Ауру немесе жағдай атауы.")
    confidence: float = Field(ge=0.0, le=1.0, description="Модельдің диагнозға сенімділігі (0.0-ден 1.0-ге дейін).")
    severity: Literal["Сау", "Төмен", "Орташа", "Жоғары"] = Field(description="Аурудың ауырлық деңгейі.")
    visual_signs: list[str] = Field(description="Аурудың визуалды белгілерінің тізімі.")
    visual_markers: list[VisualMarker] = Field(description="Суреттегі визуалды маркерлер (проблемалық аймақтар).")
    recommendations: list[str] = Field(description="Емдеу және күтім жасау бойынша ұсыныстар.")
    summary: str = Field(description="Талдау нәтижелері бойынша қысқаша түйіндеме.")

class AnalyzeResponse(BaseModel):
    """Суретті талдау сұранысына API жауабы."""
    result: HealthAnalysisResult = Field(description="Талдау нәтижелері.")
    image_url: str | None = Field(default=None, description="Жүктелген суреттің URL мекенжайы.")
    analysis_id: str | None = Field(default=None, description="Тарихтағы жазба идентификаторы (ID).")

class HistoryItem(BaseModel):
    """Талдау тарихының элементі."""
    id: str = Field(description="Талдаудың бірегей идентификаторы.")
    created_at: str = Field(description="Жазба құрылған күн мен уақыт.")
    image_url: str = Field(description="Суреттің URL мекенжайы.")
    is_healthy: bool = Field(description="Өсімдік сау ма.")
    condition_name: str = Field(description="Ауру немесе жағдай атауы.")
    confidence: float = Field(description="Диагнозға сенімділік.")
    severity: str = Field(description="Ауырлық деңгейі.")
    visual_signs: list[str] = Field(description="Визуалды белгілер.")
    visual_markers: list[VisualMarker] = Field(description="Визуалды маркерлер.")
    recommendations: list[str] = Field(description="Ұсыныстар.")
    summary: str | None = Field(default=None, description="Қысқаша түйіндеме.")
