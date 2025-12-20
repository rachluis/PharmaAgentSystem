<template>
  <div class="doctor-list-container">
    <!-- Filter Bar -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="Search">
            <el-input 
                v-model="filters.search" 
                placeholder="Name or NPI" 
                clearable 
                @input="handleFilter"
                prefix-icon="Search"
                style="width: 240px"
            />
        </el-form-item>
        <el-form-item label="Specialty">
            <el-select 
                v-model="filters.specialty" 
                placeholder="All Specialties" 
                clearable 
                filterable 
                @change="handleFilter"
                style="width: 220px"
            >
                <el-option v-for="s in specialties" :key="s" :label="s" :value="s" />
            </el-select>
        </el-form-item>
        <el-form-item label="State">
             <el-select 
                v-model="filters.state" 
                placeholder="State" 
                clearable 
                filterable
                @change="handleFilter"
                style="width: 120px"
            >
                <el-option v-for="s in states" :key="s" :label="s" :value="s" />
            </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
            <el-button @click="resetFilters">Reset</el-button>
            <el-button type="primary" @click="openCreateDialog">
                <el-icon><Plus /></el-icon> Add Doctor
            </el-button>
        </el-form-item>
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
            <el-table-column label="Doctor Info" min-width="220">
                <template #default="{ row }">
                    <div class="doctor-info-cell">
                        <div class="doctor-name">{{ row.first_name }} {{ row.last_name }}</div>
                        <div class="doctor-npi">NPI: {{ row.npi }}</div>
                    </div>
                </template>
            </el-table-column>
            
            <el-table-column label="Specialty & Location" min-width="200">
                <template #default="{ row }">
                     <div>{{ row.specialty || 'Unknown' }}</div>
                     <div class="location-text">
                        <el-icon><Location /></el-icon> {{ row.city ? row.city + ', ' : '' }}{{ row.state }}
                     </div>
                </template>
            </el-table-column>

            <el-table-column label="RFM Indicators" width="260">
                <template #default="{ row }">
                    <div class="rfm-tags">
                        <el-tooltip content="Recency (Days since last payment)" placement="top">
                             <el-tag size="small" :type="getRfmType(row.recency_days, 'Recency')" effect="plain">
                                R: {{ row.recency_days ?? '-' }}d
                             </el-tag>
                        </el-tooltip>
                        <el-tooltip content="Frequency (Total transactions)" placement="top">
                            <el-tag size="small" :type="getRfmType(row.frequency, 'Frequency')" effect="plain">
                                F: {{ row.frequency }}
                            </el-tag>
                        </el-tooltip>
                        <el-tooltip content="Monetary (Total USD)" placement="top">
                            <el-tag size="small" :type="getRfmType(row.monetary, 'Monetary')" effect="plain">
                                M: ${{ row.monetary.toLocaleString() }}
                            </el-tag>
                        </el-tooltip>
                    </div>
                </template>
            </el-table-column>

            <el-table-column label="Actions" width="160" fixed="right" align="center">
                <template #default="{ row }">
                    <el-button type="primary" link icon="Edit" @click="handleEdit(row)">Edit</el-button>
                    <el-button type="danger" link icon="Delete" @click="handleDelete(row)">Delete</el-button>
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
        :title="isEdit ? 'Edit Doctor Profile' : 'Create New Doctor'"
        width="500px"
        destroy-on-close
    >
        <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
            <el-form-item label="NPI" prop="npi">
                <el-input v-model="form.npi" :disabled="isEdit" placeholder="10-digit NPI" />
            </el-form-item>
             <el-form-item label="First Name" prop="first_name">
                <el-input v-model="form.first_name" placeholder="John" />
            </el-form-item>
             <el-form-item label="Last Name" prop="last_name">
                <el-input v-model="form.last_name" placeholder="Doe" />
            </el-form-item>
            <el-form-item label="Specialty" prop="specialty">
                <el-select v-model="form.specialty" filterable allow-create default-first-option placeholder="Select or type..." style="width: 100%">
                     <el-option v-for="s in specialties" :key="s" :label="s" :value="s" />
                </el-select>
            </el-form-item>
             <el-form-item label="State" prop="state">
                <el-select v-model="form.state" filterable placeholder="Select state" style="width: 100%">
                     <el-option v-for="s in states" :key="s" :label="s" :value="s" />
                </el-select>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="dialogVisible = false">Cancel</el-button>
            <el-button type="primary" :loading="submitting" @click="submitForm">
                {{ isEdit ? 'Update' : 'Create' }}
            </el-button>
        </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Plus, Edit, Delete, Location } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { 
    getDoctors, 
    deleteDoctor, 
    createDoctor, 
    updateDoctor, 
    getSpecialties,
    getStates,
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
    specialty: '',
    state: ''
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
        { required: true, message: 'Please input NPI', trigger: 'blur' },
        { min: 10, max: 10, message: 'NPI must be exactly 10 digits', trigger: 'blur' },
        { pattern: /^\d+$/, message: 'NPI must contain only digits', trigger: 'blur' }
    ],
    first_name: [{ required: true, message: 'First name is required', trigger: 'blur' }],
    last_name: [{ required: true, message: 'Last name is required', trigger: 'blur' }]
})

// -- Methods --

const fetchData = async () => {
    loading.value = true
    try {
        const res = await getDoctors({
            page: pagination.page,
            page_size: pagination.pageSize,
            specialty: filters.specialty || undefined,
            state: filters.state || undefined,
            search: filters.search || undefined
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
    filters.specialty = ''
    filters.state = ''
    handleFilter()
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
        `Are you sure you want to permanently delete Dr. ${row.first_name} ${row.last_name}?`,
        'Confirm Deletion',
        {
            confirmButtonText: 'Delete',
            cancelButtonText: 'Cancel',
            type: 'warning',
        }
    ).then(async () => {
        try {
            await deleteDoctor(row.npi)
            ElMessage.success('Doctor deleted successfully')
            fetchData()
        } catch (error) {
            // Error managed by interceptor
            if(error && (error as any).response?.status === 404) {
                 ElMessage.error('Doctor not found, maybe already deleted')
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
                    ElMessage.success('Doctor info updated')
                } else {
                    await createDoctor(form)
                    ElMessage.success('New doctor created')
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

/* Filter Bar */
.filter-card {
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    background-color: var(--card);
}

.filter-form {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
}

.filter-form :deep(.el-form-item) {
    margin-bottom: 0px; 
    margin-right: 0px;
}

.filter-actions {
    margin-left: auto; /* Push actions to the right */
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

.location-text {
    font-size: 13px;
    color: var(--text-color-secondary);
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 4px;
}

.rfm-tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.pagination-container {
    display: flex;
    justify-content: flex-end;
    padding: 8px 0;
}
</style>
