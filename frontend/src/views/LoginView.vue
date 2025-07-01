<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
    <button @click="goToRegister" class="register-btn">Create New User</button>
    <p v-if="error" class="error">{{ error }}</p>
    <!-- Add this button for dev only -->
    <button @click="skipLoginDev">Skip Login (Dev Only)</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

async function login() {
  error.value = ''
  // Replace with real authentication logic as needed
  if (email.value && password.value) {
    // Try to fetch user by email
    const response = await fetch(`http://localhost:8000/users/?skip=0&limit=100`)
    if (response.ok) {
      const users = await response.json()
      const user = users.find(u => u.email === email.value)
      if (user) {
        // Optionally check password here if backend supports it
        localStorage.setItem('user_id', user.id)
        router.push('/upload')
        return
      }
    }
    error.value = 'Invalid credentials'
  } else {
    error.value = 'Invalid credentials'
  }
}

function goToRegister() {
  router.push({ name: 'Register' })
}

function skipLoginDev() {
  localStorage.setItem('user_id', 1)
  router.push({ name: 'Upload' })
}
</script>

<style scoped>
.login-container { max-width: 300px; margin: 40px auto; padding: 2em; border: 1px solid #eee; border-radius: 8px; }
input { display: block; width: 100%; margin-bottom: 1em; padding: 0.5em; }
button { width: 100%; padding: 0.5em; margin-bottom: 0.5em; }
.register-btn { background: #f0f0f0; color: #333; border: 1px solid #ccc; }
.error { color: red; }
</style>
