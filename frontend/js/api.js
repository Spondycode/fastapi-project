// frontend/js/api.js
const API_BASE = '';

async function handleJson(res) {
  if (!res.ok) {
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
  const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: fd });
  return handleJson(res);
}

export async function updateItem(itemId, caption) {
  const fd = new FormData();
  fd.append('caption', caption);
  const res = await fetch(`${API_BASE}/items/${encodeURIComponent(itemId)}`, {
    method: 'PATCH',
    body: fd
  });
  return handleJson(res);
}

export async function deleteItem(itemId) {
  const res = await fetch(`${API_BASE}/items/${encodeURIComponent(itemId)}`, { method: 'DELETE' });
  if (!res.ok) {
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
