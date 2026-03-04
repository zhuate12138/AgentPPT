<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { getDownloadUrl } from '@/api'

const store = useProjectsStore()
const router = useRouter()

onMounted(() => {
  store.fetchProjects()
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function openProject(id: string) {
  router.push(`/projects/${id}/edit`)
}
</script>

<template>
  <div class="projects container">
    <h1>项目列表</h1>

    <div v-if="store.loading" class="loading">加载中...</div>

    <div v-else-if="store.error" class="error">{{ store.error }}</div>

    <div v-else-if="store.projects.length === 0" class="empty">
      <p>还没有项目</p>
      <router-link to="/" class="btn btn-primary">创建第一个 PPT</router-link>
    </div>

    <div v-else class="project-list">
      <div
        v-for="project in store.projects"
        :key="project.id"
        class="project-card card"
        @click="openProject(project.id)"
      >
        <div class="project-header">
          <h3>{{ project.name }}</h3>
          <span class="version-badge">v{{ project.current_version }}</span>
        </div>
        <p v-if="project.topic" class="topic">{{ project.topic }}</p>
        <div class="project-meta">
          <span>{{ project.total_versions }} 个版本</span>
          <span>{{ formatDate(project.updated_at) }}</span>
        </div>
        <div class="project-actions">
          <button class="btn btn-primary btn-sm" @click.stop="openProject(project.id)">
            编辑
          </button>
          <a
            :href="getDownloadUrl(project.id, project.current_version)"
            class="btn btn-secondary btn-sm"
            @click.stop
            download
          >
            下载
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.projects {
  max-width: 900px;
}

h1 {
  margin-bottom: 2rem;
}

.project-list {
  display: grid;
  gap: 1rem;
}

.project-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.project-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.project-header h3 {
  font-size: 1.125rem;
  color: #111827;
}

.version-badge {
  background: #dbeafe;
  color: #1d4ed8;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.topic {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.project-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.empty {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.empty p {
  margin-bottom: 1rem;
}
</style>