import React from 'react';
import { History, AlertTriangle, CheckCircle } from 'lucide-react';

export default function HistoryPanel({ history = [], onSelect, isLoading }) {
  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4 pb-2 border-b border-gray-100">
        <History className="w-5 h-5 text-bio-600" />
        <h2 className="text-lg font-semibold text-gray-800">История анализов</h2>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 space-y-3">
        {isLoading ? (
          Array(4).fill(0).map((_, i) => (
            <div key={i} className="animate-pulse flex gap-3 p-3 border border-gray-100 rounded-xl">
              <div className="w-12 h-12 bg-gray-200 rounded-md shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          ))
        ) : history.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="mb-2">Нет анализов</p>
            <p className="text-sm">Загрузите фото для первого анализа</p>
          </div>
        ) : (
          history.map((item) => {
            const isHealthy = item.is_healthy;
            const date = new Date(item.created_at).toLocaleDateString('ru-RU', {
              day: 'numeric',
              month: 'short',
              hour: '2-digit',
              minute: '2-digit'
            });

            return (
              <div 
                key={item.id}
                onClick={() => onSelect(item)}
                className="group flex gap-3 p-3 border border-gray-100 rounded-xl hover:border-bio-300 hover:bg-bio-50 cursor-pointer transition-colors"
              >
                {item.image_url ? (
                  <img 
                    src={item.image_url} 
                    alt={item.condition_name} 
                    className="w-12 h-12 rounded-md object-cover border border-gray-200 shrink-0 group-hover:border-bio-300"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-md bg-gray-100 border border-gray-200 shrink-0 flex items-center justify-center">
                    <History className="w-5 h-5 text-gray-400" />
                  </div>
                )}
                
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start mb-1">
                    <p className="text-sm font-semibold text-gray-800 truncate pr-2">
                      {item.condition_name}
                    </p>
                    {isHealthy ? (
                      <CheckCircle className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                    )}
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-500">{date}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                      item.severity?.toLowerCase() === 'высокая' ? 'bg-red-100 text-red-700' :
                      item.severity?.toLowerCase() === 'средняя' ? 'bg-orange-100 text-orange-700' :
                      item.severity?.toLowerCase() === 'низкая' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {item.severity}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
