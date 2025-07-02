import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('global', {
  state: () => ({
    userId: null,
    queryId: null,
  }),
  actions: {
    setUserId(id) {
      this.userId = id
    },
    setQueryId(id) {
      this.queryId = id
    },
    clear() {
      this.userId = null
      this.queryId = null
    }
  }
})
