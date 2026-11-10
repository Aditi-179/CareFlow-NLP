const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000/api' : '/api');

export async function sendHealthcareQuery(query, history = [], enableWebSearch = false) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      history: history.map(msg => ({
        role: msg.role,
        content: msg.content
      })),
      enable_web_search: enableWebSearch
    }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error (${response.status})`);
  }

  return await response.json();
}

export async function uploadMedicalReport(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload-report`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Server error (${response.status})`);
  }

  return await response.json();
}

export async function fetchHealthStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('Backend health check unreachable:', err);
    return null;
  }
}

export async function fetchCategories() {
  try {
    const response = await fetch(`${API_BASE_URL}/categories`);
    if (!response.ok) return [];
    const data = await response.json();
    return data.categories || [];
  } catch (err) {
    console.warn('Categories unreachable:', err);
    return [];
  }
}
