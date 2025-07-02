// src/api/resultService.js

export async function getResult(queryId) {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/result/${queryId}`)
  if (!response.ok) {
    throw new Error('Failed to fetch result')
  }
  return await response.json()
}
