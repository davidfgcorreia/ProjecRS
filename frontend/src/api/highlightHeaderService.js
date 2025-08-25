/*
Frontend API: highlightHeaderService.js

Purpose:
- Request a PDF from the backend with header values highlighted.

Exports:
- getHighlightedHeaderPdf(queryId, header, pdfName)
*/
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Request a PDF with highlighted header values from the backend.
 * @param {string} queryId - The query ID (string/UUID)
 * @param {string} header - The header name to highlight
 * @param {string} pdfName - The PDF file name to select
 * @returns {Promise<Blob>} - PDF blob
 */
export async function getHighlightedHeaderPdf(queryId, header, pdfName) {
  const url = `${API_BASE_URL}/highlight-header/`
  const params = { query_id: queryId, header, pdf_name: pdfName }
  const response = await axios.get(url, {
    params,
    responseType: 'blob', // Ensure we get a PDF blob
  })
  return response.data
}
