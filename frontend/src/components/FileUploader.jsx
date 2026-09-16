import React, { useRef, useState } from 'react';
import { Upload, ImagePlus, X, Loader2 } from 'lucide-react';

export default function FileUploader({ onFileSelect, isLoading, disabled }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (!file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение');
      return;
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl('');
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleAnalyze = () => {
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  };

  return (
    <div className="card mb-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Загрузка изображения</h2>
      
      {!selectedFile ? (
        <div 
          className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
            dragActive ? 'border-bio-500 bg-bio-50' : 'border-gray-300 hover:border-bio-400 bg-gray-50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input 
            ref={inputRef}
            type="file" 
            className="hidden" 
            accept="image/*" 
            onChange={handleChange}
            disabled={disabled || isLoading}
          />
          <Upload className={`w-12 h-12 mx-auto mb-4 ${dragActive ? 'text-bio-500' : 'text-gray-400'}`} />
          <p className="text-gray-600 mb-2 font-medium">Нажмите или перетащите фото сюда</p>
          <p className="text-sm text-gray-400">Поддерживаются форматы JPG, PNG, WEBP</p>
        </div>
      ) : (
        <div className="flex flex-col items-center">
          <div className="relative w-full max-w-md mx-auto mb-6 group">
            <img 
              src={previewUrl} 
              alt="Preview" 
              className="w-full h-auto rounded-xl shadow-sm object-contain max-h-[400px]"
            />
            {!isLoading && (
              <button 
                onClick={handleClear}
                className="absolute top-2 right-2 p-1 bg-white rounded-full shadow-md text-gray-500 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
          
          <div className="flex flex-wrap justify-between w-full max-w-md items-center gap-4">
            <div className="text-sm text-gray-600 truncate max-w-[200px]">
              {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} МБ)
            </div>
            
            <div className="flex gap-2">
              <button 
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors disabled:opacity-50"
                onClick={handleClear}
                disabled={isLoading}
              >
                Очистить
              </button>
              <button 
                className="btn-primary flex items-center"
                onClick={handleAnalyze}
                disabled={isLoading || disabled}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Анализ...
                  </>
                ) : (
                  <>
                    <ImagePlus className="w-5 h-5 mr-2" />
                    Анализировать
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
