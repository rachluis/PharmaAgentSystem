import request from './request'

export interface LoginLog {
  id: number
  username: string
  ip_address: string
  browser: string
  os: string
  status: number
  message: string
  login_time: string
}

export interface OperationLog {
  id: number
  username: string
  module: string
  summary: string
  method: string
  path: string
  status: number
  latency_ms: number
  create_time: string
}

export interface LogParams {
  page: number
  size: number
  username?: string
  module?: string
  status?: number
  method?: string
}

export const getLoginLogs = (params: LogParams) => {
  return request.get('/system/logs/login', { params })
}

export const getOperationLogs = (params: LogParams) => {
  return request.get('/system/logs/operation', { params })
}
