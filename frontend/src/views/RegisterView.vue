<template>
  <div class="register-container">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <input v-model="name" type="text" placeholder="Name" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <button type="submit">Register</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">User created! You can now log in.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const name = ref('')
const email = ref('')
const error = ref('')
const success = ref(false)
const router = useRouter()

async function register() {
  error.value = ''
  success.value = false
  try {
    const response = await fetch('http://localhost:8000/users/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name.value, email: email.value })
    })
    if (!response.ok) throw new Error('Registration failed')
    success.value = true
    name.value = ''
    email.value = ''
  } catch (err) {
    error.value = err.message || 'Registration failed'
  }
}
</script>

<style scoped>
.register-container { max-width: 300px; margin: 40px auto; padding: 2em; border: 1px solid #eee; border-radius: 8px; }
input { display: block; width: 100%; margin-bottom: 1em; padding: 0.5em; }
button { width: 100%; padding: 0.5em; }
.error { color: red; }
.success { color: green; }
</style>
