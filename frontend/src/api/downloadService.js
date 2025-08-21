// API service for downloading table files
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Download a table file from the backend.
 * @param {Object} params - Parameters for download
 * @param {string} params.format - File format (csv, xlsx, pdf, docx)
 * @param {string} params.queryId - Query ID
 */
export async function downloadTableFile({ format, queryId }) {
  const url = `${API_BASE_URL}/download/`
  const response = await axios.get(url, {
    params: { format, query_id: queryId },
    responseType: 'blob', // Important for file downloads
  })
  // Trigger browser download
  const fileUrl = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = fileUrl
  let ext = format === 'docx' ? 'docx' : format;
  link.setAttribute('download', `table_${queryId}.${ext}`)
  document.body.appendChild(link)
  link.click()
  link.remove()
}
