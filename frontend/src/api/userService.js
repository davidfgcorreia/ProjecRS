// src/api/userService.js
export async function registerUser({ name, email, password }) {
  const response = await fetch('http://localhost:8000/users/', {
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
