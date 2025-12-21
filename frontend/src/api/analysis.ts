import request from './request'

export interface ClusterResult {
  cluster_id: number
  cluster_name: string
  size_count: number
  size_percentage: number
  kpi_summary: any
  strategy_focus: string
  silhouette_score: number
  inertia: number
  task_id: number
  cluster_labels?: any
  visualization_data?: any
}

export interface AnalysisTask {
  task_id: number
  task_name: string
  task_type: string
  status: string
  progress: number
  created_at: string
  error_message?: string
}

export interface GenerateStrategyRequest {
  cluster_id: number
  user_prompt?: string
}

const getClusterResults = () => {
  return request.get<any, ClusterResult[]>('/analysis/tasks/results/list')
}

const createTask = (data: { task_name: string; task_type: string; parameters: any }) => {
  return request.post<any, AnalysisTask>('/analysis/tasks', data)
}

const getTask = (taskId: number) => {
  return request.get<any, AnalysisTask>(`/analysis/tasks/${taskId}`)
}

// Generate AI Strategy (SSE Streaming)
const generateStrategyStream = (
  clusterId: number,
  userPrompt: string,
  onChunk: (chunk: string) => void,
  onError: (error: Error) => void,
  onDone: () => void
) => {
  const token = localStorage.getItem('token')
  const data: GenerateStrategyRequest = {
      cluster_id: clusterId,
      user_prompt: userPrompt
  }
  
  fetch('/api/v1/reports/generate-stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  }).then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    function read() {
      reader?.read().then(({ done, value }) => {
        if (done) {
          onDone()
          return
        }
        
        const text = decoder.decode(value)
        const lines = text.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              onDone()
              return
            }
            onChunk(data)
          }
        }
        
        read()
      }).catch(onError)
    }
    
    read()
  }).catch(onError)
}

const getReports = (params?: { page?: number; page_size?: number }) => {
  return request.get('/reports', { params })
}

const getReport = (reportId: number) => {
  return request.get(`/reports/${reportId}`)
}

export const analysisApi = {
  getClusterResults,
  createTask,
  getTask,
  generateStrategyStream,
  getReports,
  getReport
}
