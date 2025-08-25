/**
 * Global Pinia store
 *
 * Purpose:
 * - Hold small app-wide state used across multiple views/components.
 * - Currently stores the authenticated `userId` and the active `queryId`.
 *
 * State shape:
 * - userId: string|null — current user identifier
 * - queryId: string|null — currently selected query/table identifier
 *
 * Actions:
 * - setUserId(id)    — set the current user id
 * - setQueryId(id)   — set the active query id
 * - clear()          — reset both values to null
 *
 * Usage example:
 * ```js
 * import { useGlobalStore } from '@/stores/global'
 * const store = useGlobalStore()
 * store.setUserId('user-123')
 * store.setQueryId('query-456')
 * ```
 *
 * Notes:
 * - If you want `queryId` to survive page reloads consider persisting it to
 *   `localStorage` or using Pinia plugins for persistence.
 * - Keep this store minimal; prefer more focused stores for larger state domains.
 */
import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('global', {
  state: () => ({
    // Initialize userId and queryId from localStorage when available so they survive reloads
    userId: (typeof window !== 'undefined' && localStorage.getItem('userId')) ? localStorage.getItem('userId') : null,
    queryId: (typeof window !== 'undefined' && localStorage.getItem('queryId')) ? localStorage.getItem('queryId') : null,
  }),
  actions: {
    setUserId(id) {
      this.userId = id
      try {
        if (typeof window !== 'undefined') {
          if (id === null || id === undefined) localStorage.removeItem('userId')
          else localStorage.setItem('userId', String(id))
        }
      } catch (e) {
        console.warn('Could not persist userId to localStorage', e)
      }
    },
    setQueryId(id) {
      this.queryId = id
      try {
        if (typeof window !== 'undefined') {
          if (id === null || id === undefined) localStorage.removeItem('queryId')
          else localStorage.setItem('queryId', String(id))
        }
      } catch (e) {
        // ignore storage errors (e.g., Safari private mode)
        console.warn('Could not persist queryId to localStorage', e)
      }
    },
    clear() {
      this.userId = null
      this.queryId = null
      try {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('queryId')
          localStorage.removeItem('userId')
        }
      } catch (e) {
        console.warn('Could not clear persisted ids from localStorage', e)
      }
    }
  }
})
