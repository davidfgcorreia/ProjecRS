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
              @click:row="onRowClick"
              @contextmenu:row="onRowContextMenu"
            >
              <template v-for="(header, idx) in headers" #[`header.${header.value}`]="slotProps">
                <span
                  class="clickable-cell table-header-center"
                  style="user-select: text; font-weight: bold; cursor: pointer; display: flex; justify-content: center; align-items: center; position: relative;"
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
                      style="width: 18ch; min-width: 12ch; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; box-sizing: border-box; text-align: center;"
                    />
                  </template>
                  <template v-else>
                    <span style="width: 100%; text-align: center;">{{ header.title }}</span>
                  </template>
                  <!-- Always-visible merge button between headers -->
                  <template v-if="idx < headers.length - 1">
                    <button
                      class="merge-header-btn"
                      title="Merge with next column"
                      @click.stop="openMergeDialog(header.value, headers[idx+1].value)"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" style="display:block; margin:auto;" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="10.5" y="4" width="3" height="16" rx="1.5" fill="white" stroke="#2F3775" stroke-width="1.5"/>
                        <path d="M4 12h6M20 12h-6" stroke="#2F3775" stroke-width="1.5" stroke-linecap="round"/>
                        <path d="M7 9l-3 3 3 3" stroke="#2F3775" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M17 15l3-3-3-3" stroke="#2F3775" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                  </template>
                </span>
              </template>
              <template #item.col0="{ item }">
                <span
                  :class="item.__meta__ && item.__meta__.col0 ? 'clickable-cell table-cell-center' : 'table-cell-center'"
                  :title="item.__meta__ && item.__meta__.col0 ? 'Request PDF for this value' : ''"
                  @click="isEditingCell(item, 'col0') ? null : openCellMenu($event, item, 'col0')"
                  @mousedown="selectCell(item, 'col0', $event)"
                  style="user-select: text; display: flex; justify-content: center; align-items: center;"
                >
                  <template v-if="isEditingCell(item, 'col0')">
                    <textarea
                      v-model="editValue"
                      @blur="saveEdit(item, 'col0')"
                      @keydown.enter="saveEdit(item, 'col0')"
                      class="cell-edit-textarea"
                      :placeholder="'Edit value...'"
                      autofocus
                      style="width: 16ch; min-width: 16ch; min-height: 2.5em; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; resize: vertical; box-sizing: border-box; overflow-y: hidden; text-align: center;"
                    />
                  </template>
                  <template v-else>
                    <span style="width: 100%; text-align: center;">{{ (item.col0 !== undefined && item.col0 !== null && String(item.col0).trim() !== '') ? String(item.col0) : '-' }}</span>
                  </template>
                </span>
              </template>
              <template v-for="header in headers" #[`item.${header.value}`]="{ item, index }">
                <span
                  :class="'clickable-cell table-cell-center'"
                  style="user-select: text; display: flex; justify-content: center; align-items: center;"
                  @click="isEditingCell(item, header.value) ? null : openCellMenu($event, item, header.value, index)"
                  @mousedown="selectCell(item, header.value, $event)"
                >
                  <template v-if="isEditingCell(item, header.value)">
                    <textarea
                      v-model="editValue"
                      @blur="saveEdit(item, header.value)"
                      @keydown.enter="saveEdit(item, header.value)"
                      class="cell-edit-textarea"
                      :placeholder="'Edit value...'"
                      autofocus
                      style="width: 16ch; min-width: 16ch; min-height: 2.5em; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; resize: vertical; box-sizing: border-box; overflow-y: hidden; text-align: center;"
                    />
                  </template>
                  <template v-else>
                    <span style="width: 100%; text-align: center;">{{ (item[header.value] !== undefined && item[header.value] !== null && String(item[header.value]).trim() !== '') ? String(item[header.value]) : '-' }}</span>
                  </template>
                </span>
              </template>
            </v-data-table>
            <!-- Independent context menu overlay for real table -->
            <div
              v-if="cellMenu.visible"
              class="cell-menu cell-menu-absolute"
              :style="{ left: cellMenu.x + 'px', top: cellMenu.y + 'px' }"
            >
              <div v-if="cellMenu.item && cellMenu.item.__meta__ && cellMenu.item.__meta__[cellMenu.col]">
                <div class="cell-menu-option" @click.stop="localizeOrigin(cellMenu.item.__meta__[cellMenu.col], cellMenu.item)">Localize Origin</div>
                <div class="cell-menu-option" @click.stop="editCell(cellMenu.item, cellMenu.col)">Edit</div>
                <div v-if="canMergeAbove(cellMenu.rowIdx)" class="cell-menu-option" @click.stop="mergeCellAbove(cellMenu.rowIdx, cellMenu.col)">Merge cell above</div>
                <div v-if="canMergeBelow(cellMenu.rowIdx)" class="cell-menu-option" @click.stop="mergeCellBelow(cellMenu.rowIdx, cellMenu.col)">Merge cell below</div>
              </div>
              <div v-else>
                <div class="cell-menu-option" @click.stop="findValue(cellMenu.item, cellMenu.col)">Find Value</div>
                <div class="cell-menu-option" @click.stop="editCell(cellMenu.item, cellMenu.col)">Edit</div>
                <div v-if="canMergeAbove(cellMenu.rowIdx)" class="cell-menu-option" @click.stop="mergeCellAbove(cellMenu.rowIdx, cellMenu.col)">Merge cell above</div>
                <div v-if="canMergeBelow(cellMenu.rowIdx)" class="cell-menu-option" @click.stop="mergeCellBelow(cellMenu.rowIdx, cellMenu.col)">Merge cell below</div>
              </div>
            </div>
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
          class="clickable-cell table-header-center"
          style="user-select: text; font-weight: bold; cursor: pointer; display: flex; justify-content: center; align-items: center;"
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
              style="width: 18ch; min-width: 12ch; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; box-sizing: border-box; text-align: center;"
            />
          </template>
          <template v-else>
            <span style="width: 100%; text-align: center;">{{ header.title }}</span>
          </template>
        </span>
      </template>
      <template #item."col0"="{ item }">
        <span
          :class="item.__meta__ && item.__meta__.col0 ? 'clickable-cell table-cell-center' : 'table-cell-center'"
          :title="item.__meta__ && item.__meta__.col0 ? 'Request PDF for this value' : ''"
          @click="isEditingCell(item, 'col0') ? null : openCellMenu($event, item, 'col0')"
          style="user-select: text; display: flex; justify-content: center; align-items: center;"
        >
          <template v-if="isEditingCell(item, 'col0')">
            <textarea
              v-model="editValue"
              @blur="saveEdit(item, 'col0')"
              @keydown.enter="saveEdit(item, 'col0')"
              class="cell-edit-textarea"
              :placeholder="'Edit value...'"
              autofocus
              style="width: 16ch; min-width: 16ch; min-height: 2.5em; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; resize: vertical; box-sizing: border-box; overflow-y: hidden; text-align: center;"
            />
          </template>
          <template v-else>
            <span style="width: 100%; text-align: center;">{{ (item.col0 !== undefined && item.col0 !== null && String(item.col0).trim() !== '') ? String(item.col0) : '-' }}</span>
          </template>
        </span>
      </template>
      <template v-for="header in mockHeaders" #[`item.${header.value}`]="{ item }">
        <span
          class="clickable-cell table-cell-center"
          style="user-select: text; display: flex; justify-content: center; align-items: center;"
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
              style="width: 16ch; min-width: 16ch; min-height: 2.5em; font-size: 1em; border-radius: 4px; border: 1px solid #2F3775; padding: 0.2em 0.5em; resize: vertical; box-sizing: border-box; overflow-y: hidden; text-align: center;"
            />
          </template>
          <template v-else>
            <span style="width: 100%; text-align: center;">{{ (item[header.value] !== undefined && item[header.value] !== null && String(item[header.value]).trim() !== '') ? String(item[header.value]) : '-' }}</span>
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
    <div v-if="showMergeDialog" class="merge-dialog-bg">
      <div class="merge-dialog-card">
        <h3>Merge Columns</h3>
        <p>Are you sure you want to merge <b>{{ mergeCol1 }}</b> and <b>{{ mergeCol2 }}</b>?</p>
        <div v-if="mergeError" class="error-msg">{{ mergeError }}</div>
        <button @click="confirmMergeColumns" class="submit-btn">Merge</button>
        <button @click="closeMergeDialog" class="submit-btn" style="background:#b0b0b0; color:#2F3775;">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Cell selection handler for table cells
function selectCell(item, col, event) {
  // You can implement custom cell selection logic here
  // For now, just log the selection for debug
  // eslint-disable-next-line no-console
  console.log('Cell selected:', { item, col, event })
}
// Row event handlers for table
function onRowClick(row) {
  // Row click handler (stub)
  // You can implement custom logic here if needed
}

function onRowContextMenu(row, event) {
  // Row context menu handler (stub)
  // You can implement custom logic here if needed
  event.preventDefault();
}
import { ref, onMounted, computed,onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTableData } from '@/api/tableDataService'
import { getHighlightedPdfSection } from '@/api/localizationService'
import { getHighlightedHeaderPdf } from '@/api/highlightHeaderService'
import { mergeTableColumns } from '@/api/tableDataService'
import { mergeCellApi } from '@/api/mergeCellService'
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
  },
  {
    col0: { display: 'Smith 2022', meta: null },
    col1: { display: '2022', meta: 'loc_215' },
    col2: { display: 'NCT04567890', meta: 'loc_216' },
    col3: { display: 'II', meta: 'loc_217' },
    col4: { display: 'United States', meta: 'loc_218' },
    col5: { display: 'Topical steroids, oral antihistamines', meta: 'loc_219' },
    col6: { display: 'Baricitinib', meta: 'loc_221' },
    col7: { display: '2 mg, q.d', meta: 'loc_223' },
    col8: { display: '150', meta: 'loc_227' },
    col9: { display: 'Placebo', meta: 'loc_228' },
    col10: { display: '0 mg', meta: 'loc_230' },
    col11: { display: '148', meta: 'loc_232' },
    col12: { display: '12', meta: 'loc_234' }
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
// Cell editing state
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

function openCellMenu(event, item, col, index) {
  event.stopPropagation()
  // Use pageX/pageY for absolute positioning
  cellMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    item,
    col,
    rowIdx: index
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
  // Get queryId and userId
  // Try to get queryId from route.params.query_id or route.params.count
  let queryId = route.params.query_id || route.params.count
  // Try to get userId from globalStore, fallback to localStorage if needed
  let userId = globalStore && globalStore.user ? globalStore.user.id : null
  if (!userId && window.localStorage) {
    const userObj = window.localStorage.getItem('user')
    if (userObj) {
      try {
        userId = JSON.parse(userObj).id
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Failed to parse user from localStorage:', e)
      }
    }
  }
  // Fallback to userId=2 if still not present
  if (!userId) {
    userId = 2
    // eslint-disable-next-line no-console
    console.log('[DEBUG] No user found, falling back to userId=2')
  }
  const marker = meta
  // Debug log for parameters
  // eslint-disable-next-line no-console
  console.log('[DEBUG] localizeOrigin params:', { queryId, userId, marker, routeParams: route.params, globalStoreUser: globalStore && globalStore.user })
  if (!queryId || !userId || !marker) {
    // eslint-disable-next-line no-console
    console.error('[DEBUG] Missing queryId, userId, or marker for localization API call', { queryId, userId, marker })
    return
  }
  // Show loading overlay while fetching PDF
  showPdfOverlay.value = true
  pdfOverlayValue.value = cellMenu.value.item[cellMenu.value.col]
  pdfOverlayOriginalValue.value = pdfOverlayValue.value
  pdfOverlayItem.value = cellMenu.value.item
  pdfOverlayCol.value = cellMenu.value.col
  pdfOverlaySrc.value = ''
  closeCellMenu()
  // Call backend API to get highlighted PDF
  getHighlightedPdfSection(queryId, userId, marker)
    .then(blob => {
      // Debug log for API response
      // eslint-disable-next-line no-console
      console.log('[DEBUG] getHighlightedPdfSection response:', blob)
      // Create a blob URL for the PDF
      const pdfUrl = URL.createObjectURL(blob)
      pdfOverlaySrc.value = pdfUrl
    })
    .catch(err => {
      // eslint-disable-next-line no-console
      console.error('[DEBUG] Failed to fetch highlighted PDF:', err)
      pdfOverlaySrc.value = ''
      showPdfOverlay.value = false
      // Optionally show error message to user
    })
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
  // Get queryId from route
  let queryId = route.params.query_id || route.params.count
  // Get header name from headers (for real table) or mockHeaders
  let headerName = ''
  if (headers.value && Array.isArray(headers.value)) {
    const headerObj = headers.value.find(h => h.value === col)
    headerName = headerObj ? headerObj.title : col
  } else {
    const headerObj = mockHeaders.find(h => h.value === col)
    headerName = headerObj ? headerObj.title : col
  }
  // Collect all first column values
  let itemsArr = items.value && Array.isArray(items.value) ? items.value : mockItemsDisplay.value
  let col0Values = itemsArr.map((r, idx) => {
    let val = r && r.col0
    // Debug log for each value being copied
    if (val && typeof val === 'object' && 'display' in val) {
      // eslint-disable-next-line no-console
      console.log(`[DEBUG] col0Values[${idx}] (object.display):`, val.display)
      return val.display
    }
    // eslint-disable-next-line no-console
    console.log(`[DEBUG] col0Values[${idx}] (raw):`, val)
    return val
  })
  // Find the first non-empty value in col0, starting from selected row and going up
  // Debug log for itemsArr and row
  // eslint-disable-next-line no-console
  console.log('[DEBUG] itemsArr:', itemsArr)
  // eslint-disable-next-line no-console
  console.log('[DEBUG] row:', row)
  let startIdx = itemsArr.findIndex(r => r === row) + 1
  // eslint-disable-next-line no-console
  console.log(`[DEBUG] startIdx for selected row:`, startIdx)
  let pdfName = ''
  if (startIdx === -1) {
    // eslint-disable-next-line no-console
    console.warn('[DEBUG] startIdx is -1, row not found in itemsArr. Skipping PDF name search.')
  } else {
    for (let i = startIdx; i >= 0; i--) {
      let val = col0Values[i]
      // Debug log for each value being looked at
      // eslint-disable-next-line no-console
      console.log(`[DEBUG] Looking at col0Values[${i}]:`, val)
      if (val !== undefined && val !== null && String(val).trim() !== '') {
        pdfName = String(val).trim()
        // eslint-disable-next-line no-console
        console.log(`[DEBUG] Selected pdfName from col0Values[${i}]:`, pdfName)
        break
      }
    }
  }
  // eslint-disable-next-line no-console
  console.log(`[DEBUG] Final pdfName after search:`, pdfName)
  // Debug log for parameters
  // eslint-disable-next-line no-console
  console.log('[DEBUG] findValue params:', { queryId, headerName, col, row, pdfName })
  if (!queryId || !headerName || !pdfName) {
    // eslint-disable-next-line no-console
    console.error('[DEBUG] Missing queryId, headerName, or pdfName for highlight header API call', { queryId, headerName, pdfName })
    return
  }
  showPdfOverlay.value = true
  pdfOverlayValue.value = row[col]
  pdfOverlayOriginalValue.value = row[col]
  pdfOverlayItem.value = row
  pdfOverlayCol.value = col
  pdfOverlaySrc.value = ''
  closeCellMenu()
  // Call backend API to get highlighted header PDF
  getHighlightedHeaderPdf(queryId, headerName, pdfName)
    .then(blob => {
      // eslint-disable-next-line no-console
      console.log('[DEBUG] getHighlightedHeaderPdf response:', blob)
      const pdfUrl = URL.createObjectURL(blob)
      pdfOverlaySrc.value = pdfUrl
    })
    .catch(err => {
      // eslint-disable-next-line no-console
      console.error('[DEBUG] Failed to fetch highlighted header PDF:', err)
      pdfOverlaySrc.value = ''
      showPdfOverlay.value = false
    })
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
    const oldValue = item[col]
    item[col] = editValue.value
    // Send API request to backend if value changed
    if (editValue.value !== oldValue) {
      // Prepare cell identification
      let queryId = route.params.query_id || route.params.count
      // Always use row index for backend update
      let rowIdx = items.value && Array.isArray(items.value) ? items.value.findIndex(r => r === item) : null
      // Prepare payload
      const payload = {
        query_id: queryId,
        row_id: rowIdx,
        col: col,
        new_value: editValue.value
      }
      // eslint-disable-next-line no-console
      console.log('Sending cell update to backend:', payload)
      import('@/api/tableDataService').then(module => {
        if (module && module.updateTableCell) {
          module.updateTableCell(payload)
            .then(res => {
              // eslint-disable-next-line no-console
              console.log('Cell update response:', res)
            })
            .catch(err => {
              // eslint-disable-next-line no-console
              console.error('Cell update error:', err)
            })
        } else {
          // eslint-disable-next-line no-console
          console.warn('updateTableCell API not found in tableDataService')
        }
      })
    }
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


const showMergeDialog = ref(false)
const mergeCol1 = ref(null)
const mergeCol2 = ref(null)
const mergeError = ref('')
function openMergeDialog(col1, col2) {
  mergeCol1.value = col1
  mergeCol2.value = col2
  showMergeDialog.value = true
  mergeError.value = ''
}
function closeMergeDialog() {
  showMergeDialog.value = false
  mergeCol1.value = null
  mergeCol2.value = null
  mergeError.value = ''
}
async function confirmMergeColumns() {
  if (!mergeCol1.value || !mergeCol2.value) return
  const queryId = route.params.query_id || route.params.count
  try {
    const updatedTable = await mergeTableColumns({ query_id: queryId, col1: mergeCol1.value, col2: mergeCol2.value })
    table.value = updatedTable
    closeMergeDialog()
  } catch (e) {
    mergeError.value = e.message || 'Failed to merge columns.'
  }
}

// Helper functions for menu options
function canMergeAbove(rowIdx) {
  return rowIdx > 0;
}
function canMergeBelow(rowIdx) {
  let itemsArr = items.value && Array.isArray(items.value) ? items.value : mockItemsDisplay.value;
  return rowIdx < itemsArr.length - 1;
}
async function mergeCellAbove(rowIdx, col) {
  if (!canMergeAbove(rowIdx)) return;
  let itemsArr = items.value && Array.isArray(items.value) ? items.value : mockItemsDisplay.value;
  let queryId = route.params.query_id || route.params.count;
  try {
    const result = await mergeCellApi({
      query_id: queryId,
      col_key: col,
      row_idx1: rowIdx,
      row_idx2: rowIdx - 1
    });
    if (result && result.columns_content) {
      table.value = result;
    }
    // For mock table, update locally
    if (!table.value && itemsArr === mockItemsDisplay.value) {
      const base = itemsArr[rowIdx];
      const target = itemsArr[rowIdx - 1];
      const mergedDisplay = (base[col] === target[col]) ? base[col] : `${base[col]} / ${target[col]}`;
      base[col] = mergedDisplay;
      target[col] = '';
    }
    closeCellMenu();
  } catch (e) {
    mergeError.value = e.message || 'Failed to merge cells.';
    closeCellMenu();
  }
}
async function mergeCellBelow(rowIdx, col) {
  let itemsArr = items.value && Array.isArray(items.value) ? items.value : mockItemsDisplay.value;
  if (!canMergeBelow(rowIdx)) return;
  let queryId = route.params.query_id || route.params.count;
  try {
    const result = await mergeCellApi({
      query_id: queryId,
      col_key: col,
      row_idx1: rowIdx,
      row_idx2: rowIdx + 1
    });
    if (result && result.columns_content) {
      table.value = result;
    }
    // For mock table, update locally
    if (!table.value && itemsArr === mockItemsDisplay.value) {
      const base = itemsArr[rowIdx];
      const target = itemsArr[rowIdx + 1];
      const mergedDisplay = (base[col] === target[col]) ? base[col] : `${base[col]} / ${target[col]}`;
      base[col] = mergedDisplay;
      target[col] = '';
    }
    closeCellMenu();
  } catch (e) {
    mergeError.value = e.message || 'Failed to merge cells.';
    closeCellMenu();
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
      // Debug: log the API response
      // eslint-disable-next-line no-console
      console.log('DEBUG API table response:', table.value)
      if (table.value && table.value.columns_content) {
        // eslint-disable-next-line no-console
        console.log('DEBUG API columns_content:', table.value.columns_content)
      }
    } catch (e) {
      errorMsg.value = 'Failed to load table data.'
      // eslint-disable-next-line no-console
      console.error('DEBUG API error:', e)
    } finally {
      loading.value = false
    }

    loading.value = false
  }
})

const headers = computed(() => {
  let result = []
  if (table.value) {
    let headerValues = []
    if (table.value.column_titles && Array.isArray(table.value.column_titles)) {
      headerValues = table.value.column_titles
    } else if (table.value.row_ids && Array.isArray(table.value.row_ids)) {
      headerValues = table.value.row_ids
    }
    if (Array.isArray(table.value.columns_content) && table.value.columns_content.length > 0) {
      const firstRow = table.value.columns_content[0]
      const allKeys = Object.keys(firstRow)
      result = []
      if (allKeys.length > 0) {
        result.push({ value: allKeys[0], title: 'File' })
          for (let idx = 1; idx < allKeys.length; idx++) {
            // Shift headerValues by one: col1 gets headerValues[0], col2 gets headerValues[1], ...
            result.push({ value: allKeys[idx], title: headerValues[idx - 1] || allKeys[idx] })
          }
      }
    }
  }
  // eslint-disable-next-line no-console
  console.log('DEBUG computed headers:', result)
  return result
})

const items = computed(() => {
  if (table.value && Array.isArray(table.value.columns_content)) {
    // Get all column keys from headers
    const allKeys = headers.value.map(h => h.value)
    const result = table.value.columns_content.map(rowObj => {
      const displayRow = { __meta__: {} }
      for (const key of allKeys) {
        const cell = rowObj[key]
        if (cell && typeof cell === 'object' && 'display' in cell) {
          displayRow[key] = cell.display
          displayRow.__meta__[key] = cell.meta
        } else if (cell !== undefined && cell !== null) {
          displayRow[key] = cell
          displayRow.__meta__[key] = null
        } else {
          displayRow[key] = ''
          displayRow.__meta__[key] = null
        }
      }
      // eslint-disable-next-line no-console
      console.log('DEBUG computed displayRow:', displayRow)
      return displayRow
    })
    // eslint-disable-next-line no-console
    console.log('DEBUG computed items:', result)
    return result
  }
  return []
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Along+Sans:wght@400;700&family=Muli:wght@400;700&display=swap');
/* Center table header and cell values */
.table-header-center {
  justify-content: center !important;
  align-items: center !important;
  text-align: center !important;
  position: relative;
  padding-right: 28px; /* Space for merge button */
}
.table-cell-center {
  justify-content: center !important;
  align-items: center !important;
  text-align: center !important;
}

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

/* Merge button styles */
.merge-header-btn {
  right: -0.8em;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: 1.5px solid #2F3775;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  box-shadow: 0 1px 4px rgba(47,55,117,0.08);
  cursor: pointer;
  z-index: 10;
  transition: background 0.2s, border-color 0.2s;
}
.merge-header-btn:hover {
  background: #e6eaf3;
  border-color: #1a1e3a;
}

/* Merge dialog styles */
.merge-dialog-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(47, 55, 117, 0.7);
  z-index: 4000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.merge-dialog-card {
  background: #fff;
  border: 2px solid #2F3775;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(47, 55, 117, 0.15);
  padding: 2em 2.5em;
  max-width: 400px;
  width: 90%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.merge-dialog-card h3 {
  color: #2F3775;
  font-size: 1.4em;
  font-weight: 700;
  margin-bottom: 0.8em;
  text-align: center;
  font-family: 'Along Sans', sans-serif;
}
.merge-dialog-card p {
  color: #2F3775;
  font-size: 1.1em;
  margin-bottom: 1.5em;
  text-align: center;
}
.merge-dialog-card .submit-btn {
  width: 100%;
  padding: 0.8em 0;
  background: #2F3775;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 1.15em;
  cursor: pointer;
  transition: background 0.2s;
  display: block;
  margin-bottom: 1em;
  font-family: 'Along Sans', sans-serif;
  font-weight: 700;
}
.merge-dialog-card .submit-btn:last-child {
  background: #b0b0b0;
  color: #2F3775;
}
.merge-dialog-card .error-msg {
  color: #d32f2f;
  margin-top: 0.5em;
  font-weight: 500;
  text-align: center;
}
</style>