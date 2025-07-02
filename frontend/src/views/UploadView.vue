<template>
  <div class="upload-container">
    <h2>Upload PDF Files</h2>
    <input type="file" multiple accept="application/pdf" @change="handleFiles" />
    <ul>
      <li v-for="file in files" :key="file.name">{{ file.name }}</li>
    </ul>
    <button :disabled="!files.length" @click="uploadFiles">Upload and Next: Choose Table</button>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">Files uploaded!</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadPdf } from '../api/upload'
import { useGlobalStore } from '@/stores/global'

const files = ref([])
const error = ref('')
const success = ref(false)
const router = useRouter()
const globalStore = useGlobalStore()

function handleFiles(event) {
  files.value = Array.from(event.target.files)
}

async function uploadFiles() {
  error.value = ''
  success.value = false
  const userId = globalStore.userId || localStorage.getItem('user_id')
  if (!userId) {
    error.value = 'User not logged in.'
    return
  }
  try {
    let firstQueryId = null
    for (const file of files.value) {
      const res = await uploadPdf(file, userId)
      if (res && res.query_id && !firstQueryId) {
        firstQueryId = res.query_id
        globalStore.setQueryId(firstQueryId)
      }
    }
    success.value = true
    router.push({ name: 'ChooseTable' })
  } catch (err) {
    error.value = err.message || 'Upload failed'
  }
}
</script>

<style scoped>
.upload-container { max-width: 400px; margin: 40px auto; padding: 2em; border: 1px solid #eee; border-radius: 8px; }
ul { margin: 1em 0; }
.error { color: red; }
.success { color: green; }
</style>
