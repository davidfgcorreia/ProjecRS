// src/api/tableDataService.js

export async function sendTableData({ query_id, userid, num_rows, row_ids }) {
  const response = await fetch('http://localhost:8000/tabledata/filled/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query_id, userid, num_rows, row_ids })
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Failed to send table data')
  }
  return response.json()
}

export async function getTableData(query_id) {
  const response = await fetch(`http://localhost:8000/tabledata/?query_id=${encodeURIComponent(query_id)}`)
  if (!response.ok) throw new Error('Failed to fetch table data')
  return response.json()
}
