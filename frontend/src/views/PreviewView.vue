<template>
  <div class="preview-bg">
    <div class="stepper">
      <div class="step">
        <div class="step-circle">1</div>
        <div class="step-label">Upload</div>
        <div class="step-sublabel">Upload Studies</div>
      </div>
      <svg class="step-arrow" viewBox="0 0 60 36">
        <path d="M6 18h48M40 8l14 10-14 10" stroke="#2F3775" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div class="step">
        <div class="step-circle">2</div>
        <div class="step-label">Select</div>
        <div class="step-sublabel">Choose Indexes</div>
      </div>
      <svg class="step-arrow" viewBox="0 0 60 36">
        <path d="M6 18h48M40 8l14 10-14 10" stroke="#2F3775" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div class="step">
        <div class="step-circle">3</div>
        <div class="step-label">Validate</div>
        <div class="step-sublabel">Fix Errors</div>
      </div>
      <svg class="step-arrow" viewBox="0 0 60 36">
        <path d="M6 18h48M40 8l14 10-14 10" stroke="#2F3775" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div class="step step-active">
        <div class="step-circle">4</div>
        <div class="step-label">Preview</div>
        <div class="step-sublabel">Preview and Download</div>
      </div>
    </div>
    <div class="preview-layout">
      <div class="preview-controls-row">
        <div class="preview-controls google-sheets-bar full-width-bar">
          <label for="format-select" class="format-label">Download format:</label>
          <select id="format-select" v-model="selectedFormat" class="format-select">
            <option value="csv">CSV</option>
            <option value="xlsx">Excel</option>
            <option value="pdf">PDF</option>
            <option value="md">Markdown</option>
          </select>
          <span class="icon-placeholder download-icon" title="Download" @click="download(selectedFormat)">
            <svg width="36" height="36" viewBox="0 0 100 100" fill="none">
              <circle cx="50" cy="50" r="48" fill="#2546a8"/>
              <rect x="30" y="70" width="40" height="8" rx="2" fill="#fff"/>
              <rect x="46" y="25" width="8" height="40" rx="2" fill="#fff"/>
              <polygon points="35,55 50,70 65,55" fill="#fff"/>
            </svg>
          </span>
          <div class="icon-group">
            <span class="icon-placeholder" title="File options"><svg width="22" height="22" fill="none" stroke="#5565A9" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18"/></svg></span>
            <span class="icon-placeholder" title="Refresh"><svg width="22" height="22" fill="none" stroke="#5565A9" stroke-width="2" viewBox="0 0 24 24"><path d="M4 4v6h6"/><path d="M20 20v-6h-6"/><path d="M5 19A9 9 0 0 1 19 5"/></svg></span>
            <span class="icon-placeholder" title="Share"><svg width="22" height="22" fill="none" stroke="#5565A9" stroke-width="2" viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98"/><path d="M15.41 6.51l-6.82 3.98"/></svg></span>
          </div>
        </div>
      </div>
      <div v-if="loading" class="loading-screen">
        <div class="spinner"></div>
        <p>Loading table data...</p>
      </div>
      <div v-else>
        <div class="preview-table-section">
          <!-- TODO: Replace with API table data -->
          <table class="simple-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Role</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>1</td>
                <td>Alice Smith</td>
                <td>alice.smith@example.com</td>
                <td>Active</td>
                <td>Admin</td>
                <td>2025-08-01</td>
              </tr>
              <tr>
                <td>2</td>
                <td>Bob Johnson</td>
                <td>bob.johnson@example.com</td>
                <td>Inactive</td>
                <td>User</td>
                <td>2025-07-15</td>
              </tr>
              <tr>
                <td>3</td>
                <td>Carol Lee</td>
                <td>carol.lee@example.com</td>
                <td>Active</td>
                <td>Editor</td>
                <td>2025-07-20</td>
              </tr>
              <tr>
                <td>4</td>
                <td>David Kim</td>
                <td>david.kim@example.com</td>
                <td>Pending</td>
                <td>Viewer</td>
                <td>2025-08-03</td>
              </tr>
              <tr>
                <td>5</td>
                <td>Eva Brown</td>
                <td>eva.brown@example.com</td>
                <td>Active</td>
                <td>User</td>
                <td>2025-08-05</td>
              </tr>
              <tr>
                <td>6</td>
                <td>Frank White</td>
                <td>frank.white@example.com</td>
                <td>Inactive</td>
                <td>Admin</td>
                <td>2025-07-10</td>
              </tr>
              <tr>
                <td>7</td>
                <td>Grace Green</td>
                <td>grace.green@example.com</td>
                <td>Active</td>
                <td>Editor</td>
                <td>2025-08-06</td>
              </tr>
              <tr>
                <td>8</td>
                <td>Henry Black</td>
                <td>henry.black@example.com</td>
                <td>Pending</td>
                <td>User</td>
                <td>2025-08-02</td>
              </tr>
              <tr>
                <td>9</td>
                <td>Ivy Blue</td>
                <td>ivy.blue@example.com</td>
                <td>Active</td>
                <td>Viewer</td>
                <td>2025-07-30</td>
              </tr>
              <tr>
                <td>10</td>
                <td>Jack Red</td>
                <td>jack.red@example.com</td>
                <td>Inactive</td>
                <td>User</td>
                <td>2025-07-25</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-description-field">
          <label class="description-label">Table Description:</label>
          <div class="description-content">
            {{ tableDescription }}
          </div>
        </div>
        <div class="action-buttons">
          <a href="#" class="back-link" @click.prevent="goBack">Back</a>
          <button class="upload-btn" @click="goToUpload">Go to Upload Page</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTableData } from '@/api/tableDataService'
import { downloadTableFile } from '@/api/tableDownloadService'

const route = useRoute()
const router = useRouter()
const table = ref(null)
const loading = ref(true)
const selectedFormat = ref('csv')
const tableDescription = ref('This table lists 10 users with their names, emails, account status, roles, and creation dates. It provides a quick overview of user activity and access levels in the system.')

function goBack() {
  router.back()
}

function goToUpload() {
  router.push({ name: 'Upload' })
}

onMounted(async () => {
  // You can pass queryId via route or global store
  const queryId = route.params.count
  if (queryId) {
    try {
      loading.value = true
      table.value = await getTableData(queryId)
    } catch (e) {
      // handle error
    } finally {
      loading.value = false
    }
  } else {
    loading.value = false
  }
})

const headers = computed(() => {
  if (table.value && table.value.column_titles) {
    return table.value.column_titles.map((title, idx) => ({ value: `col${idx}`, title }))
  }
  return []
})
const items = computed(() => {
  if (table.value && Array.isArray(table.value.columns_content)) {
    return table.value.columns_content.map(rowArr => {
      const rowObj = {}
      rowArr.forEach((cell, idx) => {
        rowObj[`col${idx}`] = cell
      })
      return rowObj
    })
  }
  return []
})

async function download(format) {
  try {
    await downloadTableFile(format, table.value)
  } catch (e) {
    alert('Download failed.')
  }
}
</script>

<style scoped>
.preview-bg {
  min-height: 100vh;
  width: 100vw;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 28vw;
  padding-bottom: 5vw;
}
.stepper {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  width: 100%;
  max-width: 1200px;
  min-width: 320px;
  margin: 2vw auto 2vw auto;
  background: none;
  box-sizing: border-box;
  z-index: 2;
  position: relative;
  top: 0;
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
.preview-layout {
  min-height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}
.title {
  color: #2F3775;
  font-size: 1.5em;
  font-weight: 700;
  margin-bottom: 1.2em;
  text-align: center;
  font-family: 'Along Sans', sans-serif;
}
.subtitle {
  color: #2F3775;
  font-size: 1.2em;
  font-weight: 600;
  margin-bottom: 1em;
  text-align: center;
  font-family: 'Along Sans', sans-serif;
}
.download-section {
  margin-top: 2em;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.download-btn {
  margin-left: -0.1em; /* Adjusts horizontal position */
  margin-top: 0.4em; /* Moves icon slightly down */
  font-size: 2em;
  color: #2546a8;
  cursor: pointer;
  vertical-align: middle;
  transition: filter 0.2s;
  font-family: 'Along Sans', sans-serif;
  font-weight: 700;
}
.download-btn:hover {
  background: #5565A9;
}
.simple-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}
.simple-table th, .simple-table td {
  border: 1px solid #e6eaf3;
  padding: 0.7em 1em;
  text-align: left;
  font-size: 1em;
  color: #222;
}
.simple-table th {
  background: #f0f4fa;
  color: #222;
  font-weight: 600;
}
.simple-table tr:nth-child(even) td {
  background: #f7f8fa;
}
.back-link {
  margin-top: 2em;
  color: #2F3775;
  font-weight: 600;
  text-decoration: underline;
  font-family: 'Muli', sans-serif;
  font-size: 1.1em;
  display: block;
  text-align: center;
}
/* Aligns the controls row to the top left below the stepper */
.preview-controls-row {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  margin-bottom: 1.5em;
}
.preview-controls {
  display: flex;
  align-items: center;
  gap: 0.4em;
  margin-left: 0;
}
/* Google Sheets style top bar for controls */
.google-sheets-bar {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(47,55,117,0.06);
  padding: 0.7em 1.5em;
  margin-top: 1em;
  margin-bottom: 1.5em;
  min-width: 320px;
  max-width: 600px;
  display: flex;
  align-items: center;
  gap: 0.4em;
}
/* Google Sheets style top bar for controls - full width */
.full-width-bar {
  width: 100%;
  min-width: unset;
  max-width: unset;
  border-radius: 0;
  box-shadow: none;
  background: #f0f4fa;
  padding: 1em 2vw;
  margin-top: 0.5em;
  margin-bottom: 2em;
  display: flex;
  align-items: center;
  border-bottom: 1.5px solid #e6eaf3;
  justify-content: space-between;
}
.format-label {
  font-weight: 600;
  color: #2F3775;
  margin-right: 0.5em;
  font-size: 1.1em;
}
.format-select {
  padding: 0.5em 1.2em;
  border-radius: 5px;
  border: 1px solid #e6eaf3;
  font-size: 1.05em;
  background: #fff;
  color: #2F3775;
  font-family: 'Muli', sans-serif;
  font-weight: 600;
  margin-right: 0.3em;
}
.icon-group {
  display: flex;
  align-items: center;
  gap: 1em;
  margin-left: auto;
}
.icon-placeholder {
  font-size: 1.3em;
  color: #5565A9;
  margin-left: 0.5em;
  cursor: pointer;
  transition: color 0.2s;
}
.icon-placeholder:hover {
  color: #2F3775;
}
.download-icon {
  margin-left: -0.1em; /* Adjusts horizontal position */
  margin-top: 0.4em; /* Moves icon slightly down */
  font-size: 2em;
  color: #2546a8;
  cursor: pointer;
  vertical-align: middle;
  transition: filter 0.2s;
}
/* Table description field styling */
.table-description-field {
  margin: 2em 0 1em 0;
  padding: 1em 1.5em;
  background: #f0f4fa;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(47,55,117,0.06);
  max-width: 700px;
  width: 100%;
  font-family: 'Muli', sans-serif;
}
.description-label {
  font-weight: 700;
  color: #2F3775;
  font-size: 1.1em;
  margin-bottom: 0.5em;
  display: block;
}
.description-content {
  color: #222;
  font-size: 1em;
  margin-top: 0.2em;
}
.action-buttons {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 2em;
  margin-top: 2em;
}
.upload-btn {
  background: #2F3775;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 1.1em;
  font-family: 'Muli', sans-serif;
  font-weight: 700;
  padding: 0.8em 2.2em;
  cursor: pointer;
  transition: background 0.2s;
}
.upload-btn:hover {
  background: #5565A9;
}

.download-icon:hover {
  filter: brightness(1.2);
}
</style>
