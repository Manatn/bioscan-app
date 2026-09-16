import React from 'react';
import { CheckCircle, AlertTriangle, Stethoscope, Leaf } from 'lucide-react';
import ConfidenceGauge from './ConfidenceGauge';
import ImageWithMarkers from './ImageWithMarkers';

export default function AnalysisResult({ result, imageSrc }) {
  if (!result) return null;

  const isHealthy = result.is_healthy;
  
  const getSeverityBadge = (severity) => {
    const sevClass = {
      'жоғары': 'bg-red-100 text-red-800 border-red-200',
      'орташа': 'bg-orange-100 text-orange-800 border-orange-200',
      'төмен': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'сау': 'bg-green-100 text-green-800 border-green-200',
    }[severity?.toLowerCase()] || 'bg-gray-100 text-gray-800 border-gray-200';

    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium border ${sevClass}`}>
        {severity}
      </span>
    );
  };

  return (
    <div className="card animate-slide-up">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 pb-6 border-b border-gray-100">
        <div>
          <div className="flex items-center gap-2 mb-2">
            {isHealthy ? (
              <div className="flex items-center gap-1.5 text-green-600 font-medium bg-green-50 px-2 py-1 rounded-md text-sm">
                <CheckCircle className="w-4 h-4" />
                Өсімдік сау
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-red-600 font-medium bg-red-50 px-2 py-1 rounded-md text-sm">
                <AlertTriangle className="w-4 h-4" />
                Ауру анықталды
              </div>
            )}
            {getSeverityBadge(result.severity)}
          </div>
          <h2 className="text-3xl font-bold text-gray-800">{result.condition_name}</h2>
        </div>
        
        <div className="shrink-0">
          <ConfidenceGauge value={result.confidence} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Жүктелген фото</h3>
          <div className="bg-gray-50 rounded-xl p-2 border border-gray-100">
            <ImageWithMarkers 
              imageSrc={imageSrc} 
              markers={result.visual_markers || []} 
              severity={result.severity} 
            />
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 text-gray-800">
              <Leaf className="w-5 h-5 text-bio-500" />
              Көрнекі белгілер
            </h3>
            {result.visual_signs && result.visual_signs.length > 0 ? (
              <ul className="space-y-2">
                {result.visual_signs.map((sign, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-700">
                    <span className="text-bio-500 mt-1.5">•</span>
                    <span>{sign}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 italic">Белгілер табылмады</p>
            )}
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 text-gray-800">
              <Stethoscope className="w-5 h-5 text-bio-500" />
              Ұсыныстар
            </h3>
            {result.recommendations && result.recommendations.length > 0 ? (
              <ol className="space-y-3">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex gap-3 text-gray-700">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-bio-100 text-bio-700 flex items-center justify-center text-sm font-bold">
                      {idx + 1}
                    </span>
                    <span className="mt-0.5">{rec}</span>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="text-gray-500 italic">Ұсыныстар жоқ</p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-gray-100">
        <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-xl border border-gray-100">
          {result.summary}
        </p>
      </div>
    </div>
  );
}
