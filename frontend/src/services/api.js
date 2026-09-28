const BASE_URL = 'http://localhost:8000/api';

export async function sendChatMessage(query) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to communicate with JEV Agent Router');
  }

  return response.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload document');
  }

  return response.json();
}

export async function getDocuments() {
  const response = await fetch(`${BASE_URL}/documents`);
  if (!response.ok) {
    throw new Error('Failed to fetch document list');
  }
  return response.json();
}

export async function deleteDocument(docId) {
  const response = await fetch(`${BASE_URL}/documents/${docId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete document');
  }
  return response.json();
}
