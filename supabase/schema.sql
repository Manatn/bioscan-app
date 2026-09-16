-- ============================================
-- BioScan: Дерекқор схемасы
-- ============================================

-- Өсімдіктерді талдау тарихының кестесі
CREATE TABLE IF NOT EXISTS analysis_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    
    -- Суретке сілтеме
    image_url TEXT NOT NULL,
    image_path TEXT,  -- Supabase Storage ішіндегі жол
    
    -- Талдау нәтижелері
    is_healthy BOOLEAN NOT NULL,
    condition_name TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    severity TEXT NOT NULL CHECK (severity IN ('Сау', 'Төмен', 'Орташа', 'Жоғары')),
    
    -- Мәліметтер (икемділік үшін JSONB ретінде сақталады)
    visual_signs JSONB DEFAULT '[]'::jsonb,
    visual_markers JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    
    -- Қысқаша түйіндеме
    summary TEXT
);

-- Күн бойынша жылдам сұрыптауға арналған индекс
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at 
    ON analysis_history(created_at DESC);

-- Row Level Security (Жол деңгейіндегі қауіпсіздік) қосу
ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;

-- Саясат: барлық операцияларға рұқсат беру (қарапайымдылық үшін, продакшенде шектеу қажет)
CREATE POLICY "Allow public access" 
    ON analysis_history 
    FOR ALL 
    USING (true) 
    WITH CHECK (true);

-- ============================================
-- Storage: plant-scans бакеті
-- Supabase Dashboard-та қолмен жасаңыз:
--   1. Storage -> New Bucket
--   2. Name: plant-scans
--   3. Public bucket: ON
--   4. INSERT және SELECT үшін кіру саясатын қосыңыз
-- ============================================

-- Storage үшін мысал саясат (SQL Editor-да орындаңыз):
-- plant-scans бакеті үшін INSERT саясаты:
INSERT INTO storage.policies (name, bucket_id, operation, definition)
SELECT 
    'Allow public uploads',
    id,
    'INSERT',
    '(true)'
FROM storage.buckets 
WHERE name = 'plant-scans'
ON CONFLICT DO NOTHING;

-- plant-scans бакеті үшін SELECT саясаты:
INSERT INTO storage.policies (name, bucket_id, operation, definition)
SELECT 
    'Allow public reads',
    id,
    'SELECT',
    '(true)'
FROM storage.buckets 
WHERE name = 'plant-scans'
ON CONFLICT DO NOTHING;
