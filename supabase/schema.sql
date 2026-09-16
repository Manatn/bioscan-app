-- ============================================
-- BioScan: Схема базы данных
-- ============================================

-- Таблица истории анализов растений
CREATE TABLE IF NOT EXISTS analysis_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    
    -- Ссылка на изображение
    image_url TEXT NOT NULL,
    image_path TEXT,  -- путь внутри Supabase Storage
    
    -- Результаты анализа
    is_healthy BOOLEAN NOT NULL,
    condition_name TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    severity TEXT NOT NULL CHECK (severity IN ('Здоров', 'Низкая', 'Средняя', 'Высокая')),
    
    -- Детали (хранятся как JSONB для гибкости)
    visual_signs JSONB DEFAULT '[]'::jsonb,
    visual_markers JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    
    -- Краткое заключение
    summary TEXT
);

-- Индекс для быстрой сортировки по дате
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at 
    ON analysis_history(created_at DESC);

-- Включение Row Level Security
ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;

-- Политика: разрешить все операции (для простоты, в продакшене ограничить)
CREATE POLICY "Allow public access" 
    ON analysis_history 
    FOR ALL 
    USING (true) 
    WITH CHECK (true);

-- ============================================
-- Storage: бакет plant-scans
-- Создайте вручную в Supabase Dashboard:
--   1. Storage -> New Bucket
--   2. Name: plant-scans
--   3. Public bucket: ON
--   4. Добавьте политику доступа для INSERT и SELECT
-- ============================================

-- Пример политики для Storage (выполните в SQL Editor):
-- INSERT политика для бакета plant-scans:
INSERT INTO storage.policies (name, bucket_id, operation, definition)
SELECT 
    'Allow public uploads',
    id,
    'INSERT',
    '(true)'
FROM storage.buckets 
WHERE name = 'plant-scans'
ON CONFLICT DO NOTHING;

-- SELECT политика для бакета plant-scans:
INSERT INTO storage.policies (name, bucket_id, operation, definition)
SELECT 
    'Allow public reads',
    id,
    'SELECT',
    '(true)'
FROM storage.buckets 
WHERE name = 'plant-scans'
ON CONFLICT DO NOTHING;
