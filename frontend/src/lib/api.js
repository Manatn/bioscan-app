const API_URL = import.meta.env.VITE_API_URL || '';

export async function analyzeImage(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_URL}/api/v1/analyze`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Ошибка сервера: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    throw new Error(`Не удалось проанализировать изображение: ${error.message}`);
  }
}

export async function fetchHistory(limit = 20) {
  try {
    const response = await fetch(`${API_URL}/api/v1/history?limit=${limit}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Ошибка сервера: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    throw new Error(`Не удалось загрузить историю: ${error.message}`);
  }
}
