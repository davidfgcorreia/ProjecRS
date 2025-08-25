<!--
ChooseTableView.vue

Purpose:
- Presents the UI where users select which extracted tables/indexes to include
  in the final dataset. Contains the stepper and table selection controls used
  during the processing flow.

Key responsibilities:
- Render selectable list of tables produced by the extraction pipeline.
- Allow users to pick indexes.

Notes:
- Keep business logic in the view's script section; UI-only helpers belong in
  small composables or services under `frontend/src/api`.
-->

<template>
  <div class="choose-table-bg">
    <LoadingScreen v-if="isSubmitting" />
    <div class="choose-table-layout">
      <div class="stepper">
        <div class="step">
          <div class="step-circle">1</div>
          <div class="step-label">Upload</div>
          <div class="step-sublabel">Upload Studies</div>
        </div>
        <svg class="step-arrow" viewBox="0 0 60 36">
          <path d="M6 18h48M40 8l14 10-14 10" stroke="#2F3775" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div class="step step-active">
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
        <div class="step">
          <div class="step-circle">4</div>
          <div class="step-label">Preview</div>
          <div class="step-sublabel">Preview and Download</div>
        </div>
      </div>
      <!-- Table options selector -->
      <div class="table-options dark-bg">
        <h3 class="title">Choose Number of Rows</h3>
        <div class="row-input-group">
          <div class="input-with-custom-arrows">
            <input
              type="number"
              v-model.number="numRows"
              min="1"
              max="20"
              id="num-rows"
              name="num-rows"
            />
            <div class="custom-arrows">
              <svg class="arrow-up" viewBox="0 0 20 20" @click="numRows = Math.min(numRows + 1, 20)">
                <path d="M5 12l5-5 5 5" stroke="#2F3775" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              </svg>
              <svg class="arrow-down" viewBox="0 0 20 20" @click="numRows = Math.max(numRows - 1, 1)">
                <path d="M5 8l5 5 5-5" stroke="#2F3775" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              </svg>
            </div>
          </div>
          <button @click="generateRows">Set Rows</button>
        </div>
      </div>
      <!-- Table preview for index input -->
      <div v-if="showTable" class="table-preview-outer">
        <div class="table-preview-dynamic center-table-preview">
          <h3 class="title">Enter Row Identifiers</h3>
          <div class="row-header-table-scroll">
            <div class="row-header-table-dynamic" :style="dynamicTableStyle">
              <div
                v-for="(row, rowIdx) in numRows"
                :key="rowIdx"
                class="header-cell-dynamic"
              >
                <input
                  class="header-row-id-input-dynamic"
                  v-model="rowIds[rowIdx]"
                  :placeholder="`Row ${rowIdx + 1} ID`"
                  :id="`row-id-${rowIdx}`"
                  :name="`row-id-${rowIdx}`"
                  autocomplete="off"
                />
              </div>
            </div>
          </div>
          <button @click="goToResult" :disabled="isSubmitting" class="submit-btn">Go to Result</button>
          <button @click="router.push({ name: 'Result', params: { count: globalStore.queryId || 1 } })" class="submit-btn dev-goto-result-btn">
            Development Go to Result
          </button>
          <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import LoadingScreen from '@/components/LoadingScreen.vue'
import { useRouter } from 'vue-router'
import { sendTableData } from '@/api/tableDataService'
import { useGlobalStore } from '@/stores/global'

const router = useRouter()
const globalStore = useGlobalStore()
const numRows = ref(2)
const rowIds = ref([])
const showTable = ref(false)
const isSubmitting = ref(false)
const errorMsg = ref('')

const minCellWidth = 220
const maxTableWidth = 1200
const minTableWidth = 400

const dynamicTableStyle = computed(() => {
  // Calculate width based on number of rows, but clamp to min/max
  const width = Math.max(
    minTableWidth,
    Math.min(numRows.value * minCellWidth, maxTableWidth)
  )
  return {
    minWidth: minTableWidth + 'px',
    width: width + 'px',
    maxWidth: maxTableWidth + 'px',
    display: 'flex',
    gap: '1.5em',
    justifyContent: 'flex-start' 
  }
})

function generateRows() {
  rowIds.value = Array(numRows.value).fill('')
  showTable.value = true
}

async function goToResult() {
  isSubmitting.value = true
  errorMsg.value = ''
  try {
    // Ensure all table fields are filled
    if (rowIds.value.some(id => !id || id.trim() === "")) {
      errorMsg.value = "All table fields must be filled."
      isSubmitting.value = false
      return
    }
    const payload = {
      query_id: String(globalStore.queryId || 1), // Ensure query_id is a string
      userid: globalStore.userId || 1,
      num_rows: numRows.value,
      row_ids: Array.from(rowIds.value)
    }
    const response = await sendTableData(payload)
    // Debug: log the API response
    // eslint-disable-next-line no-console
    console.log('DEBUG sendTableData response:', response)
    if (response && response.query_id) {
      globalStore.setQueryId(response.query_id)
    }
    router.push({ name: 'Result', params: { count: response.query_id || payload.query_id } })
  } catch (error) {
    // Show a user-friendly error if validation fails
    if (
      error?.response?.data?.detail &&
      Array.isArray(error.response.data.detail) &&
      error.response.data.detail.some(
        d => d.loc && d.loc.includes("query_id") && d.type === "string_type"
      )
    ) {
      errorMsg.value = 'All table fields must be filled or similar: query_id must be a string.'
    } else {
      let errMsg = 'Failed to submit table data.'
      if (error && error.message) {
        errMsg += '\n' + error.message
      }
      errorMsg.value = errMsg
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Along+Sans:wght@400;700&family=Muli:wght@400;700&display=swap');

.choose-table-bg {
  min-height: 100vh;
  width: 100vw;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 10vw;
}

.choose-table-layout {
  min-height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  
}

/* Stepper styles */
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

/* Table options selector */
.dark-bg {
  background: #fff;
  color: #2F3775;
  border: 1.5px solid #3C3C3C;
  box-shadow: 0 2px 12px rgba(47,55,117,0.08);
}
.table-options {
  background: #fff;
  color: #2F3775;
  box-shadow: 0 4px 24px rgba(47, 55, 117, 0.10);
  border-radius: 18px;
  margin: 3vw auto 2vw auto;
  padding: 2.5em 2.5em 2em 2.5em;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  max-width: 480px;
  min-width: 280px;
}
.title {
  color: #2F3775;
  font-size: 1.3em;
  font-weight: 600;
  margin-bottom: 1.2em;
  text-align: center;
  font-family: 'Along Sans', sans-serif;
}
.row-input-group {
  display: flex;
  gap: 1em;
  align-items: center;
  margin-bottom: 1em;
  justify-content: center;
}

/* Input with custom up/down arrows */
.input-with-custom-arrows {
  position: relative;
  display: inline-block;
}
.input-with-custom-arrows input[type="number"] {
  padding: 0.6em 2.2em 0.6em 1em;
  border: 2px solid #2F3775;
  border-radius: 7px;
  background: #f0f4fa;
  color: #2F3775;
  font-size: 1.1em;
  font-family: 'Muli', sans-serif;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
  -webkit-appearance: none;
  appearance: none;
}
.custom-arrows {
  position: absolute;
  right: 0.4em;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  height: 1.8em;
  justify-content: center;
  z-index: 2;
}
.custom-arrows svg {
  width: 1.1em;
  height: 1.1em;
  cursor: pointer;
  user-select: none;
  display: block;
}
.arrow-up {
  margin-bottom: 0.1em;
}
.arrow-down {
  margin-top: 0.1em;
}

/* Hide browser default spin buttons for all number inputs in .row-input-group */
.row-input-group input[type="number"]::-webkit-inner-spin-button,
.row-input-group input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}
.row-input-group input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}

/* Right arrow for Set Rows button */
.set-rows-btn-arrow {
  display: inline-block;
  vertical-align: middle;
  margin-left: 0.5em;
  width: 1.2em;
  height: 1.2em;
}

/* Optional: adjust button to align arrow and text */
.row-input-group button {
  display: flex;
  align-items: center;
  gap: 0.4em;
}

.row-input-group input[type="number"]:focus {
  border: 2px solid #5565A9;
  box-shadow: 0 0 0 2px #5565A933;
}
.row-input-group button {
  background: #2F3775;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 1.1em;
  font-family: 'Along Sans', sans-serif;
  font-weight: 700;
  padding: 0.6em 1.5em;
  cursor: pointer;
  transition: background 0.2s;
}
.row-input-group button:hover {
  background: #5565A9;
}

/* Dynamic Table Preview Section */
.table-preview-outer {
  display: flex;
  justify-content: center;
  width: 100%;
}
.table-preview-dynamic {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(47,55,117,0.08);
  padding: 2em 2em 1.5em 2em;
  margin: 40px auto;
  min-width: 400px;
  max-width: 1200px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2em 0 1.5em 0;
}
.row-header-table-scroll {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 1.5em;
  box-sizing: border-box;
  padding-left: 1em;
}

.row-header-table-dynamic {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: 1.5em;
  min-width: max-content;
  width: auto;
  
}
.header-cell-dynamic {
  background: #f7f8fa;
  border: 1.5px solid #2F3775;
  border-radius: 10px 10px 0 0;
  min-width: 200px;
  max-width: 260px;
  padding: 1.2em 1.2em 1em 1.2em;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center; /* Center content vertically */
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(47,55,117,0.04);
  border-bottom: 4px solid #2F3775;
  margin-left: 0;
  margin-right: 0;
}

.header-row-id-input-dynamic {
  margin: 0 auto;
  display: block;
  text-align: center;
  padding: 0.8em 0.5em;
  border: 1.5px solid #2F3775;
  border-radius: 8px;
  background: #fff;
  color: #3C3C3C;
  font-size: 1.15em;
  font-family: 'Muli', sans-serif;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
  width: 95%; /* Make input fill most of the parent for better centering */
  box-sizing: border-box;
}
.header-row-id-input-dynamic:focus {
  border: 1.5px solid #5565A9;
  box-shadow: 0 0 0 2px #5565A955;
}
.header-row-id-input-dynamic::placeholder {
  color: #888;
  opacity: 1;
}

/* Custom horizontal scrollbar */
.row-header-table-scroll::-webkit-scrollbar {
  height: 10px;
}
.row-header-table-scroll::-webkit-scrollbar-thumb {
  background: #2F3775;
  border-radius: 6px;
}
.row-header-table-scroll::-webkit-scrollbar-track {
  background: #e6eaf3;
  border-radius: 6px;
}
.row-header-table-scroll {
  scrollbar-color: #2F3775 #e6eaf3;
  scrollbar-width: thin;
}

/* Button and error styles */
.submit-btn {
  margin-top: 1.5em;
  padding: 0.8em 2.2em;
  background: #2F3775;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 1.15em;
  cursor: pointer;
  transition: background 0.2s;
  display: block;
  margin-left: auto;
  margin-right: auto;
  font-family: 'Along Sans', sans-serif;
  font-weight: 700;
}
.submit-btn:disabled {
  background: #b0b0b0;
  cursor: not-allowed;
}
.error-msg {
  color: #d32f2f;
  margin-top: 1em;
    font-weight: 500;
    text-align: center;
  }
.dev-goto-result-btn {
  margin-top: 1.2em;
}

</style>