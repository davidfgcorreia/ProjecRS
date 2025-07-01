<template>
  <div class="table-options">
    <h3>Choose Number of Columns</h3>
    <input type="number" v-model.number="numColumns" min="1" max="10" />
    <button @click="generateTable">Generate Table</button>
  </div>
  <div v-if="showTable" class="table-preview">
    <h3>Select Column Titles</h3>
    <table>
      <tbody>
        <tr>
          <th v-for="(col, idx) in numColumns" :key="idx">
            <input v-model="columnTitles[idx]" :placeholder="`Column ${idx + 1}`" />
          </th>
        </tr>
        <tr>
          <td v-for="(col, idx) in numColumns" :key="idx">...</td>
        </tr>
      </tbody>
    </table>
    <button @click="goToResult">Go to Result</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const numColumns = ref(3)
const columnTitles = ref([])
const showTable = ref(false)

function generateTable() {
  if (numColumns.value > 0) {
    columnTitles.value = Array(numColumns.value).fill('')
    showTable.value = true
  }
}

function goToResult() {
  router.push({ name: 'Result' })
}
</script>

<style scoped>
.table-options, .table-preview { max-width: 600px; margin: 30px auto; padding: 1em; border: 1px solid #ccc; border-radius: 8px; }
table { width: 100%; border-collapse: collapse; margin-top: 1em; }
th, td { border: 1px solid #ddd; padding: 0.5em; text-align: center; }
input[type="number"] { width: 60px; }
</style>
