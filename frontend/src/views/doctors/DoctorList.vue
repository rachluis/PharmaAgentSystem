<template>
  <div class="doctor-list-container">
    <!-- Filter Bar -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters" class="filter-form">
        <!-- Main Filters & Search Actions Row -->
        <div class="filter-row">
            <div class="filter-main-group">
                <el-form-item label="搜索">
                    <el-input 
                        v-model="filters.search" 
                        placeholder="姓名或 NPI" 
                        clearable 
                        @keyup.enter="handleFilter"
                        prefix-icon="Search"
                        style="width: 240px"
                    />
                </el-form-item>
                <el-form-item label="专科">
                    <el-select 
                        v-model="filters.specialty" 
                        placeholder="选择专科 (可多选)" 
                        clearable 
                        filterable 
                        multiple
                        collapse-tags
                        collapse-tags-indicator
                        style="width: 220px"
                    >
                        <el-option v-for="s in specialties" :key="s" :label="s" :value="s" />
                    </el-select>
                </el-form-item>
                <el-form-item label="州">
                     <el-select 
                        v-model="filters.state" 
                        placeholder="选择州" 
                        clearable 
                        filterable
                        multiple
                        collapse-tags
                        style="width: 180px"
                    >
                        <el-option v-for="s in states" :key="s" :label="s" :value="s" />
                    </el-select>
                </el-form-item>
            </div>
            
            <div class="filter-action-group">
                <el-button type="primary" :icon="Search" @click="handleFilter">查询</el-button>
                <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
            </div>
        </div>

        <!-- RFM & Utilities Row -->
        <div class="filter-row secondary-row">
            <div class="filter-rfm-group">
                <el-form-item label="Recency">
                    <div class="range-inputs">
                        <el-input-number v-model="filters.min_recency" :controls="false" placeholder="Min" style="width: 80px" />
                        <span class="range-split">-</span>
                        <el-input-number v-model="filters.max_recency" :controls="false" placeholder="Max" style="width: 80px" />
                    </div>
                </el-form-item>
                <el-form-item label="Frequency">
                    <div class="range-inputs">
                        <el-input-number v-model="filters.min_frequency" :controls="false" placeholder="Min" style="width: 80px" />
                        <span class="range-split">-</span>
                        <el-input-number v-model="filters.max_frequency" :controls="false" placeholder="Max" style="width: 80px" />
                    </div>
                </el-form-item>
                <el-form-item label="Monetary">
                    <div class="range-inputs">
                        <el-input-number v-model="filters.min_monetary" :controls="false" placeholder="Min" style="width: 100px" />
                        <span class="range-split">-</span>
                        <el-input-number v-model="filters.max_monetary" :controls="false" placeholder="Max" style="width: 100px" />
                    </div>
                </el-form-item>
            </div>

            <div class="filter-utility-group">
                <el-dropdown split-button type="info" @click="handleDownloadTemplate">
                    <el-icon><Download /></el-icon> 下载模板
                    <template #dropdown>
                        <el-upload
                            class="import-upload"
                            action="#"
                            :auto-upload="true"
                            :show-file-list="false"
                            :http-request="handleUploadRequest"
                            accept=".csv,.xlsx,.xls"
                        >
                            <el-dropdown-item>
                                <el-icon><Upload /></el-icon> 批量导入
                            </el-dropdown-item>
                        </el-upload>
                    </template>
                </el-dropdown>
                <el-button type="success" :icon="Plus" @click="openCreateDialog">
                    新增医生
                </el-button>
            </div>
        </div>
      </el-form>
    </el-card>

    <!-- Data Table -->
    <div class="table-wrapper">
        <el-table 
            v-loading="loading"
            :data="doctors" 
            stripe 
            border 
            style="width: 100%; height: 100%"
            highlight-current-row
        >
            <el-table-column label="医生信息" min-width="200">
                <template #default="{ row }">
                    <div class="doctor-info-cell">
                        <div class="doctor-name">{{ row.first_name }} {{ row.last_name }}</div>
                        <div class="doctor-npi">NPI: {{ row.npi }}</div>
                    </div>
                </template>
            </el-table-column>
            
            <el-table-column label="专科与地区" min-width="220">
                <template #default="{ row }">
                     <div 
                        class="interactive-text" 
                        @click="handleInteractiveFilter('specialty', row.specialty)"
                        title="点击筛选专科"
                     >
                        {{ row.specialty || 'Unknown' }}
                     </div>
                     <div class="location-text">
                        <el-icon><Location /></el-icon> 
                        <span 
                            class="interactive-text" 
                            @click="handleInteractiveFilter('state', row.state)"
                            title="点击筛选州"
                        >
                            {{ row.state }}
                        </span>
                        <span v-if="row.city" class="city-text">({{ row.city }})</span>
                     </div>
                </template>
            </el-table-column>

            <el-table-column label="RFM 指标" width="300">
                <template #default="{ row }">
                    <div class="rfm-tags">
                        <el-tooltip content="Recency (距今支付天数)" placement="top">
                             <el-tag 
                                size="small" 
                                :type="getRfmType(row.recency_days, 'Recency')" 
                                effect="plain"
                                class="interactive-tag"
                                @click="handleInteractiveFilter('recency', row.recency_days)"
                             >
                                R: {{ row.recency_days ?? '-' }}d
                             </el-tag>
                        </el-tooltip>
                        <el-tooltip content="Frequency (总支付次数)" placement="top">
                            <el-tag 
                                size="small" 
                                :type="getRfmType(row.frequency, 'Frequency')" 
                                effect="plain"
                                class="interactive-tag"
                                @click="handleInteractiveFilter('frequency', row.frequency)"
                            >
                                F: {{ row.frequency }}
                            </el-tag>
                        </el-tooltip>
                        <el-tooltip content="Monetary (累计支付金额)" placement="top">
                            <el-tag 
                                size="small" 
                                :type="getRfmType(row.monetary, 'Monetary')" 
                                effect="plain"
                                class="interactive-tag"
                                @click="handleInteractiveFilter('monetary', row.monetary)"
                            >
                                M: ${{ row.monetary.toLocaleString() }}
                            </el-tag>
                        </el-tooltip>
                    </div>
                </template>
            </el-table-column>

            <el-table-column label="操作" width="160" fixed="right" align="center">
                <template #default="{ row }">
                    <el-button type="primary" link icon="Edit" @click="handleEdit(row)">编辑</el-button>
                    <el-button type="danger" link icon="Delete" @click="handleDelete(row)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>

    <!-- Pagination -->
    <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
    </div>

    <!-- Dialogs (Create/Edit) -->
     <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? '编辑医生资料' : '新增医生'"
        width="500px"
        destroy-on-close
    >
        <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
            <el-form-item label="NPI" prop="npi">
                <el-input v-model="form.npi" :disabled="isEdit" placeholder="10位数字 NPI" />
            </el-form-item>
             <el-form-item label="First Name" prop="名">
                <el-input v-model="form.first_name" />
            </el-form-item>
             <el-form-item label="Last Name" prop="姓">
                <el-input v-model="form.last_name" />
            </el-form-item>
            <el-form-item label="专科" prop="specialty">
                <el-select v-model="form.specialty" filterable allow-create default-first-option placeholder="选择或输入..." style="width: 100%">
                     <el-option v-for="s in specialties" :key="s" :label="s" :value="s" />
                </el-select>
            </el-form-item>
             <el-form-item label="州" prop="state">
                <el-select v-model="form.state" filterable placeholder="选择州" style="width: 100%">
                     <el-option v-for="s in states" :key="s" :label="s" :value="s" />
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="submitting" @click="submitForm">
                {{ isEdit ? '更新' : '创建' }}
            </el-button>
        </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Plus, Location, Download, Upload, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { 
    getDoctors, 
    deleteDoctor, 
    createDoctor, 
    updateDoctor, 
    getSpecialties,
    getStates,
    downloadTemplate,
    importDoctors,
    type Doctor 
} from '@/api/doctors'

// -- Refs & State --
const loading = ref(false)
const submitting = ref(false)
const doctors = ref<Doctor[]>([])
const total = ref(0)
const specialties = ref<string[]>([])
const states = ref<string[]>([])

const pagination = reactive({
    page: 1,
    pageSize: 20
})

const filters = reactive({
    search: '',
    specialty: [] as string[],
    state: [] as string[],
    min_recency: null as number | null,
    max_recency: null as number | null,
    min_frequency: null as number | null,
    max_frequency: null as number | null,
    min_monetary: null as number | null,
    max_monetary: null as number | null
})

// Dialog State
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({
    npi: '',
    first_name: '',
    last_name: '',
    specialty: '',
    state: '',
    primary_type: 'Medical Doctor'
})

// Validation Rules
const rules = reactive<FormRules>({
    npi: [
        { required: true, message: '请输入 NPI', trigger: 'blur' },
        { min: 10, max: 10, message: 'NPI 必须为 10 位数字', trigger: 'blur' },
        { pattern: /^\d+$/, message: 'NPI 只能包含数字', trigger: 'blur' }
    ],
    first_name: [{ required: true, message: '名是必填项', trigger: 'blur' }],
    last_name: [{ required: true, message: '姓是必填项', trigger: 'blur' }]
})

// -- Methods --

const fetchData = async () => {
    loading.value = true
    try {
        const res = await getDoctors({
            page: pagination.page,
            page_size: pagination.pageSize,
            specialty: filters.specialty.length > 0 ? filters.specialty : undefined,
            state: filters.state.length > 0 ? filters.state : undefined,
            search: filters.search || undefined,
            min_recency: filters.min_recency ?? undefined,
            max_recency: filters.max_recency ?? undefined,
            min_frequency: filters.min_frequency ?? undefined,
            max_frequency: filters.max_frequency ?? undefined,
            min_monetary: filters.min_monetary ?? undefined,
            max_monetary: filters.max_monetary ?? undefined
        })
        doctors.value = res.items
        total.value = res.total
    } catch (error) {
        // ElMessage handled by request interceptor
    } finally {
        loading.value = false
    }
}

const fetchOptions = async () => {
    try {
        const [specRes, stateRes] = await Promise.all([
            getSpecialties(),
            getStates()
        ])
        specialties.value = specRes.specialties
        states.value = stateRes.states
    } catch(e) {
        console.error("Failed to load options", e)
    }
}

// Handler for filtering (search input, select change)
const handleFilter = () => {
    pagination.page = 1
    fetchData()
}

const resetFilters = () => {
    filters.search = ''
    filters.specialty = []
    filters.state = []
    filters.min_recency = null
    filters.max_recency = null
    filters.min_frequency = null
    filters.max_frequency = null
    filters.min_monetary = null
    filters.max_monetary = null
    handleFilter()
}

// Interactive filter from table cells
const handleInteractiveFilter = (type: string, value: any) => {
    if (value === null || value === undefined) return
    
    // Reset other irrelevant filters if needed, or just append
    if (type === 'specialty') {
        if (!filters.specialty.includes(value)) {
            filters.specialty = [value] // Replace or append? Let's replace for focused filter
        }
    } else if (type === 'state') {
        filters.state = [value]
    } else if (type === 'recency') {
        filters.min_recency = value
        filters.max_recency = value
    } else if (type === 'frequency') {
        filters.min_frequency = value
        filters.max_frequency = value
    } else if (type === 'monetary') {
        filters.min_monetary = value
        filters.max_monetary = value
    }
    
    handleFilter()
}

// Batch Import Handlers
const handleDownloadTemplate = async () => {
    try {
        const res = await downloadTemplate()
        const blob = new Blob([res as any], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'doctor_import_template.xlsx')
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
    } catch (e) {
        ElMessage.error('下载模板失败')
    }
}

const handleUploadRequest = async (options: any) => {
    const { file } = options
    try {
        const res = await importDoctors(file)
        if (res.status === 'success') {
            ElMessage({
                message: `成功导入 ${res.inserted} 位医生。跳过 ${res.skipped_duplicates} 条重复数据。`,
                type: 'success',
                duration: 5000
            })
            fetchData()
        }
    } catch (e: any) {
        const errorMsg = e.response?.data?.detail || '导入失败，请检查文件格式'
        ElMessage.error(errorMsg)
    }
}

const handlePageChange = (val: number) => {
    pagination.page = val
    fetchData()
}

const handleSizeChange = (val: number) => {
    pagination.pageSize = val
    pagination.page = 1
    fetchData()
}

// RFM Visual Logic
const getRfmType = (value: number | null | undefined, type: string) => {
   if (value === null || value === undefined) return 'info'
   
   if (type === 'Recency') {
       // Smaller is better (more recent)
       if (value <= 90) return 'success'
       if (value <= 365) return 'warning'
       return 'danger'
   }
   if (type === 'Frequency') {
       // Higher is better
       if (value >= 10) return 'success'
       if (value >= 5) return 'primary'
       return 'info'
   }
   if (type === 'Monetary') {
       // Higher is better
       if (value >= 50000) return 'warning' // High value
       if (value >= 1000) return 'primary'
       return 'info'
   }
   return 'info'
}

// Delete Logic
const handleDelete = (row: Doctor) => {
    ElMessageBox.confirm(
        `确定要永久删除 ${row.first_name} ${row.last_name} 医生的资料吗？`,
        '确认删除',
        {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(async () => {
        try {
            await deleteDoctor(row.npi)
            ElMessage.success('医生资料已成功删除')
            fetchData()
        } catch (error) {
            // Error managed by interceptor
            if(error && (error as any).response?.status === 404) {
                 ElMessage.error('医生不存在，可能已被删除')
                 fetchData()
            }
        }
    }).catch(() => {
        // Cancelled
    })
}

// Dialog Logic
const openCreateDialog = () => {
    isEdit.value = false
    // Reset form
    form.npi = ''
    form.first_name = ''
    form.last_name = ''
    form.specialty = ''
    form.state = ''
    dialogVisible.value = true
}

const handleEdit = (row: Doctor) => {
    isEdit.value = true
    form.npi = row.npi
    form.first_name = row.first_name || ''
    form.last_name = row.last_name || ''
    form.specialty = row.specialty || ''
    form.state = row.state || ''
    dialogVisible.value = true
}

const submitForm = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true
            try {
                if (isEdit.value) {
                    await updateDoctor(form.npi, form)
                    ElMessage.success('医生资料已更新')
                } else {
                    await createDoctor(form)
                    ElMessage.success('新医生已成功创建')
                }
                dialogVisible.value = false
                fetchData()
            } catch (error) {
                // Interceptor handles error message
            } finally {
                submitting.value = false
            }
        }
    })
}

// Init
onMounted(() => {
    fetchData()
    fetchOptions()
})
</script>

<style scoped>
.doctor-list-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 20px;
    /* Adapts to parent layout padding */
}

/* Filter Bar Revamp */
.filter-card {
    margin-bottom: 20px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background-color: #fff;
}

.filter-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.filter-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

.secondary-row {
    padding-top: 12px;
    border-top: 1px dashed #ebeef5;
}

.filter-main-group, .filter-rfm-group {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.filter-action-group, .filter-utility-group {
    display: flex;
    gap: 12px;
    margin-left: 20px;
}

.range-inputs {
    display: flex;
    align-items: center;
    gap: 4px;
}

.range-split {
    color: #909399;
}

.filter-form :deep(.el-form-item) {
    margin-bottom: 0px !important;
    margin-right: 0px !important;
}

/* Adjust numerical input arrows */
:deep(.el-input-number .el-input__inner) {
    text-align: left;
}

/* Table Area */
.table-wrapper {
    flex: 1;
    overflow: hidden; /* Ensures table scrolls inside */
    border-radius: var(--radius-sm);
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Custom Cells */
.doctor-info-cell {
    display: flex;
    flex-direction: column;
    line-height: 1.4;
}

.doctor-name {
    font-weight: 700;
    color: var(--foreground);
    font-size: 14px;
}

.doctor-npi {
    color: var(--muted-foreground, #999);
    font-size: 12px;
    font-family: 'Courier New', Courier, monospace;
}

.interactive-text {
    cursor: pointer;
    color: var(--el-color-primary);
    transition: color 0.2s;
}

.interactive-text:hover {
    color: var(--el-color-primary-light-3);
    text-decoration: underline;
}

.location-text {
    font-size: 13px;
    color: var(--text-color-secondary);
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 4px;
}

.city-text {
    color: #999;
    font-size: 12px;
}

.rfm-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.interactive-tag {
    cursor: pointer;
}

.interactive-tag:hover {
    filter: brightness(0.9);
}

.pagination-container {
    display: flex;
    justify-content: flex-end;
    padding: 8px 0;
}

/* Adjust numerical input arrows */
:deep(.el-input-number .el-input__inner) {
    text-align: left;
}
</style>
