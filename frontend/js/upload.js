// frontend/js/upload.js
import { uploadItem } from './api.js';

function $(id) {
  return document.getElementById(id);
}

function setStatus(msg, kind = 'info') {
  const el = $('upload-status');
  el.textContent = msg;
  el.className = kind === 'error'
    ? 'text-sm text-red-600'
    : kind === 'success'
    ? 'text-sm text-green-600'
    : 'text-sm text-gray-600';
}

function previewFile(file) {
  const preview = $('preview');
  preview.innerHTML = '';
  if (!file) return;
  const img = document.createElement('img');
  img.className = 'max-h-64 object-contain rounded border';
  img.src = URL.createObjectURL(file);
  img.onload = () => URL.revokeObjectURL(img.src);
  preview.appendChild(img);
}

function validate(file) {
  if (!file) return 'Please choose an image file.';
  if (!file.type.startsWith('image/')) return 'Only image files are allowed.';
  if (file.size > 10 * 1024 * 1024) return 'File must be 10 MB or smaller.';
  return null;
}

async function init() {
  const form = $('upload-form');
  const fileInput = $('file');
  const captionInput = $('caption');
  const submitBtn = $('submit-btn');

  fileInput.addEventListener('change', () => previewFile(fileInput.files[0]));

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    const err = validate(file);
    if (err) {
      setStatus(err, 'error');
      return;
    }
    setStatus('Uploading...');
    submitBtn.disabled = true;

    try {
      await uploadItem(file, captionInput.value || '');
      setStatus('Upload complete. Redirecting…', 'success');
      setTimeout(() => {
        window.location.href = 'index.html';
      }, 500);
    } catch (ex) {
      setStatus(`Upload failed: ${ex.message}`, 'error');
    } finally {
      submitBtn.disabled = false;
    }
  });
}

document.addEventListener('DOMContentLoaded', init);
