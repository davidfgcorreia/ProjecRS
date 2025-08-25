/*
Frontend API: localizationService.js

Purpose:
- Helpers to call localization-related backend endpoints (PDF section highlighting,
  localization maps, etc.).

Exports:
- getHighlightedPdfSection(queryId, userId, marker)
*/
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Request a highlighted PDF section from the backend localization API.
 * @param {number} queryId - The query ID.
 * @param {number} userId - The user ID.
 * @param {string} marker - The marker string.
 * @returns {Promise<Blob>} - The PDF file as a Blob.
 */
export async function getHighlightedPdfSection(queryId, userId, marker) {
  const url = `${API_BASE_URL}/localization/pdf-section/`;
    const params = { query_id: String(queryId), user_id: userId, marker };
  const response = await axios.get(url, {
    params,
    responseType: 'blob', // Ensure we get a PDF blob
  });
  return response.data;
}
