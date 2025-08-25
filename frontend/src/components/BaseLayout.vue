<!--
BaseLayout.vue

Purpose: lightweight application shell used by `App.vue`.
Provides a header with navigation, a default slot where pages render,
and a small footer. Keep business logic in pages; this component is only
for consistent chrome and simple page scaffolding.
-->
<template>
  <div class="app-root">
    <header class="app-header">
      <div class="header-inner">
        <router-link to="/" class="app-title">ProjecRS</router-link>
        <nav class="app-nav">
          <router-link :to="{ name: 'Upload' }" class="nav-link">Upload</router-link>
          <router-link :to="{ name: 'Result' }" class="nav-link">Results</router-link>
          <router-link :to="{ name: 'Preview' }" class="nav-link">Preview</router-link>
        </nav>
        <div class="header-right"><slot name="header-right" /></div>
      </div>
    </header>

    <main class="app-main">
      <slot />
    </main>

  </div>
</template>

<script setup>
// Lightweight layout wrapper. Keep logic minimal — pages render into the default slot.
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f6f7fb;
  color: #222;
}
.app-header {
  background: linear-gradient(90deg, #2f3775 0%, #4a4fa0 100%);
  color: white;
  padding: 0.75rem 1rem;
  box-shadow: 0 2px 6px rgba(47,55,117,0.12);
}
.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.app-title {
  font-weight: 700;
  color: white;
  text-decoration: none;
  font-size: 1.05rem;
}
.app-nav {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
.nav-link {
  color: rgba(255,255,255,0.9);
  text-decoration: none;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  font-size: 0.95rem;
}
.nav-link:hover { background: rgba(255,255,255,0.06); }
.app-main {
  flex: 1 1 auto;
  max-width: 1100px;
  width: 100%;
  margin: 1.25rem auto;
  padding: 1rem 1rem 4rem; /* larger bottom padding to increase gap above footer */
  box-sizing: border-box;
}
.app-main {
  display: flex;
  justify-content: center; /* center direct child views horizontally */
  align-items: flex-start;
}
/* Constrain full-viewport view wrappers (e.g. .upload-bg) so they don't push layout to the right */
.app-main > * {
  width: 100%;
  max-width: 1100px;
  box-sizing: border-box;
}
.app-footer { background: #ffffff; border-top: 1px solid #e6e7ee; padding: 0.6rem 1rem; }
.footer-inner { max-width: 1100px; margin: 0 auto; color: #6b6f86; font-size: 0.9rem; }
</style>
