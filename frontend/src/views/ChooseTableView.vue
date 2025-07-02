<template>
  <div class="table-options dark-bg">
    <h3 class="title">Choose Number of Rows</h3>
    <div class="row-input-group">
      <input type="number" v-model.number="numRows" min="1" max="20" id="num-rows" name="num-rows" />
      <button @click="generateRows">Set Rows</button>
    </div>
  </div>
  <div v-if="showTable" class="table-preview-outer">
    <div class="table-preview dark-bg center-table-preview" :style="dynamicTableStyle">
      <h3 class="title">Enter Row Identifiers</h3>
      <div class="row-header-table-wrapper">
        <table class="row-header-table">
          <thead>
            <tr>
              <th v-for="(row, rowIdx) in numRows" :key="rowIdx" class="header-cell">
                <input
                  class="header-row-id-input"
                  v-model="rowIds[rowIdx]"
                  :placeholder="`Row ${rowIdx + 1} ID`"
                  :id="`row-id-${rowIdx}`"
                  :name="`row-id-${rowIdx}`"
                  autocomplete="off"
                />
              </th>
            </tr>
          </thead>
        </table>
      </div>
      <button @click="goToResult" :disabled="isSubmitting" class="submit-btn">Go to Result</button>
      <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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

const maxTableWidth = 1200
const minTableWidth = 700
const colWidth = 140
const dynamicTableStyle = computed(() => {
  let width = minTableWidth
  if (numRows.value > 4) {
    width = Math.min(minTableWidth + (numRows.value - 4) * colWidth, maxTableWidth)
  }
  return {
    maxWidth: width + 'px',
    width: '100%'
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
    const payload = {
      query_id: globalStore.queryId || 1,
      userid: globalStore.userId || 1,
      num_rows: numRows.value,
      row_ids: Array.from(rowIds.value)
    }
    console.log('Submitting payload:', payload)
    const response = await sendTableData(payload)
    // Store the correct query_id from backend response
    if (response && response.query_id) {
      globalStore.setQueryId(response.query_id)
    }
    router.push({ name: 'Result', params: { count: response.query_id || payload.query_id } })
  } catch (error) {
    let errMsg = 'Failed to submit table data.'
    if (error && error.message) {
      errMsg += '\n' + error.message
    }
    errorMsg.value = errMsg
    console.error('Error in goToResult:', error, error?.stack || error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
body {
  background: #181a1b;
}
.dark-bg {
  background: #181a1b;
  color: #e0e0e0;
  border: 1.5px solid #23272a;
  box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}
.table-options, .table-preview {
  max-width: 700px;
  margin: 40px auto;
  padding: 2em 2em 1.5em 2em;
  border-radius: 14px;
}
.title {
  color: #e0e0e0;
  font-size: 1.3em;
  font-weight: 600;
  margin-bottom: 1.2em;
  text-align: center;
}
.row-input-group {
  display: flex;
  gap: 1em;
  align-items: center;
  margin-bottom: 1em;
  justify-content: center;
}
.row-header-table-wrapper {
  overflow-x: auto;
  margin-bottom: 1.5em;
}
.row-header-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 0.5em;
  background: transparent;
}
.header-cell {
  background: #23272a;
  border-radius: 8px 8px 0 0;
  border: 2px solid #23272a;
  border-bottom: 3px solid #1976d2;
  padding: 1.1em 1.2em 0.7em 1.2em;
  min-width: 120px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
}
.header-row-id-input {
  width: 100%;
  padding: 0.7em 0.5em;
  border: 1.5px solid #1976d2;
  border-radius: 6px;
  background: #181a1b;
  color: #e0e0e0;
  font-size: 1em;
  text-align: center;
  outline: none;
  transition: border 0.2s;
}
.header-row-id-input:focus {
  border: 1.5px solid #42a5f5;
}
.header-row-id-input::placeholder {
  color: #888;
  opacity: 1;
}
.submit-btn {
  margin-top: 1.5em;
  padding: 0.8em 2.2em;
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 1.15em;
  cursor: pointer;
  transition: background 0.2s;
  display: block;
  margin-left: auto;
  margin-right: auto;
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
.table-preview-outer {
  display: flex;
  justify-content: center;
  width: 100%;
}
.center-table-preview {
  margin-left: auto;
  margin-right: auto;
  display: block;
}
</style>
