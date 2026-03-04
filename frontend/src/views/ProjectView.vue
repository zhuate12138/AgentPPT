<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProject, type ProjectMeta, type VersionMeta, type PPTSummary } from '@/api'

const route = useRoute()
const router = useRouter()

const projectId = route.params.id as string

const loading = ref(true)
const error = ref<string | null>(null)
const meta = ref<ProjectMeta | null>(null)
const versions = ref<VersionMeta[]>([])
const summary = ref<PPTSummary | null>(null)

onMounted(async () => {
  try {
    const data = await getProject(projectId)
    meta.value = data.meta
    versions.value = data.versions
    summary.value = data.current_summary
  } catch (e: any) {
    error.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function startEdit() {
  router.push(`/projects/${projectId}/edit`)
}
</script>

<template>
  <div class="project container">
    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else-if="meta">
      <div class="project-header card">
        <div>
          <h1>{{ meta.name }}</h1>
          <p v-if="meta.topic" class="topic">{{ meta.topic }}</p>
        </div>
        <div class="actions">
          <button class="btn btn-primary" @click="startEdit">编辑 PPT</button>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-card card">
          <h3>概览</h3>
          <div class="info-item">
            <span class="label">当前版本</span>
            <span class="value">v{{ meta.current_version }}</span>
          </div>
          <div class="info-item">
            <span class="label">总页数</span>
            <span class="value">{{ summary?.total_slides || 0 }} 页</span>
          </div>
          <div class="info-item">
            <span class="label">创建时间</span>
            <span class="value">{{ formatDate(meta.created_at) }}</span>
          </div>
        </div>

        <div class="versions-card card">
          <h3>版本历史</h3>
          <div v-if="versions.length === 0" class="empty-versions">
            暂无版本记录
          </div>
          <div v-else class="version-list">
            <div
              v-for="v in [...versions].reverse()"
              :key="v.version"
              class="version-item"
              :class="{ current: v.version === meta.current_version }"
            >
              <div class="version-info">
                <span class="version-num">v{{ v.version }}</span>
                <span v-if="v.description" class="version-desc">{{ v.description }}</span>
              </div>
              <span class="version-date">{{ formatDate(v.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="summary" class="outline-card card">
        <h3>内容大纲</h3>
        <div class="outline">
          <div
            v-for="slide in summary.slides"
            :key="slide.index"
            class="outline-item"
          >
            <span class="slide-num">第 {{ slide.index + 1 }} 页</span>
            <span class="slide-title">{{ slide.title || '(无标题)' }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.project {
  max-width: 900px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.project-header h1 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.topic {
  color: #6b7280;
  font-size: 0.875rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-card h3,
.versions-card h3,
.outline-card h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: #374151;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #6b7280;
  font-size: 0.875rem;
}

.info-item .value {
  font-weight: 500;
}

.empty-versions {
  color: #9ca3af;
  font-size: 0.875rem;
}

.version-list {
  max-height: 200px;
  overflow-y: auto;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.version-item:last-child {
  border-bottom: none;
}

.version-item.current {
  background: #f0fdf4;
  margin: 0 -0.5rem;
  padding: 0.5rem;
  border-radius: 0.25rem;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.version-num {
  font-weight: 500;
  font-size: 0.875rem;
}

.version-desc {
  color: #6b7280;
  font-size: 0.75rem;
}

.version-date {
  color: #9ca3af;
  font-size: 0.75rem;
}

.outline-card {
  margin-bottom: 1.5rem;
}

.outline-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.outline-item:last-child {
  border-bottom: none;
}

.slide-num {
  color: #6b7280;
  font-size: 0.875rem;
  min-width: 60px;
}

.slide-title {
  font-size: 0.875rem;
}

@media (max-width: 640px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>