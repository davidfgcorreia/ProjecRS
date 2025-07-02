<template>
  <div class="result-container">
    <h2>Upload Result</h2>
    <div v-if="loading" class="loading-screen">
      <div class="spinner"></div>
      <p>Loading table data...</p>
    </div>
    <div v-else-if="table">
      <h3>Table</h3>
      <EasyDataTable :headers="headers" :items="items" />
      <button disabled title="PDF download temporarily unavailable">Download as PDF</button>
    </div>
    <div v-else-if="errorMsg">
      <p style="color:red">{{ errorMsg }}</p>
    </div>
    <router-link to="/upload">Back to Upload</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getTableData } from '@/api/tableDataService'
import EasyDataTable from 'vue3-easy-data-table'
import 'vue3-easy-data-table/dist/style.css'

const route = useRoute()
const table = ref(null)
const errorMsg = ref('')
const loading = ref(true)

onMounted(async () => {
  const queryId = route.params.count
  if (queryId) {
    try {
      loading.value = true
      table.value = await getTableData(queryId)
    } catch (e) {
      errorMsg.value = 'Failed to load table data.'
    } finally {
      loading.value = false
    }
  } else {
    errorMsg.value = 'No query ID provided.'
    loading.value = false
  }
})

const headers = computed(() => {
  if (table.value) {
    if (table.value.column_titles && Array.isArray(table.value.column_titles)) {
      return table.value.column_titles.map((title, idx) => ({
        text: title,
        value: `col${idx}`
      }))
    } else if (table.value.row_ids && Array.isArray(table.value.row_ids)) {
      return table.value.row_ids.map((id, idx) => ({
        text: id,
        value: `col${idx}`
      }))
    }
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
</script>

<style scoped>
.result-container {
  max-width: 700px;
  margin: 40px auto;
  padding: 2em;
  border: 1px solid #23272a;
  border-radius: 18px;
  background: #181a1b;
  color: #e0e0e0;
}

.loading-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.spinner {
  border: 6px solid #23272a;
  border-top: 6px solid #1976d2;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
  margin-bottom: 1em;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Force EasyDataTable to use a true dark mode */
.easy-data-table,
.easy-data-table__main,
.easy-data-table__footer,
.easy-data-table__pagination {
  background: #181a1b !important;
  color: #e0e0e0 !important;
  border: none !important;
}
.easy-data-table thead th,
.easy-data-table__header {
  background: #23272a !important;
  color: #90caf9 !important;
  border-bottom: 2px solid #1976d2 !important;
  font-weight: 600;
}
.easy-data-table tbody td,
.easy-data-table__cell {
  background: #181a1b !important;
  color: #e0e0e0 !important;
  border-top: 1px solid #23272a !important;
}
.easy-data-table tbody tr:nth-child(even) td {
  background: #20232a !important;
}
.easy-data-table__button,
.easy-data-table__pagination__item {
  background: #23272a !important;
  color: #90caf9 !important;
  border-radius: 6px;
  border: 1px solid #1976d2 !important;
  transition: background 0.2s;
}
.easy-data-table__button:hover,
.easy-data-table__pagination__item:hover {
  background: #1976d2 !important;
  color: #fff !important;
}
.easy-data-table__pagination__item--active {
  background: #1976d2 !important;
  color: #fff !important;
}
.easy-data-table__row--selected {
  background: #263043 !important;
}
</style>