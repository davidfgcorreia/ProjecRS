// tableDownloadService.js
// Service to request table downloads from backend
// Usage: downloadTableFile(format, tableData)

import axios from 'axios'

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
