// src/api/upload.js
export async function uploadPdf(file, userId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId);
  const response = await fetch('http://localhost:8000/upload/pdf/', {
    method: 'POST',
    body: formData
  });
  if (!response.ok) throw new Error('Upload failed');
  return await response.json();
}
