<template>
  <div class="result-container">
    <h2>Upload Result</h2>
    <div v-if="result">
      <p>Query ID: {{ result.query_id }}</p>
      <p>User ID: {{ result.user_id }}</p>
      <p>Query Date: {{ result.query_date }}</p>
      <ul>
        <li v-for="file in result.files" :key="file.id">File: {{ file.filename }}</li>
      </ul>
      <p>Report: {{ result.report }}</p>
    </div>
    <div v-else>
      <p>No result loaded.</p>
    </div>
    <router-link to="/upload">Back to Upload</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const result = ref(null)

onMounted(async () => {
  const queryId = route.params.count // or get from another param
  if (queryId) {
    const response = await fetch(`http://localhost:8000/result/${queryId}`)
    if (response.ok) {
      result.value = await response.json()
    }
  }
})
</script>

<style scoped>
.result-container { max-width: 400px; margin: 40px auto; padding: 2em; border: 1px solid #eee; border-radius: 8px; }
</style>
