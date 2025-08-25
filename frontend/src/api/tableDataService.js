/*
Frontend API: tableDataService.js

Purpose:
- Table data CRUD, merging, cell updates and fetching on-demand table descriptions.

Exports:
- getTableDescription(query_id)
- mergeTableColumns(payload)
- sendTableData({ query_id, userid, num_rows, row_ids })
- getTableData(query_id)
- updateTableCell(payload)
*/

/**
 * Fetch table description by queryId from backend.
 * @param {string} query_id - The query ID for the table.
 * @returns {Promise<string>} - Table description text.
 */
export async function getTableDescription(query_id) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const response = await fetch(`${base}/tabledata/table-description/?query_id=${encodeURIComponent(query_id)}`)
  if (!response.ok) {
    let errText = 'Failed to fetch table description';
    try {
      const err = await response.json();
      errText = typeof err === 'string' ? err : JSON.stringify(err, null, 2);
    } catch (e) {
      errText = await response.text();
    }
    throw new Error(errText);
  }
  return response.text();
}
/**
 * Merge two columns in the table on the backend and get the updated table.
 * @param {Object} payload - { query_id, col1, col2 }
 * @returns {Promise<any>} - API response (updated table)
 */
export async function mergeTableColumns(payload) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const response = await fetch(`${base}/tabledata/merge-columns/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!response.ok) {
    let errText = 'Failed to merge table columns';
    try {
      const err = await response.json();
      errText = typeof err === 'string' ? err : JSON.stringify(err, null, 2);
    } catch (e) {
      errText = await response.text();
    }
    throw new Error(errText);
  }
  return response.json();
}
/**
 * Merge two columns on the server and return the updated table payload.
 * @param {Object} payload - { query_id, col1, col2 }
 * @returns {Promise<Object>} - Updated table data from backend.
 */
// src/api/tableDataService.js

export async function sendTableData({ query_id, userid, num_rows, row_ids }) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const response = await fetch(`${base}/tabledata/filled/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query_id, userid, num_rows, row_ids })
  })
  if (!response.ok) {
    let errText = 'Failed to send table data';
    try {
      const err = await response.json();
      errText = typeof err === 'string' ? err : JSON.stringify(err, null, 2);
    } catch (e) {
      errText = await response.text();
    }
    throw new Error(errText);
  }
  return response.json()
}
/**
 * Send filled table metadata to the backend (finalize table state).
 * @param {Object} params - { query_id, userid, num_rows, row_ids }
 * @returns {Promise<Object>} - Server response JSON.
 */

export async function getTableData(query_id) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const response = await fetch(`${base}/tabledata/?query_id=${encodeURIComponent(query_id)}`)
  if (!response.ok) throw new Error('Failed to fetch table data')
  return response.json()
}

/**
 * Update a single cell in the table on the backend.
 * @param {Object} payload - { query_id, row_id, col, new_value }
 * @returns {Promise<any>} - API response
 */
export async function updateTableCell(payload) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const response = await fetch(`${base}/tabledata/update-cell/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!response.ok) {
    let errText = 'Failed to update table cell';
    try {
      const err = await response.json();
      errText = typeof err === 'string' ? err : JSON.stringify(err, null, 2);
    } catch (e) {
      errText = await response.text();
    }
    throw new Error(errText);
  }
  return response.json();
}
