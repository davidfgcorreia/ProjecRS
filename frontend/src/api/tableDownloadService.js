/*
Frontend API: tableDownloadService.js

Purpose:
- Request server-side table downloads (client posts table data and requests a file).

Exports:
- downloadTableFile(format, tableData)
*/
import axios from 'axios'

// Note: configure axios.baseURL globally or use import.meta.env.VITE_API_BASE_URL when needed.

/**
 * Request server-side table download.
 * @param {string} format - File format to request (e.g., 'xlsx', 'pdf').
 * @param {Object} tableData - Table payload sent to backend for conversion.
 * @returns {Promise<void>} - Resolves when the browser download is triggered.
 */

export async function downloadTableFile(format, tableData) {
  // Example: POST to /api/download-table with format and tableData
  // Backend should return a file (blob)
  try {
    const response = await axios.post(`/api/download-table`, {
      format,
      table: tableData
    }, {
      responseType: 'blob'
    })
    // Create a link to download the file
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `table.${format}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    throw error
  }
}
