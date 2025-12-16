import request from '@/api/request'

export interface DoctorForm {
  npi: string
  first_name: string
  last_name: string
  specialty?: string
  state?: string
  primary_type?: string
}

export function getDoctors(params: any) {
  return request({
    url: '/doctors',
    method: 'get',
    params
  })
}

export function getDoctor(npi: string) {
  return request({
    url: `/doctors/${npi}`,
    method: 'get'
  })
}

export function createDoctor(data: DoctorForm) {
  return request({
    url: '/doctors',
    method: 'post',
    data
  })
}

export function updateDoctor(npi: string, data: Partial<DoctorForm>) {
  return request({
    url: `/doctors/${npi}`,
    method: 'put',
    data
  })
}

export function deleteDoctor(npi: string) {
  return request({
    url: `/doctors/${npi}`,
    method: 'delete'
  })
}

export function getSpecialties() {
  return request({
    url: '/doctors/specialties',
    method: 'get'
  })
}

export function getStates() {
  return request({
    url: '/doctors/states',
    method: 'get'
  })
}
