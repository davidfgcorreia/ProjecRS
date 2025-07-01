<template>
  <div class="register-container">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <input v-model="name" type="text" placeholder="Name" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">Register</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">User created! Redirecting to login...</p>
    <button v-if="!success" @click="goToLogin" style="margin-top:1em;width:100%">Back to Login</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { registerUser } from '../api/userService'

const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const success = ref(false)
const router = useRouter()

async function register() {
  error.value = ''
  success.value = false
  try {
    await registerUser({ name: name.value, email: email.value, password: password.value })
    success.value = true
    name.value = ''
    email.value = ''
    password.value = ''
    setTimeout(() => router.push({ name: 'Login' }), 1500)
  } catch (err) {
    error.value = err.message || 'Registration failed'
  }
}

function goToLogin() {
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.register-container { max-width: 300px; margin: 40px auto; padding: 2em; border: 1px solid #eee; border-radius: 8px; }
input { display: block; width: 100%; margin-bottom: 1em; padding: 0.5em; }
button { width: 100%; padding: 0.5em; }
.error { color: red; }
.success { color: green; }
</style>
