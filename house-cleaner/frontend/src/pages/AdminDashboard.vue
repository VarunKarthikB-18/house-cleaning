<template>
  <div class="admin-dashboard">
    <h2>Admin Dashboard</h2>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else>
      <!-- Statistics Cards -->
      <div class="stats-grid">
        <div class="stat-card" v-for="(value, key) in stats" :key="key">
          <div class="stat-icon">{{ getStatIcon(key) }}</div>
          <div class="stat-content">
            <h3>{{ value }}</h3>
            <p>{{ formatStatLabel(key) }}</p>
          </div>
        </div>
      </div>

      <!-- Tabs for different sections -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="['tab-btn', { active: activeTab === tab.id }]"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Bookings Tab -->
      <div v-if="activeTab === 'bookings'" class="tab-content">
        <div class="section-header">
          <h3>All Bookings</h3>
          <button class="btn btn-primary btn-sm" @click="fetchAll">Refresh</button>
        </div>
        <div v-if="bookings.length === 0" class="empty">No bookings found</div>
        <div v-else class="bookings-table-wrapper">
          <table class="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Service</th>
                <th>Date & Time</th>
                <th>Status</th>
                <th>Cleaner</th>
                <th>Price</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <AdminBookingRow 
                v-for="b in bookings" 
                :key="b.id" 
                :booking="b" 
                @updated="fetchAll" 
              />
            </tbody>
          </table>
        </div>
      </div>

      <!-- Services Tab -->
      <div v-if="activeTab === 'services'" class="tab-content">
        <div class="section-header">
          <h3>Service Management</h3>
          <button class="btn btn-primary btn-sm" @click="showServiceForm = true">+ Add Service</button>
        </div>
        
        <div v-if="loadingServices" class="loading">Loading services...</div>
        <div v-else>
          <div v-if="services.length === 0" class="empty">No services found</div>
          <div v-else class="services-grid">
            <div v-for="service in services" :key="service.id" class="service-card card">
              <div class="service-header">
                <h4>{{ service.name }}</h4>
                <span :class="['status-badge', service.active !== false ? 'active' : 'inactive']">
                  {{ service.active !== false ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="service-details">
                <p><strong>Duration:</strong> {{ service.duration_mins }} minutes</p>
                <p><strong>Price:</strong> ${{ service.price.toFixed(2) }}</p>
                <p v-if="service.description"><strong>Description:</strong> {{ service.description }}</p>
              </div>
              <div class="service-actions">
                <button class="btn btn-secondary btn-sm" @click="editService(service)">Edit</button>
                <button class="btn btn-danger btn-sm" @click="deleteService(service.id)">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Service Form Modal -->
      <div v-if="showServiceForm" class="modal-overlay" @click.self="closeServiceForm">
        <div class="modal-content card">
          <div class="modal-header">
            <h3>{{ editingService ? 'Edit Service' : 'Add New Service' }}</h3>
            <button class="close-btn" @click="closeServiceForm">×</button>
          </div>
          <form @submit.prevent="saveService">
            <label>
              Service Name
              <input v-model="serviceForm.name" type="text" required placeholder="e.g., Basic Clean" />
            </label>
            <label>
              Duration (minutes)
              <input v-model.number="serviceForm.duration_mins" type="number" required min="15" step="15" />
            </label>
            <label>
              Price ($)
              <input v-model.number="serviceForm.price" type="number" required min="0" step="0.01" />
            </label>
            <label>
              Description
              <textarea v-model="serviceForm.description" placeholder="Service description..."></textarea>
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="serviceForm.active" />
              Active (available for booking)
            </label>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="closeServiceForm">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="savingService">
                {{ savingService ? 'Saving...' : 'Save Service' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import AdminBookingRow from '../components/AdminBookingRow.vue'

export default {
  components: { AdminBookingRow },
  setup() {
    const bookings = ref([])
    const services = ref([])
    const stats = ref({ pending: 0, confirmed: 0, in_progress: 0, completed: 0 })
    const loading = ref(true)
    const loadingServices = ref(false)
    const activeTab = ref('bookings')
    const showServiceForm = ref(false)
    const editingService = ref(null)
    const savingService = ref(false)
    
    const tabs = [
      { id: 'bookings', label: 'Bookings' },
      { id: 'services', label: 'Services' }
    ]

    const serviceForm = ref({
      name: '',
      duration_mins: 60,
      price: 50.0,
      description: '',
      active: true
    })

    function getStatIcon(key) {
      const icons = {
        pending: '⏳',
        confirmed: '✅',
        in_progress: '🔄',
        completed: '✨'
      }
      return icons[key] || '📊'
    }

    function formatStatLabel(key) {
      return key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    async function fetchAll() {
      loading.value = true
      try {
        const [bRes, sRes] = await Promise.all([
          api.get('/admin/bookings'),
          api.get('/admin/stats')
        ])
        bookings.value = bRes.data?.data || bRes.data?.bookings || []
        
        // Handle stats response format
        const statsData = sRes.data?.data || sRes.data || {}
        if (statsData.counts) {
          // Backend returns { counts: { pending: X, confirmed: Y, ... } }
          stats.value = statsData.counts
        } else {
          // Fallback to direct stats object
          stats.value = statsData
        }
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Failed to load admin data: ' + errorMsg, type: 'error' } 
        }))
      } finally { 
        loading.value = false 
      }
    }

    async function fetchServices() {
      loadingServices.value = true
      try {
        const res = await api.get('/services')
        services.value = res.data?.data || res.data?.services || []
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Failed to load services: ' + errorMsg, type: 'error' } 
        }))
      } finally {
        loadingServices.value = false
      }
    }

    function editService(service) {
      editingService.value = service
      serviceForm.value = {
        name: service.name,
        duration_mins: service.duration_mins,
        price: service.price,
        description: service.description || '',
        active: service.active !== false
      }
      showServiceForm.value = true
    }

    function closeServiceForm() {
      showServiceForm.value = false
      editingService.value = null
      serviceForm.value = {
        name: '',
        duration_mins: 60,
        price: 50.0,
        description: '',
        active: true
      }
    }

    async function saveService() {
      savingService.value = true
      try {
        if (editingService.value) {
          await api.put(`/services/${editingService.value.id}`, serviceForm.value)
          window.dispatchEvent(new CustomEvent('toast', { 
            detail: { message: 'Service updated successfully', type: 'success' } 
          }))
        } else {
          await api.post('/services', serviceForm.value)
          window.dispatchEvent(new CustomEvent('toast', { 
            detail: { message: 'Service created successfully', type: 'success' } 
          }))
        }
        closeServiceForm()
        fetchServices()
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Failed to save service: ' + errorMsg, type: 'error' } 
        }))
      } finally {
        savingService.value = false
      }
    }

    async function deleteService(serviceId) {
      if (!confirm('Are you sure you want to delete this service? This action cannot be undone.')) {
        return
      }
      try {
        await api.delete(`/services/${serviceId}`)
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Service deleted successfully', type: 'success' } 
        }))
        fetchServices()
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Failed to delete service: ' + errorMsg, type: 'error' } 
        }))
      }
    }

    onMounted(() => {
      fetchAll()
      fetchServices()
    })

    return {
      bookings,
      services,
      stats,
      loading,
      loadingServices,
      activeTab,
      tabs,
      showServiceForm,
      editingService,
      savingService,
      serviceForm,
      getStatIcon,
      formatStatLabel,
      fetchAll,
      fetchServices,
      editService,
      closeServiceForm,
      saveService,
      deleteService
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  width: 100%;
}

h2 {
  background: var(--gradient-secondary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--shadow);
  border-left: 4px solid var(--primary);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary);
  border-radius: var(--radius);
  flex-shrink: 0;
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937 !important;
  margin: 0;
}

.stat-content p {
  color: #6b7280 !important;
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--border);
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: #6b7280;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.tab-btn:hover {
  color: var(--primary);
}

.tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.tab-content {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937 !important;
}

.bookings-table-wrapper {
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow);
}

.admin-table th,
.admin-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
  color: #1f2937 !important;
}

.admin-table th {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
  font-weight: 700;
  color: #1f2937 !important;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.service-card {
  padding: 1.5rem;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.service-header h4 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937 !important;
  margin: 0;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: var(--gradient-success);
  color: white;
}

.status-badge.inactive {
  background: var(--gradient-danger);
  color: white;
}

.service-details {
  margin-bottom: 1rem;
}

.service-details p {
  color: #374151 !important;
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.service-actions {
  display: flex;
  gap: 0.5rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal-content {
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937 !important;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6b7280;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-content form label {
  display: block;
  margin-bottom: 1rem;
  color: #1f2937 !important;
  font-weight: 600;
}

.modal-content form input,
.modal-content form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 1rem;
  background: #ffffff !important;
  color: #1f2937 !important;
  margin-top: 0.5rem;
}

.modal-content form textarea {
  min-height: 100px;
  resize: vertical;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
  transform: scale(1.2);
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.empty {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%);
  color: #6b7280 !important;
  padding: 3rem 2rem;
  margin: 2rem 0;
  text-align: center;
  border-radius: var(--radius-lg);
  border: 2px dashed var(--border);
  font-size: 1.1rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .admin-table {
    font-size: 0.875rem;
  }
  
  .admin-table th,
  .admin-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .modal-overlay {
    padding: 1rem;
  }
}
</style>
