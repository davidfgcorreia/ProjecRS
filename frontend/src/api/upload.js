/*
Frontend API: upload.js

Purpose:
- File upload helpers used by the UI to send PDFs and other files to the backend.

Exports:
- uploadPdf(file, userId)
*/


/**
 * Upload a PDF file to the backend.
 * @param {File} file - The PDF file to upload.
 * @param {string|number} userId - The requesting user's ID.
 * @returns {Promise<Object>} - JSON response from the server describing the upload.
 */

export async function uploadPdf(file, userId) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${base}/upload/pdf/?user_id=${encodeURIComponent(userId)}`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) throw new Error('Upload failed');
  return await response.json();
}
