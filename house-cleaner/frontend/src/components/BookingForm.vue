<template>
  <div class="card booking-form">
    <h3>{{ title }}</h3>
    <form @submit.prevent="submit">
      <!-- Service Selection -->
      <label>
        Service Package
        <select v-model="service_id" @change="onServiceChange" required>
          <option value="" disabled>-- Select a service --</option>
          <option v-for="s in services" :key="s.id" :value="s.id">
            {{ s.name }} - {{ formatPrice(s.price) }} ({{ s.duration_mins }} min)
          </option>
        </select>
        <small v-if="services.length === 0 && !loadingServices" class="error-text">No services available. Please contact support.</small>
        <small v-if="loadingServices" class="text-muted">Loading services...</small>
        <span v-if="selectedService" class="service-description">{{ selectedService.description }}</span>
      </label>

      <!-- Areas Selection -->
      <label>
        Areas to Clean (select all that apply)
        <div class="areas-grid">
          <label v-for="area in availableAreas" :key="area" class="area-checkbox">
            <input
              type="checkbox"
              :value="area"
              v-model="selectedAreas"
              @change="calculatePrice"
            />
            <span>{{ area }}</span>
          </label>
        </div>
        <small v-if="selectedAreas.length === 0" class="error-text">Please select at least one area</small>
      </label>

      <!-- Date & Time Selection -->
      <TimeSlotPicker
        v-model="start_datetime"
        :service-duration="selectedService?.duration_mins || 60"
        :slot-duration="30"
        :business-hours-start="8"
        :business-hours-end="19"
        :min-lead-time-hours="3"
      />

      <!-- Address -->
      <label>
        Service Address
        <input 
          v-model="address" 
          type="text" 
          placeholder="123 Main St, City, State"
          required
        />
      </label>

      <!-- Payment Method -->
      <label>
        Payment Method
        <select v-model="payment_method" required>
          <option value="cash">Cash on Arrival</option>
          <option value="cod">Cash on Delivery</option>
          <option value="online">Online Payment</option>
        </select>
      </label>

      <!-- Notes -->
      <label>
        Additional Notes (optional)
        <textarea 
          v-model="notes" 
          placeholder="Special instructions, gate codes, preferred cleaning products, etc."
          rows="4"
        />
      </label>

      <!-- Price Breakdown -->
      <div v-if="selectedService && selectedAreas.length > 0" class="price-breakdown">
        <h4>Price Breakdown</h4>
        <div class="price-row">
          <span>Base Price ({{ selectedService.name }})</span>
          <span>{{ formatPrice(selectedService.price) }}</span>
        </div>
        <div v-if="areaExtra > 0" class="price-row">
          <span>Additional Areas ({{ selectedAreas.length - 1 }} × $10)</span>
          <span>{{ formatPrice(areaExtra) }}</span>
        </div>
        <div class="price-row subtotal">
          <span>Subtotal</span>
          <span>{{ formatPrice(subtotal) }}</span>
        </div>
        <div class="price-row">
          <span>Tax (8%)</span>
          <span>{{ formatPrice(tax) }}</span>
        </div>
        <div class="price-row total">
          <span><strong>Total</strong></span>
          <span><strong>{{ formatPrice(priceTotal) }}</strong></span>
        </div>
      </div>

      <div class="actions">
        <button 
          type="submit" 
          class="btn btn-primary" 
          :disabled="!canSubmit || loading"
        >
          {{ loading ? 'Creating Booking...' : 'Create Booking' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import TimeSlotPicker from './TimeSlotPicker.vue'

export default {
  components: { TimeSlotPicker },
  props: { 
    title: { type: String, default: 'Create Booking' },
    booking: { type: Object, default: null } // For editing existing booking
  },
  emits: ['created'],
  setup(props, { emit }) {
    const services = ref([])
    const service_id = ref(null)
    const start_datetime = ref('')
    const address = ref('')
    const notes = ref('')
    const payment_method = ref('cash')
    const selectedAreas = ref([])
    const loading = ref(false)
    const loadingServices = ref(true)

    // Available areas to select from
    const availableAreas = ['Bathroom', 'Kitchen', 'Living Room', 'Bedroom(s)', 'Balcony', 'Other']

    // Calculate price breakdown
    const selectedService = computed(() => {
      return services.value.find(s => s.id === service_id.value)
    })

    const areaExtra = computed(() => {
      const extraCount = Math.max(0, selectedAreas.value.length - 1)
      return extraCount * 10 // $10 per additional area
    })

    const subtotal = computed(() => {
      if (!selectedService.value) return 0
      return selectedService.value.price + areaExtra.value
    })

    const tax = computed(() => {
      return subtotal.value * 0.08
    })

    const priceTotal = computed(() => {
      return subtotal.value + tax.value
    })

    const canSubmit = computed(() => {
      return service_id.value && 
             start_datetime.value && 
             address.value && 
             selectedAreas.value.length > 0 &&
             payment_method.value
    })

    function formatPrice(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }

    function calculatePrice() {
      // Price is computed, this is just a trigger function if needed
    }

    function onServiceChange() {
      calculatePrice()
    }

    async function fetchServices() {
      loadingServices.value = true
      try {
        const res = await api.get('/services')
        const servicesData = res.data?.data || res.data?.services || []
        
        // Show all services (backend already filters by active if column exists)
        services.value = servicesData
        
        if (props.booking?.service_id) {
          service_id.value = props.booking.service_id
        }
        // Don't auto-select - let user choose
      } catch (err) {
        console.error('Failed to fetch services:', err)
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message || 'Unknown error'
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Failed to load services: ' + errorMsg, type: 'error' } 
        }))
      } finally {
        loadingServices.value = false
      }
    }
    
    async function submit() {
      if (!canSubmit.value) {
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Please fill in all required fields', type: 'error' } 
        }))
        return
      }

      loading.value = true
      try {
        const payload = {
          service_id: service_id.value,
          start_datetime: start_datetime.value,
          address: address.value,
          areas: selectedAreas.value,
          payment_method: payment_method.value,
          notes: notes.value
        }

        let response
        if (props.booking?.id) {
          // Update existing booking
          response = await api.put(`/bookings/${props.booking.id}`, payload)
        } else {
          // Create new booking
          response = await api.post('/bookings', payload)
        }

        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: props.booking ? 'Booking updated successfully' : 'Booking created successfully', type: 'success' } 
        }))
        emit('created')
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message || 'Operation failed'
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: errorMsg, type: 'error' } 
        }))
      } finally {
        loading.value = false
      }
    }

    // Initialize form if editing
    onMounted(() => {
      fetchServices()
      if (props.booking) {
        service_id.value = props.booking.service_id
        start_datetime.value = props.booking.start_datetime
        address.value = props.booking.address || ''
        notes.value = props.booking.notes || ''
        payment_method.value = props.booking.payment_method || 'cash'
        selectedAreas.value = props.booking.areas || []
      }
    })

    return {
      loadingServices,
      services,
      service_id,
      start_datetime,
      address,
      notes,
      payment_method,
      selectedAreas,
      availableAreas,
      selectedService,
      areaExtra,
      subtotal,
      tax,
      priceTotal,
      loading,
      canSubmit,
      formatPrice,
      calculatePrice,
      onServiceChange,
      submit
    }
  }
}
</script>

<style scoped>
.booking-form {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.card h3 {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: var(--spacing-md);
  font-weight: 600;
  color: #1f2937 !important;
  font-size: var(--font-size-base);
}

.service-description {
  display: block;
  margin-top: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: #6b7280 !important;
  font-weight: normal;
}

.areas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
}

.area-checkbox {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-base);
  font-weight: normal;
  background: #ffffff;
  color: #1f2937 !important;
}

.area-checkbox span {
  color: #1f2937 !important;
}

.area-checkbox:hover {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.05);
}

.area-checkbox input[type="checkbox"] {
  width: auto;
  margin: 0;
  cursor: pointer;
}

.area-checkbox input[type="checkbox"]:checked + span {
  font-weight: 600;
  color: var(--color-primary);
}

.error-text {
  display: block;
  color: #ef4444 !important;
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
  font-weight: 500;
}

select,
textarea,
input[type="text"],
input[type="date"] {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
  transition: all var(--transition-base);
  background: #ffffff !important;
  color: #1f2937 !important;
}

select:focus,
textarea:focus,
input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background: #ffffff !important;
  color: #1f2937 !important;
}

select {
  cursor: pointer;
  background: #ffffff !important;
  color: #1f2937 !important;
}

select option {
  background: #ffffff !important;
  color: #1f2937 !important;
  padding: 0.5rem;
}

textarea {
  min-height: 100px;
  resize: vertical;
  font-family: var(--font-family);
  background: #ffffff !important;
  color: #1f2937 !important;
}

textarea::placeholder {
  color: #6b7280 !important;
  opacity: 1;
}

input::placeholder {
  color: #6b7280 !important;
  opacity: 1;
}

.price-breakdown {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: #f9fafb;
  border-radius: var(--border-radius-lg);
  border: 2px solid var(--border-color);
}

.price-breakdown h4 {
  margin: 0 0 var(--spacing-md) 0;
  font-size: var(--font-size-lg);
  color: #1f2937 !important;
}

.price-breakdown .price-row {
  color: #374151 !important;
}

.price-breakdown .price-row.total {
  color: #1f2937 !important;
}

.price-breakdown .price-row.total strong {
  color: #1f2937 !important;
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--border-color);
}

.price-row:last-child {
  border-bottom: none;
}

.price-row.subtotal {
  border-top: 2px solid var(--border-color);
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-md);
  font-weight: 600;
}

.price-row.total {
  border-top: 2px solid var(--color-primary);
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-md);
  font-size: var(--font-size-lg);
}

.actions {
  margin-top: var(--spacing-xl);
}

.actions .btn-primary {
  width: 100%;
  padding: var(--spacing-lg);
  font-size: var(--font-size-lg);
  font-weight: 600;
}

.actions .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .areas-grid {
    grid-template-columns: 1fr;
  }
}
</style>
