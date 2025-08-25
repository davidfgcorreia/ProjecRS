<!--
RegisterView.vue

Purpose:
- User registration page. Collects required user details and calls the
  `userService` registration endpoint. On success, optionally signs the user
  in and redirects to the upload flow.

Key responsibilities:
- Validate input data, show clear validation messages, and handle server
  errors gracefully.
-->

<template>
  <div class="register-bg">
    <div class="register-card-centered">
      <h1 class="register-title">Create account</h1>
      <form @submit.prevent="register">
        <input v-model="name" type="text" placeholder="Name" required />
        <input v-model="email" type="email" placeholder="Email address" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button type="submit" class="primary-btn">Register</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">User created! Redirecting to login...</p>
      <div class="register-footer">
        <span>Already have an account?</span>
        <a href="#" @click.prevent="goToLogin" class="login-link">Back to Login</a>
      </div>
    </div>
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

@import url('https://fonts.googleapis.com/css2?family=Along+Sans:wght@400;700&family=Muli:wght@400;700&display=swap');

html, body {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  background: #f7f8fa !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

#app {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-bg {
  width: 100vw;
  height: 100vh;
  background: #f7f8fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-card-centered {
  width: auto;
  max-width: 410px;
  background: transparent;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(47, 55, 117, 0.07);
  padding: 2.5em 2.5em 2em 2.5em;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.7em;
}

.register-title {
  font-family: 'Along Sans', sans-serif;
  color: #232323;
  font-size: 2.1em;
  font-weight: 800;
  margin-bottom: 1.2em;
  text-align: center;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1em;
  padding: 0;
  margin: 0;
}
input[type="text"], input[type="email"], input[type="password"] {
  width: 100%;
  padding: 1em 1em;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-family: 'Muli', sans-serif;
  font-size: 1.08em;
  color: #232323;
  background: #fafbfc;
  transition: border 0.2s;
  box-sizing: border-box;
  margin: 0;
}
input[type="text"]:focus, input[type="email"]:focus, input[type="password"]:focus {
  border: 1.5px solid #2F3775;
  outline: none;
}
.primary-btn {
  width: 100%;
  padding: 1em;
  background: #2f3775;;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-family: 'Along Sans', sans-serif;
  font-weight: 700;
  font-size: 1.1em;
  margin: 0;
  box-sizing: border-box;
  cursor: pointer;
  transition: background 0.2s;
  text-align: center;
}
.primary-btn:hover {
  background: #2F3775;
}
.register-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4em;
  margin-top: 1.2em;
  font-family: 'Muli', sans-serif;
  font-size: 1em;
  color: #8b8b8b;
}
.login-link {
  color: #2F3775;
  font-weight: 700;
  text-decoration: underline;
  cursor: pointer;
}
.error {
  color: #c0392b;
  font-family: 'Muli', sans-serif;
  margin-top: 0.5em;
  text-align: center;
}
.success {
  color: green;
  font-family: 'Muli', sans-serif;
  margin-top: 0.5em;
  text-align: center;
}
</style>
