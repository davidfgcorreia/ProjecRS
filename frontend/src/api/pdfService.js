// src/api/pdfService.js
// Service for requesting PDFs from the backend
import axios from 'axios'

/**
 * Request a PDF for a given cell, using query_id and user_id as metadata.
 * @param {Object} params
 * @param {string|number} params.query_id - The query ID for the table.
 * @param {string|number} params.user_id - The user ID for the request.
 * @param {string} [params.value] - The cell value (optional, for context).
 * @returns {Promise<any>} The backend response.
 */
export async function requestPdf({ query_id, user_id, value }) {
  // Adjust endpoint and params as needed
  return axios.get('/api/pdf', { params: { query_id, user_id, value } })
}
