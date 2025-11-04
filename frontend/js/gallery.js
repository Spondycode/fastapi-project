// frontend/js/gallery.js
import { listItems, getItemImageUrl } from './api.js';

function el(tag, className) {
  const e = document.createElement(tag);
  if (className) e.className = className;
  return e;
}

function renderCard(item) {
  const card = el('div', 'rounded-lg border overflow-hidden hover:shadow transition');
  const link = el('a', 'block');
  link.href = `post.html?id=${encodeURIComponent(item.id)}`;

  const img = el('img', 'w-full object-cover h-48 bg-gray-100');
  img.src = getItemImageUrl(item);
  img.alt = item.caption || item.filename || 'image';

  const body = el('div', 'p-3 space-y-1');
  const cap = el('div', 'text-sm text-gray-900 line-clamp-2');
  cap.textContent = item.caption || '(no caption)';
  const meta = el('div', 'text-xs text-gray-500');
  const created = item.created_at ? new Date(item.created_at).toLocaleString() : '';
  meta.textContent = [item.file_type, created].filter(Boolean).join(' • ');

  link.appendChild(img);
  body.appendChild(cap);
  body.appendChild(meta);
  card.appendChild(link);
  card.appendChild(body);
  return card;
}

async function init() {
  const root = document.getElementById('gallery-root');
  const grid = document.getElementById('gallery-grid');
  const loading = document.getElementById('gallery-loading');
  const empty = document.getElementById('gallery-empty');

  loading.style.display = 'block';
  empty.style.display = 'none';
  grid.innerHTML = '';

  try {
    const data = await listItems();
    const items = data.items || [];
    if (!items || items.length === 0) {
      empty.style.display = 'block';
      return;
    }
    items.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
    for (const item of items) {
      grid.appendChild(renderCard(item));
    }
  } catch (err) {
    const alert = el('div', 'p-3 rounded bg-red-50 text-red-700 border border-red-200');
    alert.textContent = `Failed to load posts: ${err.message}`;
    root.prepend(alert);
  } finally {
    loading.style.display = 'none';
  }
}

document.addEventListener('DOMContentLoaded', init);
