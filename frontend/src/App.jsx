import React, { useState, useEffect } from 'react';
import FileUploader from './components/FileUploader';
import AnalysisResult from './components/AnalysisResult';
import HistoryPanel from './components/HistoryPanel';
import { analyzeImage, fetchHistory } from './lib/api';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewSrc, setPreviewSrc] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const [history, setHistory] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState(null);

  const loadHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleFileSelect = async (file) => {
    setError(null);
    setSelectedFile(file);
    setPreviewSrc(URL.createObjectURL(file));
    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      const response = await analyzeImage(file);
      setAnalysisResult(response.result);
      loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleHistorySelect = (item) => {
    setError(null);
    setSelectedFile(null);
    setPreviewSrc(item.image_url);
    setAnalysisResult({
      is_healthy: item.is_healthy,
      condition_name: item.condition_name,
      confidence: item.confidence,
      severity: item.severity,
      visual_signs: item.visual_signs || [],
      visual_markers: item.visual_markers || [],
      recommendations: item.recommendations || [],
      summary: item.summary || ''
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 animate-fade-in text-gray-800">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl" role="img" aria-label="leaf">🌿</span>
            <div>
              <h1 className="text-2xl font-bold text-bio-800 leading-tight">BioScan</h1>
              <p className="text-sm text-gray-500 font-medium">Өсімдіктер ауруларын ЖИ-диагностикалау</p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <FileUploader 
              onFileSelect={handleFileSelect}
              isLoading={isAnalyzing}
              disabled={isAnalyzing}
            />

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
                <p className="font-medium">Қате</p>
                <p className="text-sm">{error}</p>
              </div>
            )}

            {analysisResult && previewSrc && (
              <AnalysisResult 
                result={analysisResult} 
                imageSrc={previewSrc} 
              />
            )}
          </div>

          <div className="lg:col-span-1 h-[600px] lg:h-auto">
            <HistoryPanel 
              history={history}
              onSelect={handleHistorySelect}
              isLoading={isLoadingHistory}
            />
          </div>
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-gray-500 text-sm">
          <p>© {new Date().getFullYear()} BioScan. Биология бойынша жарысқа арналған жоба.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
