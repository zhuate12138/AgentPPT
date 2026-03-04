<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getProject,
  getSlides,
  editPPT,
  confirmEdit,
  cancelEdit,
  getDownloadUrl,
  type SlidePreview,
  type ProjectMeta
} from '@/api'

const route = useRoute()
const router = useRouter()

const projectId = route.params.id as string

// State
const loading = ref(true)
const meta = ref<ProjectMeta | null>(null)
const slides = ref<SlidePreview[]>([])
const currentSlideIndex = ref(0)
const editPrompt = ref('')
const editLoading = ref(false)
const pendingVersion = ref<number | null>(null)
const error = ref<string | null>(null)
const success = ref<string | null>(null)

// Computed
const currentSlide = computed(() => {
  if (slides.value.length === 0) return null
  return slides.value[currentSlideIndex.value]
})

const hasPendingEdit = computed(() => pendingVersion.value !== null)

// Methods
async function loadProject() {
  loading.value = true
  error.value = null
  
  try {
    const data = await getProject(projectId)
    meta.value = data.meta
    
    const slidesData = await getSlides(projectId, data.meta.current_version)
    slides.value = slidesData.slides
  } catch (e: any) {
    error.value = e.response?.data?.detail || '加载失败'
  } finally {
    loading.value = false
  }
}

async function handleEdit() {
  if (!editPrompt.value.trim() || !meta.value) return

  editLoading.value = true
  error.value = null
  success.value = null

  try {
    const result = await editPPT(projectId, {
      version: meta.value.current_version,
      prompt: editPrompt.value,
      current_slide_index: currentSlideIndex.value
    })

    if (result.new_version !== result.old_version) {
      pendingVersion.value = result.new_version
      
      // Load new previews
      const slidesData = await getSlides(projectId, result.new_version)
      slides.value = slidesData.slides
    }

    editPrompt.value = ''
  } catch (e: any) {
    error.value = e.response?.data?.detail || '编辑失败'
  } finally {
    editLoading.value = false
  }
}

async function handleConfirm() {
  if (!pendingVersion.value) return

  try {
    await confirmEdit(projectId, pendingVersion.value)
    
    if (meta.value) {
      meta.value.current_version = pendingVersion.value
    }
    
    pendingVersion.value = null
    success.value = '已保存'
    setTimeout(() => { success.value = null }, 3000)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '确认失败'
  }
}

async function handleCancel() {
  if (!pendingVersion.value || !meta.value) return

  try {
    await cancelEdit(projectId, pendingVersion.value)
    
    // Reload original version
    const slidesData = await getSlides(projectId, meta.value.current_version)
    slides.value = slidesData.slides
    
    pendingVersion.value = null
    success.value = '已取消'
    setTimeout(() => { success.value = null }, 3000)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '取消失败'
  }
}

function selectSlide(index: number) {
  currentSlideIndex.value = index
}

function prevSlide() {
  if (currentSlideIndex.value > 0) {
    currentSlideIndex.value--
  }
}

function nextSlide() {
  if (currentSlideIndex.value < slides.value.length - 1) {
    currentSlideIndex.value++
  }
}

// Lifecycle
onMounted(() => {
  loadProject()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

// Keyboard navigation
function handleKeydown(e: KeyboardEvent) {
  if (e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLInputElement) {
    return
  }
  
  if (e.key === 'ArrowLeft') {
    prevSlide()
  } else if (e.key === 'ArrowRight') {
    nextSlide()
  }
}
</script>

<template>
  <div class="edit-view">
    <div v-if="loading" class="loading-full">加载中...</div>

    <div v-else-if="error && !meta" class="error-full">
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="loadProject">重试</button>
    </div>

    <template v-else>
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <router-link to="/projects" class="btn btn-secondary btn-sm">← 返回</router-link>
          <span class="project-name">{{ meta?.name }}</span>
        </div>
        <div class="toolbar-right">
          <span v-if="hasPendingEdit" class="pending-badge">待确认修改</span>
          <a
            v-if="meta"
            :href="getDownloadUrl(projectId, pendingVersion || meta.current_version)"
            class="btn btn-secondary btn-sm"
            download
          >
            下载 PPT
          </a>
        </div>
      </div>

      <!-- Main content -->
      <div class="main-content">
        <!-- Sidebar: Thumbnails -->
        <div class="sidebar">
          <div class="thumbnails">
            <div
              v-for="slide in slides"
              :key="slide.index"
              class="thumbnail"
              :class="{ active: slide.index === currentSlideIndex }"
              @click="selectSlide(slide.index)"
            >
              <img
                :src="slide.image_url"
                :alt="`Slide ${slide.index + 1}`"
              />
              <span class="thumb-num">{{ slide.index + 1 }}</span>
            </div>
          </div>
        </div>

        <!-- Center: Current slide -->
        <div class="slide-area">
          <div v-if="currentSlide" class="slide-container">
            <img
              :src="currentSlide.image_url"
              :alt="`Slide ${currentSlideIndex + 1}`"
              class="slide-image"
            />
          </div>
          <div class="slide-nav">
            <button
              class="btn btn-secondary btn-sm"
              :disabled="currentSlideIndex === 0"
              @click="prevSlide"
            >
              ← 上一页
            </button>
            <span class="slide-counter">
              {{ currentSlideIndex + 1 }} / {{ slides.length }}
            </span>
            <button
              class="btn btn-secondary btn-sm"
              :disabled="currentSlideIndex === slides.length - 1"
              @click="nextSlide"
            >
              下一页 →
            </button>
          </div>
        </div>

        <!-- Right: Edit panel -->
        <div class="edit-panel">
          <div class="panel-section">
            <h3>编辑 PPT</h3>
            <p class="hint">用自然语言描述你想修改的内容</p>

            <div v-if="error" class="error">{{ error }}</div>
            <div v-if="success" class="success">{{ success }}</div>

            <textarea
              v-model="editPrompt"
              class="textarea"
              placeholder="例如：把标题改成「人工智能的发展历程」"
              :disabled="editLoading || hasPendingEdit"
            />

            <button
              class="btn btn-primary btn-block"
              :disabled="!editPrompt.trim() || editLoading || hasPendingEdit"
              @click="handleEdit"
            >
              {{ editLoading ? '处理中...' : '执行修改' }}
            </button>
          </div>

          <!-- Pending edit actions -->
          <div v-if="hasPendingEdit" class="panel-section pending-section">
            <h4>待确认修改</h4>
            <p class="pending-info">版本 v{{ pendingVersion }} 待确认</p>
            <div class="pending-actions">
              <button
                class="btn btn-success btn-block"
                @click="handleConfirm"
              >
                ✓ 确认保存
              </button>
              <button
                class="btn btn-danger btn-block"
                @click="handleCancel"
              >
                ✗ 取消修改
              </button>
            </div>
          </div>

          <!-- Tips -->
          <div class="panel-section tips">
            <h4>💡 使用提示</h4>
            <ul>
              <li>可以修改标题、正文内容</li>
              <li>使用「第X页」指定页面</li>
              <li>不满意可以取消重来</li>
              <li>使用 ← → 键切换页面</li>
            </ul>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.edit-view {
  height: calc(100vh - 73px);
  display: flex;
  flex-direction: column;
  background: #f3f4f6;
}

.loading-full,
.error-full {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.project-name {
  font-weight: 500;
  color: #374151;
}

.pending-badge {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Main content */
.main-content {
  flex: 1;
  display: flex;
  min-height: 0;
}

/* Sidebar */
.sidebar {
  width: 180px;
  background: white;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
  padding: 1rem 0.5rem;
}

.thumbnails {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.thumbnail {
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 0.25rem;
  overflow: hidden;
  position: relative;
  transition: border-color 0.2s;
}

.thumbnail:hover {
  border-color: #d1d5db;
}

.thumbnail.active {
  border-color: #3b82f6;
}

.thumbnail img {
  width: 100%;
  display: block;
}

.thumb-num {
  position: absolute;
  bottom: 0.25rem;
  right: 0.25rem;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

/* Slide area */
.slide-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  min-width: 0;
}

.slide-container {
  max-width: 100%;
  max-height: calc(100% - 60px);
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.slide-image {
  max-width: 100%;
  max-height: calc(100vh - 200px);
  display: block;
}

.slide-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.slide-counter {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Edit panel */
.edit-panel {
  width: 320px;
  background: white;
  border-left: 1px solid #e5e7eb;
  padding: 1rem;
  overflow-y: auto;
}

.panel-section {
  margin-bottom: 1.5rem;
}

.panel-section h3 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.panel-section h4 {
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

.textarea {
  margin-bottom: 1rem;
  min-height: 120px;
}

.btn-block {
  width: 100%;
}

.pending-section {
  background: #fffbeb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.pending-info {
  font-size: 0.875rem;
  color: #92400e;
  margin-bottom: 1rem;
}

.pending-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tips ul {
  font-size: 0.75rem;
  color: #6b7280;
  padding-left: 1rem;
  margin: 0;
}

.tips li {
  margin-bottom: 0.25rem;
}
</style>