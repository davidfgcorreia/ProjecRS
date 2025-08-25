/*
Frontend API: resultService.js

Purpose:
- Fetch processed result objects for a given query (used by result views).

Exports:
- getResult(queryId)
*/
/**
 * Fetch processed result for a query.
 * @param {string|number} queryId - The query identifier.
 * @returns {Promise<Object>} - Parsed JSON result object from the backend.
 */
export async function getResult(queryId) {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/result/${queryId}`)
  if (!response.ok) {
    throw new Error('Failed to fetch result')
  }
  return await response.json()
}
