<!--
App.vue - Root application component

Purpose:
- Serves as the single root for the SPA. The file currently renders the router
  outlet (`<router-view />`) where page views are injected by Vue Router.

Common extension points:
- Add a global navigation bar, footer, or app-wide providers (theme switcher,
  error boundary) here so every view inherits the same layout.
- Use named slots or layout components to provide different page scaffolding
  (e.g., dashboard vs. auth pages).

Notes:
- Keep the root component light. Heavy per-page logic belongs in view components.
-->

<script setup>
import BaseLayout from './components/BaseLayout.vue'
</script>

<template>
  <BaseLayout>
    <router-view />
  </BaseLayout>
</template>

<style>
body { font-family: Arial, sans-serif; }
</style>
