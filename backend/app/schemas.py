from pydantic import BaseModel, Field
from typing import Literal

class VisualMarker(BaseModel):
    """Модель для визуального маркера (bounding box) на изображении."""
    box_2d: list[int] = Field(
        min_length=4,
        max_length=4,
        description="Координаты прямоугольника в формате [ymin, xmin, ymax, xmax], значения от 0 до 1000."
    )
    label: str = Field(description="Метка/описание выделенной области (например, 'пятно', 'плесень').")

class HealthAnalysisResult(BaseModel):
    """Результат анализа здоровья растения."""
    is_healthy: bool = Field(description="Указывает, является ли растение здоровым.")
    condition_name: str = Field(description="Название болезни или состояния.")
    confidence: float = Field(ge=0.0, le=1.0, description="Уверенность модели в диагнозе (от 0.0 до 1.0).")
    severity: Literal["Здоров", "Низкая", "Средняя", "Высокая"] = Field(description="Степень тяжести заболевания.")
    visual_signs: list[str] = Field(description="Список визуальных признаков заболевания.")
    visual_markers: list[VisualMarker] = Field(description="Визуальные маркеры (проблемные зоны) на изображении.")
    recommendations: list[str] = Field(description="Рекомендации по лечению и уходу.")
    summary: str = Field(description="Краткое резюме по результатам анализа.")

class AnalyzeResponse(BaseModel):
    """Ответ API на запрос анализа изображения."""
    result: HealthAnalysisResult = Field(description="Результаты анализа.")
    image_url: str | None = Field(default=None, description="URL загруженного изображения.")
    analysis_id: str | None = Field(default=None, description="ID записи в истории.")

class HistoryItem(BaseModel):
    """Элемент истории анализа."""
    id: str = Field(description="Уникальный идентификатор анализа.")
    created_at: str = Field(description="Дата и время создания записи.")
    image_url: str = Field(description="URL изображения.")
    is_healthy: bool = Field(description="Является ли растение здоровым.")
    condition_name: str = Field(description="Название болезни или состояния.")
    confidence: float = Field(description="Уверенность в диагнозе.")
    severity: str = Field(description="Степень тяжести.")
    visual_signs: list[str] = Field(description="Визуальные признаки.")
    visual_markers: list[VisualMarker] = Field(description="Визуальные маркеры.")
    recommendations: list[str] = Field(description="Рекомендации.")
    summary: str | None = Field(default=None, description="Краткое резюме.")
