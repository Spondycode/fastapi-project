// frontend/js/post.js
import { getItem, deleteItem, updateItem, getItemImageUrl } from './api.js';

function $(id) {
  return document.getElementById(id);
}

function qsParam(name) {
  return new URLSearchParams(window.location.search).get(name);
}

function renderItem(item) {
  const imageWrap = $('post-image');
  imageWrap.innerHTML = '';
  const img = document.createElement('img');
  img.className = 'w-full max-h-[75vh] object-contain bg-gray-50 rounded border';
  img.src = getItemImageUrl(item);
  img.alt = item.caption || item.filename || 'image';
  imageWrap.appendChild(img);

  const meta = $('post-meta');
  meta.innerHTML = '';
  const title = document.createElement('div');
  title.className = 'text-lg font-semibold';
  title.textContent = item.caption || '(no caption)';
  const info = document.createElement('div');
  info.className = 'text-sm text-gray-600';
  const created = item.created_at ? new Date(item.created_at).toLocaleString() : '';
  info.textContent = [item.filename, item.file_type, created].filter(Boolean).join(' • ');
  meta.appendChild(title);
  meta.appendChild(info);
}

async function init() {
  const id = qsParam('id');
  const loading = $('post-loading');
  const error = $('post-error');
  const delBtn = $('delete-btn');
  const editBtn = $('edit-btn');
  const editForm = $('edit-form');
  const editCaptionForm = $('edit-caption-form');
  const captionInput = $('caption-input');
  const cancelEditBtn = $('cancel-edit-btn');
  const editStatus = $('edit-status');
  const postMeta = $('post-meta');

  let currentItem = null;

  if (!id) {
    error.textContent = 'Missing id parameter.';
    error.className = 'p-3 rounded bg-red-50 text-red-700 border border-red-200';
    return;
  }

  loading.style.display = 'block';
  try {
    const item = await getItem(id);
    currentItem = item;
    renderItem(item);

    // Edit button handler
    editBtn.addEventListener('click', () => {
      captionInput.value = currentItem.caption || '';
      postMeta.style.display = 'none';
      editForm.style.display = 'block';
      editStatus.textContent = '';
    });

    // Cancel edit handler
    cancelEditBtn.addEventListener('click', () => {
      editForm.style.display = 'none';
      postMeta.style.display = 'block';
      editStatus.textContent = '';
    });

    // Save edit handler
    editCaptionForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const newCaption = captionInput.value.trim();
      const saveBtn = $('save-btn');
      
      saveBtn.disabled = true;
      editStatus.textContent = 'Saving...';
      editStatus.className = 'text-sm text-gray-600';
      
      try {
        const updated = await updateItem(id, newCaption);
        currentItem = updated;
        renderItem(updated);
        editForm.style.display = 'none';
        postMeta.style.display = 'block';
        editStatus.textContent = '';
      } catch (ex) {
        editStatus.textContent = `Failed to save: ${ex.message}`;
        editStatus.className = 'text-sm text-red-600';
      } finally {
        saveBtn.disabled = false;
      }
    });

    // Delete button handler
    delBtn.addEventListener('click', async () => {
      const ok = confirm('Delete this post? This cannot be undone.');
      if (!ok) return;
      delBtn.disabled = true;
      try {
        await deleteItem(id);
        window.location.href = '/index.html';
      } catch (ex) {
        alert(`Delete failed: ${ex.message}`);
      } finally {
        delBtn.disabled = false;
      }
    });
  } catch (ex) {
    error.textContent = `Failed to load post: ${ex.message}`;
    error.className = 'p-3 rounded bg-red-50 text-red-700 border border-red-200';
  } finally {
    loading.style.display = 'none';
  }
}

document.addEventListener('DOMContentLoaded', init);
