<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="app">
    <header class="header">
      <router-link to="/" class="logo">
        <span class="logo-icon">📊</span>
        <span class="logo-text">AgentPPT</span>
      </router-link>
      <nav class="nav">
        <router-link to="/">首页</router-link>
        <router-link to="/projects">项目列表</router-link>
      </nav>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.logo-icon {
  font-size: 1.5rem;
}

.nav {
  display: flex;
  gap: 1.5rem;
}

.nav a {
  text-decoration: none;
  color: #6b7280;
  font-weight: 500;
  transition: color 0.2s;
}

.nav a:hover,
.nav a.router-link-active {
  color: #3b82f6;
}

.main {
  flex: 1;
  padding: 2rem;
  background: #f9fafb;
}
</style>