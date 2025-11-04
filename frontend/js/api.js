// frontend/js/api.js
import { getToken, clearToken } from './auth.js';

const API_BASE = '';

/**
 * Get headers with authentication token if available
 * @returns {object} Headers object
 */
function getAuthHeaders() {
  const headers = {};
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Handle JSON responses and authentication errors
 * @param {Response} res - Fetch response
 * @returns {Promise<object>} JSON data
 */
async function handleJson(res) {
  if (!res.ok) {
    // Handle 401 Unauthorized - redirect to login
    if (res.status === 401) {
      clearToken();
      const currentPath = window.location.pathname;
      if (currentPath !== '/login.html' && currentPath !== '/register.html') {
        localStorage.setItem('return_url', currentPath + window.location.search);
        window.location.href = '/login.html';
      }
    }
    
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${text || res.statusText}`);
  }
  return res.json();
}

export async function listItems() {
  const res = await fetch(`${API_BASE}/items/`, { method: 'GET' });
  return handleJson(res);
}

export async function getItem(itemId) {
  const res = await fetch(`${API_BASE}/items/${encodeURIComponent(itemId)}`, { method: 'GET' });
  return handleJson(res);
}

export async function uploadItem(file, caption) {
  const fd = new FormData();
  fd.append('file', file);
  if (caption != null) fd.append('caption', caption);
  
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/upload`, { 
    method: 'POST', 
    body: fd,
    headers
  });
  return handleJson(res);
}

export async function updateItem(itemId, caption) {
  const fd = new FormData();
  fd.append('caption', caption);
  
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/items/${encodeURIComponent(itemId)}`, {
    method: 'PATCH',
    body: fd,
    headers
  });
  return handleJson(res);
}

export async function deleteItem(itemId) {
  const headers = getAuthHeaders();
  const res = await fetch(`${API_BASE}/items/${encodeURIComponent(itemId)}`, { 
    method: 'DELETE',
    headers
  });
  if (!res.ok) {
    // Handle 401 Unauthorized
    if (res.status === 401) {
      clearToken();
      localStorage.setItem('return_url', window.location.pathname + window.location.search);
      window.location.href = '/login.html';
    }
    const text = await res.text().catch(() => '');
    throw new Error(`Delete failed: ${res.status} ${text || res.statusText}`);
  }
  return true;
}

// Helper to normalize image URL from item
export function getItemImageUrl(item) {
  if (item.url && (item.url.startsWith('http://') || item.url.startsWith('https://') || item.url.startsWith('/'))) {
    return item.url;
  }
  if (item.filename) {
    return `/uploads/${item.filename}`;
  }
  return '';
}
