import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ProjectMeta } from '@/api'
import { listProjects } from '@/api'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<ProjectMeta[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProjects() {
    loading.value = true
    error.value = null
    try {
      projects.value = await listProjects()
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch projects'
    } finally {
      loading.value = false
    }
  }

  return {
    projects,
    loading,
    error,
    fetchProjects
  }
})