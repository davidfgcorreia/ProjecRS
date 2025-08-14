import axios from 'axios'
// Set Axios base URL to FastAPI backend
axios.defaults.baseURL = 'http://localhost:8000';

/**
 * Merge two cells in the same column via backend API.
 * If the display values are the same, keeps one and merges meta from both.
 *
 * @param {Object} params - Parameters for the merge operation.
 * @param {string|number} params.query_id - The query ID.
 * @param {string} params.col_key - The column key (e.g., 'col5').
 * @param {number} params.row_idx1 - The index of the first row to merge.
 * @param {number} params.row_idx2 - The index of the second row to merge.
 * @returns {Promise<Object>} - The updated table data from the backend.
 */
export async function mergeCellApi({ query_id, col_key, row_idx1, row_idx2 }) {
  // Debug log for request parameters
  console.log('[mergeCellApi] Request:', {
    query_id,
    col_key,
    row_idx1,
    row_idx2
  })
  try {
    const response = await axios.post('/tabledata/merge-cell/', {
      query_id,
      col_key,
      row_idx1,
      row_idx2
    })
    // Debug log for response
    console.log('[mergeCellApi] Response:', response)
    return response.data
  } catch (error) {
    // Debug log for error
    console.error('[mergeCellApi] Error:', error)
    throw error
  }
}
