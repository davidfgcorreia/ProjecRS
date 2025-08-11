<template>
  <div class="upload-bg">
    <div class="upload-layout">
      <div class="stepper">
        <div class="step step-active">
          <div class="step-circle">1</div>
          <div class="step-label">Upload</div>
          <div class="step-sublabel">Upload Studies</div>
        </div>
        <svg class="step-arrow" viewBox="0 0 60 36"><path d="M6 18h48M40 8l14 10-14 10" stroke="#3887f6" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div class="step">
          <div class="step-circle">2</div>
          <div class="step-label">Select</div>
          <div class="step-sublabel">Choose Indexes</div>
        </div>
        <svg class="step-arrow" viewBox="0 0 60 36"><path d="M6 18h48M40 8l14 10-14 10" stroke="#3887f6" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div class="step">
          <div class="step-circle">3</div>
          <div class="step-label">Validate</div>
          <div class="step-sublabel">Fix Errors</div>
        </div>
        <svg class="step-arrow" viewBox="0 0 60 36"><path d="M6 18h48M40 8l14 10-14 10" stroke="#3887f6" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <div class="step">
          <div class="step-circle">4</div>
          <div class="step-label">Preview</div>
          <div class="step-sublabel">Preview and Download</div>
        </div>
      </div>
      <div class="upload-card-centered">
        <div class="upload-header">
          <span class="upload-icon" aria-label="Upload">
            <svg width="2em" height="2em" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 16V4M12 4L7 9M12 4l5 5" stroke="#2F3775" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
              <rect x="4" y="16" width="16" height="4" rx="1.5" fill="#2F3775" fill-opacity="0.12"/>
            </svg>
          </span>
          <button class="report-btn" @click.prevent="error = 'Report issue clicked!'">&#9888; REPORT ISSUE</button>
        </div>
        <div class="dropzone" @dragover.prevent @drop.prevent="onDrop" @click="triggerFileInput">
          <input ref="fileInput" type="file" multiple accept="application/pdf" @change="handleFiles" class="file-input-hidden" />
          <div class="dropzone-content">
            <span class="dropzone-cloud">&#9729;&#65039;</span>
            <div class="dropzone-text">Drag & Drop PDF files to import</div>
            <button class="import-btn" @click.stop="triggerFileInput">IMPORT FROM <span style="font-size:1.2em;vertical-align:middle;">&#9776;</span></button>
          </div>
        </div>
        <ul class="file-list">
          <li v-for="file in files" :key="file.name">{{ file.name }}</li>
        </ul>
        <div class="upload-footer">
          <span>Maximum upload file size: <b>128 MB</b>.</span>
        </div>
        <button class="primary-btn" :disabled="!files.length" @click="uploadFiles">Upload and Next: Choose Table</button>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">Files uploaded!</p>
      </div>
      <!-- TEMPORARY: Button to go to next page for testing -->
      <button class="primary-btn" style="margin-top:2vw;background:#5565A9;" @click="router.push({ name: 'ChooseTable' })">
        TEMP: Go to Next Page
      </button>
    </div>
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
const fileInput = ref(null)

function handleFiles(event) {
  files.value = Array.from(event.target.files)
}

function triggerFileInput() {
  fileInput.value && fileInput.value.click()
}

function onDrop(e) {
  if (e.dataTransfer && e.dataTransfer.files) {
    files.value = Array.from(e.dataTransfer.files)
  }
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

.upload-bg {
  width: 100vw;
  height: 100vh;
  background: #f7f8fa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 5vw;
}

.upload-card-centered {
  width: 90vw;
  max-width: 1000px;
  min-width: 320px;
  background: #fff;
  border: 0.15vw solid #e0e0e0;
  border-radius: 1.5vw;
  box-shadow: 0 0.2vw 1.2vw rgba(47, 55, 117, 0.07);
  padding: 1.2vw 2vw 0.7vw 2vw;
  display: flex;
  flex-direction: column;
  gap: 0.7vw;
}

.upload-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1vw;
}
.upload-icon {
  font-size: 2vw;
  margin-right: 1vw;
  color: #2F3775;
}
.upload-title {
  font-family: 'Along Sans', sans-serif;
  color: #2F3775;
  font-size: 2vw;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.report-btn {
  background: #fff;
  color: #c0392b;
  border: 0.2vw solid #c0392b;
  border-radius: 1vw;
  font-family: 'Muli', sans-serif;
  font-size: 1.1vw;
  font-weight: 600;
  padding: 0.5vw 2vw;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.report-btn:hover {
  background: #ffeaea;
}

.dropzone {
  border: 0.3vw dashed #5565A9;
  border-radius: 2vw;
  background: #f0f4fa;
  min-height: 7vw;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-bottom: 1vw;
  position: relative;
  transition: border-color 0.2s;
}
.dropzone:hover {
  border-color: #2F3775;
}
.file-input-hidden {
  display: none;
}
.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}
.dropzone-cloud {
  font-size: 4vw;
  color: #5565A9;
  margin-bottom: 1vw;
}
.dropzone-text {
  color: #3C3C3C;
  font-family: 'Muli', sans-serif;
  font-size: 1.5vw;
  margin-bottom: 1vw;
}
.import-btn {
  background: #fff;
  color: #2F3775;
  border: 0.2vw solid #2F3775;
  border-radius: 1vw;
  font-family: 'Muli', sans-serif;
  font-size: 1.2vw;
  font-weight: 600;
  padding: 0.7vw 2vw;
  cursor: pointer;
  margin-bottom: 0.5vw;
  transition: background 0.2s, color 0.2s;
}
.import-btn:hover {
  background: #eaf3ff;
}

.file-list {
  margin: 1vw 0 1vw 0;
  padding: 0;
  list-style: none;
  font-family: 'Muli', sans-serif;
  font-size: 1.1vw;
  color: #3C3C3C;
}
.file-list li {
  margin-bottom: 0.5vw;
}

.upload-footer {
  margin-top: 0.5vw;
  font-family: 'Muli', sans-serif;
  font-size: 1vw;
  color: #3C3C3C;
  display: flex;
  flex-direction: column;
  gap: 0.5vw;
}
.upload-links {
  display: flex;
  align-items: center;
  gap: 1vw;
}
.howto-link {
  color: #5565A9;
  text-decoration: underline;
  font-size: 1vw;
  cursor: pointer;
}
.get-unlimited-btn {
  background: #fff;
  color: #5565A9;
  border: 0.2vw solid #5565A9;
  border-radius: 1vw;
  font-family: 'Muli', sans-serif;
  font-size: 1vw;
  font-weight: 600;
  padding: 0.3vw 1vw;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.get-unlimited-btn:hover {
  background: #eaf3ff;
}

.primary-btn {
  width: 100%;
  padding: 1.2vw;
  background: #2F3775;
  color: #fff;
  border: none;
  border-radius: 1vw;
  font-family: 'Along Sans', sans-serif;
  font-weight: 700;
  font-size: 1.3vw;
  margin: 1vw 0 0 0;
  box-sizing: border-box;
  cursor: pointer;
  transition: background 0.2s;
  text-align: center;
}
.primary-btn:disabled {
  background: #b3cdfa;
  cursor: not-allowed;
}
.primary-btn:hover:enabled {
  background: #5565A9;
}
.error {
  color: #c0392b;
  font-family: 'Muli', sans-serif;
  margin-top: 0.5em;
  text-align: center;
}
.success {
  color: #1a7f3c;
  font-family: 'Muli', sans-serif;
  margin-top: 0.5em;
  text-align: center;
}

/* Stepper styles */
.stepper {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  width: 90vw;
  max-width: 1000px;
  min-width: 320px;
  margin: 2vw auto 2vw auto;
  padding: 0 1vw;
  background: none;
  box-sizing: border-box;
  z-index: 2;
}
.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1 1 0;
  min-width: 0;
  position: relative;
  opacity: 1;
}
.step-label {
  font-family: 'Muli', sans-serif;
  font-size: 1vw;
  font-weight: 700;
  color: #2F3775;
  margin-bottom: 0.1vw;
  text-align: center;
  letter-spacing: 0.01em;
}
.step-sublabel {
  font-family: 'Muli', sans-serif;
  font-size: 0.9vw;
  color: #5565A9;
  text-align: center;
  margin-top: 0.1vw;
}
.step-line, .step-line-vertical {
  flex: 0 0 4vw;
  height: 3px;
  background: #2F3775;
  align-self: center;
  margin: 0 0.5vw;
  margin-top: 1vw;
  border-radius: 2px;
  width: 100%;
}
.step-circle {
  width: 2.8vw;
  height: 2.8vw;
  min-width: 38px;
  min-height: 38px;
  max-width: 48px;
  max-height: 48px;
  background: #f0f4fa;
  color: #2F3775;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Muli', sans-serif;
  font-size: 1.3vw;
  font-weight: 700;
  margin-bottom: 0.5vw;
  border: 3px solid #2F3775;
  box-shadow: 0 2px 8px 0 rgba(47,55,117,0.06);
  transition: background 0.2s, color 0.2s, border 0.2s;
}
.step.step-active .step-circle {
  background: #2F3775;
  color: #fff;
  border: 3px solid #2F3775;
}
.step.step-active .step-label {
  color: #2F3775;
  font-size: 1.15vw;
}
.step.step-active .step-sublabel {
  color: #5565A9;
  font-weight: 600;
}

/* Update arrow styles for larger size and palette */
.step-arrow {
  width: 4vw;
  height: 2vw;
  min-width: 48px;
  min-height: 24px;
  max-width: 80px;
  max-height: 40px;
  margin: 0 0.3vw;
  vertical-align: middle;
  display: inline-block;
}
.step-arrow path {
  stroke: #2F3775;
}

@media (max-width: 600px) {
  .upload-card-centered {
    padding: 1vw 1vw 0.5vw 1vw;
    border-radius: 3vw;
    gap: 0.7vw;
  }
  .upload-title {
    font-size: 4vw;
  }
  .report-btn, .import-btn, .get-unlimited-btn {
    font-size: 3vw;
    padding: 1vw 2vw;
    border-radius: 2vw;
  }
  .dropzone {
    min-height: 10vw;
    border-radius: 3vw;
  }
  .stepper {
    flex-direction: column;
    align-items: stretch;
    gap: 2vw;
    margin-bottom: 2vw;
  }
  .step-line {
    width: 100%;
    height: 2px;
    margin: 0.5vw 0;
    flex: none;
  }
  .step-circle {
    width: 9vw;
    height: 9vw;
    font-size: 4vw;
    min-width: 32px;
    min-height: 32px;
    max-width: 48px;
    max-height: 48px;
  }
  .step-label {
    font-size: 3.5vw;
  }
  .step-sublabel {
    font-size: 2.2vw;
  }
  .dropzone-cloud {
    font-size: 8vw;
  }
  .dropzone-text {
    font-size: 3vw;
  }
  .primary-btn {
    font-size: 3vw;
    padding: 2vw;
    border-radius: 2vw;
  }
  .file-list {
    font-size: 2vw;
  }
  .upload-footer, .howto-link, .get-unlimited-btn {
    font-size: 2vw;
  }
}
</style>
