import request from './request'

// Types
export interface Doctor {
    npi: string
    first_name: string | null
    last_name: string | null
    full_name: string | null
    specialty: string | null
    state: string | null
    city: string | null
    primary_type: string | null
    monetary: number
    frequency: number
    recency_days: number | null
}

export interface DoctorListResponse {
    total: number
    items: Doctor[]
}

export interface DoctorCreate {
    npi: string
    first_name: string
    last_name: string
    specialty?: string
    state?: string
    primary_type?: string
}

export interface DoctorUpdate {
    first_name?: string
    last_name?: string
    specialty?: string
    state?: string
    primary_type?: string
}

export interface DoctorQueryParams {
    page?: number
    page_size?: number
    specialty?: string
    state?: string
    search?: string
    cluster_id?: number
    min_monetary?: number
    max_monetary?: number
}

export interface StatisticsResponse {
    total_doctors: number
    total_monetary: number
    avg_monetary: number
    avg_frequency: number
    specialty_distribution: Record<string, number>
    state_distribution: Record<string, number>
}

// API Methods
export const getDoctors = (params: DoctorQueryParams) => {
    return request<any, DoctorListResponse>({
        url: '/doctors',
        method: 'get',
        params
    })
}

export const getDoctor = (npi: string) => {
    return request<any, { doctor: Doctor, recent_payments: any[] }>({
        url: `/doctors/${npi}`,
        method: 'get'
    })
}

export const createDoctor = (data: DoctorCreate) => {
    return request<any, Doctor>({
        url: '/doctors',
        method: 'post',
        data
    })
}

export const updateDoctor = (npi: string, data: DoctorUpdate) => {
    return request<any, Doctor>({
        url: `/doctors/${npi}`,
        method: 'put',
        data
    })
}

export const deleteDoctor = (npi: string) => {
    return request<any, void>({
        url: `/doctors/${npi}`,
        method: 'delete'
    })
}

export const getStatistics = () => {
    return request<any, StatisticsResponse>({
        url: '/doctors/statistics',
        method: 'get'
    })
}

export const getSpecialties = () => {
    return request<any, { specialties: string[] }>({
        url: '/doctors/specialties',
        method: 'get'
    })
}

export const getStates = () => {
    return request<any, { states: string[] }>({
        url: '/doctors/states',
        method: 'get'
    })
}
