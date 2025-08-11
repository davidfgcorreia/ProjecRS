<template>
  <div class="login-card-centered">
      <img :src="logoUrl" alt="Logo" class="logo-img-big" />
      <p class="login-subtitle">Please enter your details</p>
      <h1 class="login-title">Welcome back</h1>
      <form @submit.prevent="login">
        <input v-model="email" type="email" placeholder="Email address" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <div class="login-row">
          <label class="remember-label">
            <input type="checkbox" v-model="rememberMe" /> Remember for 30 days 
          </label>
          <a href="#" class="forgot-link">Forgot password</a>
        </div>
        <button type="submit" class="primary-btn">Login</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      <div class="login-footer">
        <span>Don't have an account?</span>
        <a href="#" @click.prevent="goToRegister" class="signup-link">Sign up</a>
      </div>
      <button @click="skipLoginDev" class="dev-btn">Skip Login (Dev Only)</button>
  </div>
</template>

<script setup>
import logoUrl from '@/assets/logo.svg'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGlobalStore } from '@/stores/global'

const email = ref('')
const password = ref('')
const error = ref('')
const rememberMe = ref(false)
const router = useRouter()
const globalStore = useGlobalStore()

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
        globalStore.setUserId(user.id)
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
  globalStore.setUserId(1)
  router.push({ name: 'Upload' })
}
</script>

<style>

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

.login-card-centered {
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

.logo-img-big {
  width: 120px;
  height: 120px;
  max-width: 40vw;
  max-height: 40vh;
  display: block;
  margin: 0 auto 1.2em auto;
}
.login-subtitle {
  font-family: 'Muli', sans-serif;
  color: #8b8b8b;
  font-size: 1.08em;
  margin-bottom: 0.2em;
}
.login-title {
  font-family: 'Along Sans', sans-serif;
  color: #232323;
  font-size: 2.1em;
  font-weight: 800;
  margin-bottom: 1.2em;
}
form {
  display: flex;
  flex-direction: column;
  gap: 1em;
  padding: 0;
  margin: 0;
}
input[type="email"], input[type="password"] {
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
input[type="email"]:focus, input[type="password"]:focus {
  border: 1.5px solid #2F3775;
  outline: none;
}
.login-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5em;
}
.remember-label {
  font-family: 'Muli', sans-serif;
  font-size: 0.98em;
  color: #232323;
  display: flex;
  align-items: center;
  gap: 0.4em;
}
.forgot-link {
  font-family: 'Muli', sans-serif;
  font-size: 0.98em;
  color: #2F3775;
  text-decoration: underline;
  cursor: pointer;
}
.primary-btn {
  width: 100%;
  padding: 1em;
  background: #2f3775;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-family: 'Along Sans', sans-serif;
  font-weight: 700;
  font-size: 1.1em;
  margin-top: 0.5em;
  margin-bottom: 0.7em;
  cursor: pointer;
  transition: background 0.2s;
  text-align: center;
}
.primary-btn:hover {
  background: #2F3775;
}
.login-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4em;
  margin-top: 1.2em;
  font-family: 'Muli', sans-serif;
  font-size: 1em;
  color: #8b8b8b;
}
.signup-link {
  color: #2F3775;
  font-weight: 700;
  text-decoration: underline;
  cursor: pointer;
}
.dev-btn {
  width: 100%;
  padding: 0.5em;
  background: #fff;
  color: #3C3C3C;
  border: 1px dashed #3C3C3C;
  border-radius: 6px;
  font-family: 'Muli', sans-serif;
  font-size: 0.95em;
  margin-top: 0.5em;
  cursor: pointer;
  text-align: center;
}
.error {
  color: #c0392b;
  font-family: 'Muli', sans-serif;
  margin-top: 0.5em;
  text-align: center;
}
</style>
