/*
Frontend API: userService.js

Purpose:
- User registration and user-related backend calls.

Exports:
- registerUser({ name, email, password })
*/

/**
 * Register a new user.
 * @param {Object} params
 * @param {string} params.name
 * @param {string} params.email
 * @param {string} params.password
 * @returns {Promise<Object>} - Created user object from backend.
 */

export async function registerUser({ name, email, password }) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const response = await fetch(`${base}/users/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Registration failed')
  }
  return response.json()
}
