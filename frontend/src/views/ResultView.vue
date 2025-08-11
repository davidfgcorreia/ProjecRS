<template>
  <div class="result-bg">
    <div class="result-layout">
      <!-- Stepper -->
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
        <div class="step step-active">
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
      <!-- Result Card -->
      <div class="result-card dark-bg">
        <h2 class="title">Upload Result</h2>
        <div v-if="loading" class="loading-screen">
          <div class="spinner"></div>
          <p>Loading table data...</p>
        </div>
        <div v-else-if="table" class="result-table-outer">
          <div class="result-table-inner">
            <h3 class="subtitle">Table</h3>
            <v-data-table
              :headers="headers"
              :items="items"
              class="elevation-1"
              item-key="col0"
              dense
              hide-default-footer
            >
              <template v-for="header in headers" #[`header.${header.value}`]="slotProps">
                <span
                  class="clickable-cell"
                  style="user-select: text; font-weight: bold; cursor: pointer;"
                  @click="headerEditKey === header.value ? null : setHeaderEdit(header.value)"
                >
                  <template v-if="headerEditKey === header.value">
                    <input
                      v-model="editHeaderValue"
                      @blur="saveHeaderEdit(header.value)"
                      @keydown.enter="saveHeaderEdit(header.value)"
                      class="cell-edit-textarea"
                      :placeholder="'Edit header...'"
                      autofocus
                      style="width: 18ch; min-width: 12ch; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; box-sizing: border-box;"
                    />
                  </template>
                  <template v-else>
                    {{ header.title }}
                  </template>
                </span>
              </template>
<template #item="{ item, headers }">
  <tr>
    <td v-for="header in headers" :key="header.value">
      <span
        class="clickable-cell"
        style="user-select: text;"
        @mousedown="selectCell(item, header.value, $event)"
      >
        <template v-if="isEditingCell(item, header.value)">
          <textarea
            v-model="editValue"
            @blur="onCellEditBlur(item, header.value)"
            @keydown.enter="saveEdit(item, header.value)"
            class="cell-edit-textarea"
            :placeholder="'Edit value...'"
            autofocus
            style="width: 16ch; min-width: 16ch; min-height: 2.5em; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; resize: vertical; box-sizing: border-box; overflow-y: hidden;"
          />
        </template>
        <template v-else>
          {{ (item[header.value] !== undefined && item[header.value] !== null && String(item[header.value]).trim() !== '') ? String(item[header.value]) : '-' }}
        </template>
      </span>
    </td>
  </tr>
</template>
            </v-data-table>
            <button @click="goToPreview" class="submit-btn" style="margin-top:1.5em;">Go to Preview</button>
          </div>
        </div>
        <div v-else-if="showMockTable" class="result-table-outer">
          <div class="result-table-inner">
            <h3 class="subtitle">Mock Table (Development)</h3>
            <div v-if="errorMsg" class="error-msg" style="margin-bottom:1em;">{{ errorMsg }}<br/>Showing mock table for development.</div>
    <v-data-table
      :headers="mockHeaders"
      :items="mockItemsDisplay"
      class="elevation-1"
      item-key="col0"
      dense
      hide-default-footer
    >
      <template v-for="header in mockHeaders" #[`header.${header.value}`]="slotProps">
        <span
          class="clickable-cell"
          style="user-select: text; font-weight: bold; cursor: pointer;"
          @click="headerEditKey === header.value ? null : setHeaderEdit(header.value)"
        >
          <template v-if="headerEditKey === header.value">
            <input
              v-model="editHeaderValue"
              @blur="saveHeaderEdit(header.value)"
              @keydown.enter="saveHeaderEdit(header.value)"
              class="cell-edit-textarea"
              :placeholder="'Edit header...'"
              autofocus
              style="width: 18ch; min-width: 12ch; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; box-sizing: border-box;"
            />
          </template>
          <template v-else>
            {{ header.title }}
          </template>
        </span>
      </template>
      <template #item."col0"="{ item }">
        <span
          :class="item.__meta__ && item.__meta__.col0 ? 'clickable-cell' : ''"
          :title="item.__meta__ && item.__meta__.col0 ? 'Request PDF for this value' : ''"
          @click="isEditingCell(item, 'col0') ? null : openCellMenu($event, item, 'col0')"
          style="user-select: text;"
        >
          <template v-if="isEditingCell(item, 'col0')">
            <textarea
              v-model="editValue"
              @blur="saveEdit(item, 'col0')"
              @keydown.enter="saveEdit(item, 'col0')"
              class="cell-edit-textarea"
              :placeholder="'Edit value...'"
              autofocus
              style="width: 16ch; min-width: 16ch; min-height: 2.5em; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; resize: vertical; box-sizing: border-box; overflow-y: hidden;"
            />
          </template>
          <template v-else>
            {{ (item.col0 !== undefined && item.col0 !== null && String(item.col0).trim() !== '') ? String(item.col0) : '-' }}
          </template>
        </span>
      </template>
      <template v-for="header in mockHeaders" #[`item.${header.value}`]="{ item }">
        <span
          class="clickable-cell"
          style="user-select: text;"
          @click="isEditingCell(item, header.value) ? null : openCellMenu($event, item, header.value)"
        >
          <template v-if="isEditingCell(item, header.value)">
            <textarea
              v-model="editValue"
              @blur="saveEdit(item, header.value)"
              @keydown.enter="saveEdit(item, header.value)"
              class="cell-edit-textarea"
              :placeholder="'Edit value...'"
              autofocus
              style="width: 16ch; min-width: 16ch; min-height: 2.5em; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; resize: vertical; box-sizing: border-box; overflow-y: hidden;"
            />
          </template>
          <template v-else>
            {{ (item[header.value] !== undefined && item[header.value] !== null && String(item[header.value]).trim() !== '') ? String(item[header.value]) : '-' }}
          </template>
        </span>
      </template>
    </v-data-table>
    <button @click="goToPreview" class="submit-btn" style="margin-top:1.5em;">Go to Preview</button>
    <!-- Independent context menu overlay -->
    <div
      v-if="cellMenu.visible"
      class="cell-menu cell-menu-absolute"
      :style="{ left: cellMenu.x + 'px', top: cellMenu.y + 'px' }"
    >
      <template v-if="cellMenu.item && cellMenu.item.__meta__ && cellMenu.item.__meta__[cellMenu.col]">
        <div class="cell-menu-option" @click.stop="localizeOrigin(cellMenu.item.__meta__[cellMenu.col], cellMenu.item)">Localize Origin</div>
        <div class="cell-menu-option" @click.stop="editCell(cellMenu.item, cellMenu.col)">Edit</div>
      </template>
      <template v-else>
        <div class="cell-menu-option" @click.stop="findValue(cellMenu.item, cellMenu.col)">Find Value</div>
        <div class="cell-menu-option" @click.stop="editCell(cellMenu.item, cellMenu.col)">Edit</div>
      </template>
    </div>
          </div>
        </div>
        <router-link to="/upload" class="back-link">Back to Upload</router-link>
      </div>
    </div>
    <!-- PDF overlay UI -->
    <div v-if="showPdfOverlay" class="pdf-overlay-bg">
      <div class="pdf-overlay-card-full">
        <iframe :src="pdfOverlaySrc" class="pdf-overlay-pdf-full" frameborder="0"></iframe>
        <div class="pdf-overlay-bottom-box">
          <textarea
            v-model="pdfOverlayValue"
            class="pdf-overlay-value-edit"
            :placeholder="'Edit value...'"
            autofocus
            @blur="savePdfOverlayValue"
            @keydown.enter="savePdfOverlayValue"
          />
          <button class="pdf-overlay-close" @click="showPdfOverlay = false">&times;</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed,onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTableData } from '@/api/tableDataService'
import { requestPdf } from '@/api/pdfService'
import { useGlobalStore } from '@/stores/global'

const route = useRoute()
const router = useRouter()
function goToPreview() {
  router.push('/preview')
}
const table = ref(null)
const errorMsg = ref('')
const loading = ref(true)

// Mock data for development (from merged_columns_table.md, with metadata)
const mockHeaders = [
  { value: 'col0', title: 'File' },
  { value: 'col1', title: 'Year of publication' },
  { value: 'col2', title: 'RCT identifer' },
  { value: 'col3', title: 'RCT phase' },
  { value: 'col4', title: 'Region' },
  { value: 'col5', title: 'Background Therapy' },
  { value: 'col6', title: 'Intervention-name' },
  { value: 'col7', title: 'Intervention-dosage/Intervention-frequency' },
  { value: 'col8', title: 'Intervention-sample-size' },
  { value: 'col9', title: 'Comparator-name' },
  { value: 'col10', title: 'Comparator-dosage/Comparator-frequency' },
  { value: 'col11', title: 'Comparator-sample-size' },
  { value: 'col12', title: 'Followup-weeks' }
]
const mockItems = [
  {
    col0: { display: 'Bieber 2021', meta: null },
    col1: { display: '2021', meta: 'loc_115' },
    col2: { display: 'NCT03422822', meta: 'loc_116' },
    col3: { display: 'III', meta: 'loc_117' },
    col4: { display: 'Australia and countries across North and South America, Europe, and Asia', meta: 'loc_118' },
    col5: { display: 'Emollients, low- or medium-potency topical glucocorticoids, topical calcineurin inhibitors, topical phosphodiesterase 4 inhibitors', meta: 'loc_119' },
    col6: { display: 'Abrocitinib', meta: 'loc_121' },
    col7: { display: '100 mg, q.d', meta: 'loc_123' },
    col8: { display: '238', meta: 'loc_127' },
    col9: { display: 'Dupilumab', meta: 'loc_128' },
    col10: { display: '300 mg, q2w', meta: 'loc_130' },
    col11: { display: '242', meta: 'loc_132' },
    col12: { display: '16', meta: 'loc_134' }
  }
]

const globalStore = useGlobalStore ? useGlobalStore() : null

const showMockTable = computed(() => {
  // Show mock table if no real table is available (either no queryId or error loading table)
  return (!table.value && !loading.value)
})

// Flatten mockItems for display: ensure all columns are present for every row
const mockItemsDisplay = computed(() => {
  // Get all column keys from mockHeaders
  const allKeys = mockHeaders.map(h => h.value)
  // Debug: log the original mockItems and headers
  // eslint-disable-next-line no-console
  console.log('DEBUG mockHeaders:', mockHeaders)
  // eslint-disable-next-line no-console
  console.log('DEBUG mockItems:', mockItems)
  const result = mockItems.map(row => {
    const displayRow = { __meta__: {} }
    for (const key of allKeys) {
      const val = row[key]
      if (val && typeof val === 'object' && 'display' in val) {
        displayRow[key] = val.display
        displayRow.__meta__[key] = val.meta
      } else if (val !== undefined && val !== null) {
        displayRow[key] = val
        displayRow.__meta__[key] = null
      } else {
        displayRow[key] = ''
        displayRow.__meta__[key] = null
      }
    }
    // Debug: log each converted row
    // eslint-disable-next-line no-console
    console.log('DEBUG converted row:', displayRow)
    return displayRow
  })
  // eslint-disable-next-line no-console
  console.log('DEBUG mockItemsDisplay:', result)
  return result
})



// Context menu state
import { nextTick } from 'vue'
const cellMenu = ref({ visible: false, x: 0, y: 0, item: null, col: null })
const editingCellKey = ref(null)
const editValue = ref('')
const headerEditKey = ref(null)
const editHeaderValue = ref('')
// Temporary PDF storage in browser memory
const tempPdfStorage = ref({})

// UI state for PDF overlay
const showPdfOverlay = ref(false)
const pdfOverlayValue = ref('')
const pdfOverlaySrc = ref('')
const pdfOverlayOriginalValue = ref('')

function setHeaderEdit(col) {
  headerEditKey.value = col
  const headerObj = headers.value.find(h => h.value === col) || mockHeaders.find(h => h.value === col)
  if (headerObj) {
    editHeaderValue.value = headerObj.title
  }
  // Delay adding the click listener to avoid immediate close
  nextTick(() => {
    setTimeout(() => {
      document.addEventListener('click', handleHeaderEditOutsideClick)
    }, 0)
  })
}

function handleHeaderEditOutsideClick(event) {
  // Only close if click is outside the input
  const input = document.querySelector('.cell-edit-textarea')
  if (input && !input.contains(event.target)) {
    saveHeaderEdit(headerEditKey.value)
  }
}

function saveHeaderEdit(col) {
  const headerObj = headers.value.find(h => h.value === col) || mockHeaders.find(h => h.value === col)
  if (headerObj && editHeaderValue.value !== undefined && editHeaderValue.value !== null) {
    headerObj.title = editHeaderValue.value
    // Optionally, trigger an API call to persist header changes here
    // eslint-disable-next-line no-console
    console.log('Header updated:', col, editHeaderValue.value)
  }
  headerEditKey.value = null
  document.removeEventListener('click', handleHeaderEditOutsideClick)
}

function getCellKey(item, col) {
  // Use a unique key for each cell (row id + col)
  return (item.col0 || JSON.stringify(item)) + ':' + col
}

function openCellMenu(event, item, col) {
  event.stopPropagation()
  // Use pageX/pageY for absolute positioning
  cellMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    item,
    col
  }
  nextTick(() => {
    document.addEventListener('click', closeCellMenu)
  })
}
function closeCellMenu() {
  cellMenu.value.visible = false
  cellMenu.value.item = null
  cellMenu.value.col = null
  document.removeEventListener('click', closeCellMenu)
}

function localizeOrigin(meta, row) {
  // For development, show overlay with mock PDF and cell value
  pdfOverlaySrc.value = '/public/development/mock.pdf'
  let cellValue = ''
  if (cellMenu.value && cellMenu.value.item && cellMenu.value.col) {
    cellValue = cellMenu.value.item[cellMenu.value.col]
  }
  pdfOverlayValue.value = cellValue
  pdfOverlayOriginalValue.value = cellValue
  // Store reference to the item and col for saving
  pdfOverlayItem.value = cellMenu.value.item
  pdfOverlayCol.value = cellMenu.value.col
  showPdfOverlay.value = true
  closeCellMenu()
}
// Store reference to the item and col for saving overlay edits
const pdfOverlayItem = ref(null)
const pdfOverlayCol = ref(null)

function savePdfOverlayValue() {
  // Only save if value changed
  if (
    pdfOverlayItem.value &&
    pdfOverlayCol.value &&
    pdfOverlayValue.value !== pdfOverlayOriginalValue.value
  ) {
    pdfOverlayItem.value[pdfOverlayCol.value] = pdfOverlayValue.value
    pdfOverlayOriginalValue.value = pdfOverlayValue.value
    // Optionally, trigger an API call to persist changes here
    // eslint-disable-next-line no-console
    console.log('PDF overlay value saved:', pdfOverlayCol.value, pdfOverlayValue.value)
  }
}
function findValue(row, col) {
  // TODO: Replace with API request for PDF localization
  pdfOverlaySrc.value = '/public/development/mock.pdf'
  let cellValue = ''
  if (row && col) {
    cellValue = row[col]
  }
  pdfOverlayValue.value = cellValue
  pdfOverlayOriginalValue.value = cellValue
  pdfOverlayItem.value = row
  pdfOverlayCol.value = col
  showPdfOverlay.value = true
  closeCellMenu()
}
function editCell(item, col) {
  // Start editing the cell using a unique key
  editingCellKey.value = getCellKey(item, col)
  editValue.value = item[col]
  nextTick(() => adjustTextareaHeight())
  closeCellMenu()
}

function isEditingCell(item, col) {
  return editingCellKey.value === getCellKey(item, col)
}

function saveEdit(item, col) {
  // Save the new value to the cell
  if (editValue.value !== undefined && editValue.value !== null) {
    item[col] = editValue.value
    // Placeholder for API call to update cell value
    // TODO: implement real API call here
    // eslint-disable-next-line no-console
    console.log('API call to update cell', col, 'with value', editValue.value, 'in row', item)
  }
  editingCellKey.value = null
}

function adjustTextareaHeight() {
  // Find the textarea and set its height to fit content
  const textarea = document.querySelector('.cell-edit-textarea')
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = textarea.scrollHeight + 'px'
  }
}

// Watch editValue and adjust height dynamically
import { watch } from 'vue'
watch(editValue, () => {
  adjustTextareaHeight()
})

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
    errorMsg.value = ''
    loading.value = false
  }
})

const headers = computed(() => {
  if (table.value) {
    if (table.value.column_titles && Array.isArray(table.value.column_titles)) {
      return table.value.column_titles.map((title, idx) => ({
        value: `col${idx}`,
        title: title
      }))
    } else if (table.value.row_ids && Array.isArray(table.value.row_ids)) {
      return table.value.row_ids.map((id, idx) => ({
        value: `col${idx}`,
        title: id
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
@import url('https://fonts.googleapis.com/css2?family=Along+Sans:wght@400;700&family=Muli:wght@400;700&display=swap');

.result-bg {
  min-height: 100vh;
  width: 100vw;
  background: #f7f8fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding-top: 10vw;
}

.result-layout {
  min-height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Stepper styles (copied from ChooseTableView for consistency) */
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

/* Card styles */
.result-card.dark-bg {
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
  max-width: 1200px;
  min-width: 400px;
  width: 100%;
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

.result-table-outer {
  display: flex;
  justify-content: center;
  width: 100%;
}
.result-table-inner {
  width: 100%;
  max-width: 1200px;
}

.loading-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}
.spinner {
  border: 6px solid #e6eaf3;
  border-top: 6px solid #2F3775;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
  margin-bottom: 1em;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* EasyDataTable dark-on-light override */
.easy-data-table,
.easy-data-table__main,
.easy-data-table__footer,
.easy-data-table__pagination {
  background: #fff !important;
  color: #2F3775 !important;
  border: none !important;
}
.easy-data-table thead th,
.easy-data-table__header {
  background: #f0f4fa !important;
  color: #2F3775 !important;
  border-bottom: 2px solid #2F3775 !important;
  font-weight: 600;
}
.easy-data-table tbody td,
.easy-data-table__cell {
  background: #fff !important;
  color: #2F3775 !important;
  border-top: 1px solid #e6eaf3 !important;
}
.easy-data-table tbody tr:nth-child(even) td {
  background: #f7f8fa !important;
}
.easy-data-table__button,
.easy-data-table__pagination__item {
  background: #f0f4fa !important;
  color: #2F3775 !important;
  border-radius: 6px;
  border: 1.5px solid #2F3775 !important;
  transition: background 0.2s;
}
.easy-data-table__button:hover,
.easy-data-table__pagination__item:hover {
  background: #2F3775 !important;
  color: #fff !important;
}
.easy-data-table__pagination__item--active {
  background: #2F3775 !important;
  color: #fff !important;
}
.easy-data-table__row--selected {
  background: #e6eaf3 !important;
}

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
.clickable-cell {
  cursor: pointer;
  color: inherit;
  text-decoration: none;
  transition: color 0.15s;
  outline: none !important;
  position: relative;
}
.clickable-cell:focus {
  outline: none !important;
}
.clickable-cell:hover {
  color: inherit;
}
.cell-menu {
  position: absolute;
  z-index: 2000;
  min-width: 140px;
  background: #fff;
  border: 1.5px solid #2F3775;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(47,55,117,0.13);
  padding: 0.3em 0;
  font-family: 'Muli', sans-serif;
  overflow: visible;
}
.cell-menu-absolute {
  position: fixed;
  pointer-events: auto;
}
.cell-menu-option {
  padding: 0.5em 1.2em;
  color: #2F3775;
  font-size: 1em;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  border-radius: 5px;
}
.cell-menu-option:hover {
  background: #f0f4fa;
  color: #0d47a1;
}
.cell-edit-textarea {
  font-family: 'Muli', sans-serif;
  font-size: 1em;
  color: #2F3775;
  background: #f7f8fa;
  border: 1px solid #2F3775;
  border-radius: 4px;
  padding: 0.2em 0.5em;
  outline: none;
  width: 16ch;
  min-width: 16ch;
  min-height: 2.5em;
  resize: vertical;
  box-sizing: border-box;
  overflow-y: hidden;
}
.cell-edit-textarea:focus {
  border-color: #0d47a1;
  background: #fff;
}

/* PDF overlay styles */
.pdf-overlay-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(47, 55, 117, 0.18);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.pdf-overlay-card-full {
  background: #fff;
  border: 2.5px solid #2F3775;
  border-radius: 0;
  box-shadow: none;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
/* PDF overlay bottom box styles */
.pdf-overlay-bottom-box {
  position: absolute;
  right: 2.5em;
  bottom: 2.5em;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  background: rgba(255,255,255,0.98);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(47,55,117,0.13);
  padding: 1.2em 1.5em 1.2em 1.2em;
  z-index: 3100;
}
.pdf-overlay-value-edit {
  font-size: 1.1em;
  font-weight: 600;
  color: #2F3775;
  background: #f7f8fa;
  border: 2px solid #2F3775;
  border-radius: 8px;
  padding: 0.5em 1em;
  margin-right: 1em;
  resize: vertical;
  outline: none;
  min-width: 22ch;
  min-height: 2.5em;
  box-sizing: border-box;
}
.pdf-overlay-value-edit:focus {
  border-color: #0d47a1;
  background: #fff;
}
.pdf-overlay-close {
  background: none;
  border: none;
  font-size: 2em;
  color: #2F3775;
  cursor: pointer;
  font-weight: bold;
  margin-left: 1em;
  margin-bottom: 0.2em;
}
.pdf-overlay-pdf-full {
  width: 100vw;
  height: 100vh;
  border-radius: 0;
  border: none;
  margin: 0;
  background: #f7f8fa;
}
</style>