<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createProject } from '@/api'

const router = useRouter()
const topic = ref('')
const additionalContext = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

async function handleCreate() {
  if (!topic.value.trim()) {
    error.value = '请输入主题'
    return
  }

  loading.value = true
  error.value = null

  try {
    const result = await createProject({
      topic: topic.value,
      additional_context: additionalContext.value || undefined
    })
    router.push(`/projects/${result.project_id}/edit`)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '创建失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="home container">
    <div class="hero">
      <h1 class="title">
        <span class="icon">📊</span>
        AgentPPT
      </h1>
      <p class="subtitle">用自然语言创建和编辑演示文稿，让 AI Agent 帮你做 PPT</p>
    </div>

    <div class="create-form card">
      <h2>创建新 PPT</h2>
      
      <div class="form-group">
        <label class="label" for="topic">主题 *</label>
        <input
          id="topic"
          v-model="topic"
          type="text"
          class="input"
          placeholder="例如：人工智能在教育领域的应用"
          :disabled="loading"
        />
      </div>

      <div class="form-group">
        <label class="label" for="context">补充说明（可选）</label>
        <textarea
          id="context"
          v-model="additionalContext"
          class="textarea"
          placeholder="可以添加更多背景信息、具体要求等..."
          :disabled="loading"
        />
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <button
        class="btn btn-primary"
        :disabled="loading || !topic.trim()"
        @click="handleCreate"
      >
        {{ loading ? '生成中...' : '生成 PPT' }}
      </button>
    </div>

    <div class="features">
      <div class="feature">
        <span class="feature-icon">🎯</span>
        <h3>主题驱动</h3>
        <p>输入主题，AI 自动生成大纲和内容</p>
      </div>
      <div class="feature">
        <span class="feature-icon">✏️</span>
        <h3>自然语言编辑</h3>
        <p>用文字描述修改意图，AI 理解并执行</p>
      </div>
      <div class="feature">
        <span class="feature-icon">👁️</span>
        <h3>实时预览</h3>
        <p>修改即时预览，满意再保存</p>
      </div>
      <div class="feature">
        <span class="feature-icon">📦</span>
        <h3>版本管理</h3>
        <p>多版本保存，随时回退</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 900px;
}

.hero {
  text-align: center;
  padding: 3rem 0;
}

.title {
  font-size: 3rem;
  font-weight: 700;
  color: #111827;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.icon {
  font-size: 3rem;
}

.subtitle {
  font-size: 1.25rem;
  color: #6b7280;
  margin-top: 1rem;
}

.create-form {
  margin-top: 2rem;
  text-align: left;
}

.create-form h2 {
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 4rem;
}

.feature {
  text-align: center;
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 2.5rem;
}

.feature h3 {
  margin: 0.75rem 0 0.5rem;
  font-size: 1rem;
  color: #111827;
}

.feature p {
  font-size: 0.875rem;
  color: #6b7280;
}
</style>