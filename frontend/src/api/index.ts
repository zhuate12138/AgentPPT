import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Types
export interface PPTSummary {
  total_slides: number
  slides: SlideSummary[]
  theme?: string
}

export interface SlideSummary {
  index: number
  title?: string
  body_text?: string
  has_image: boolean
  has_chart: boolean
  notes?: string
  shape_count: number
}

export interface ProjectMeta {
  id: string
  name: string
  created_at: string
  updated_at: string
  current_version: number
  total_versions: number
  topic?: string
}

export interface VersionMeta {
  version: number
  created_at: string
  description?: string
  is_confirmed: boolean
}

export interface CreatePPTRequest {
  topic: string
  mode?: 'no_template' | 'with_template'
  template_id?: string
  additional_context?: string
}

export interface CreatePPTResponse {
  project_id: string
  version: number
  slide_count: number
  summary: PPTSummary
}

export interface EditPPTRequest {
  project_id: string
  version: number
  prompt: string
  current_slide_index?: number
}

export interface EditInstruction {
  type: string
  slide_index: number
  shape_id?: string
  content?: string
  bullets?: string[]
  position?: { left: number; top: number; width: number; height: number }
}

export interface EditPPTResponse {
  project_id: string
  old_version: number
  new_version: number
  is_confirmed: boolean
  instructions_executed: EditInstruction[]
  preview_images: string[]
}

export interface SlidePreview {
  index: number
  image_url: string
}

// API functions

export async function createProject(data: CreatePPTRequest): Promise<CreatePPTResponse> {
  const response = await api.post('/projects', data)
  return response.data
}

export async function listProjects(): Promise<ProjectMeta[]> {
  const response = await api.get('/projects')
  return response.data
}

export async function getProject(projectId: string): Promise<{
  meta: ProjectMeta
  versions: VersionMeta[]
  current_summary: PPTSummary
}> {
  const response = await api.get(`/projects/${projectId}`)
  return response.data
}

export async function getSlides(projectId: string, version: number): Promise<{
  project_id: string
  version: number
  slides: SlidePreview[]
}> {
  const response = await api.get(`/projects/${projectId}/versions/${version}/slides`)
  return response.data
}

export async function editPPT(projectId: string, data: {
  version: number
  prompt: string
  current_slide_index?: number
}): Promise<EditPPTResponse> {
  const response = await api.post(`/projects/${projectId}/edit`, {
    project_id: projectId,
    ...data
  })
  return response.data
}

export async function confirmEdit(projectId: string, version: number): Promise<void> {
  await api.post(`/projects/${projectId}/confirm`, {
    project_id: projectId,
    version
  })
}

export async function cancelEdit(projectId: string, version: number): Promise<void> {
  await api.post(`/projects/${projectId}/cancel`, {
    project_id: projectId,
    version
  })
}

export async function restoreVersion(projectId: string, targetVersion: number): Promise<{
  status: string
  new_version: number
}> {
  const response = await api.post(`/projects/${projectId}/restore`, {
    project_id: projectId,
    target_version: targetVersion
  })
  return response.data
}

export async function deleteProject(projectId: string): Promise<void> {
  await api.delete(`/projects/${projectId}`)
}

export function getPreviewUrl(projectId: string, version: number, slideIndex: number): string {
  return `/api/v1/projects/${projectId}/versions/${version}/previews/slide_${slideIndex}.png`
}

export function getDownloadUrl(projectId: string, version: number): string {
  return `/api/v1/projects/${projectId}/versions/${version}/download`
}

export default api