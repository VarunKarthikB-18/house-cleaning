<template>
  <div class="card booking-card" :class="statusClass">
    <div class="booking-content">
      <router-link :to="`/bookings/${booking.id}`" class="booking-link">
        <div class="booking-main">
          <div class="service-badge">
            <span class="service-icon">🧹</span>
          </div>
          <div class="booking-info">
            <strong class="service-name">{{ booking.service_name || booking.service?.name || 'Service' }}</strong>
            <div class="meta">
              <span class="meta-item">📅 {{ formatDate(booking.start_datetime) }}</span>
              <span class="status-badge" :class="statusBadgeClass">{{ booking.status }}</span>
            </div>
            <div v-if="booking.cleaner" class="cleaner-info">
              <span>Cleaner: {{ booking.cleaner.name }}</span>
            </div>
            <div v-if="booking.price_total" class="price-info">
              <strong>{{ formatPrice(booking.price_total) }}</strong>
            </div>
          </div>
        </div>
      </router-link>
      <div class="actions" @click.stop>
        <button class="btn btn-danger btn-sm" @click="cancel" v-if="canCancel">Cancel</button>
        <router-link :to="`/bookings/${booking.id}`" class="btn btn-primary btn-sm">View Details</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'
import { computed } from 'vue'

export default {
  props: { booking: Object },
  emits: ['cancelled'],
  setup(props, { emit }) {
    const canCancel = computed(() => props.booking?.status === 'pending')
    
    const statusClass = computed(() => {
      const status = props.booking?.status?.toLowerCase()
      if (status === 'confirmed') return 'status-confirmed'
      if (status === 'completed') return 'status-completed'
      if (status === 'cancelled') return 'status-cancelled'
      return 'status-pending'
    })
    
    const statusBadgeClass = computed(() => {
      const status = props.booking?.status?.toLowerCase()
      return `badge-${status || 'pending'}`
    })
    
    function formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        weekday: 'short',
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    function formatPrice(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }

    async function cancel() {
      if (!confirm('Cancel this booking?')) return
      try {
        await api.delete(`/bookings/${props.booking.id}`)
        window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Booking cancelled', type: 'success' } }))
        emit('cancelled')
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message
        window.dispatchEvent(new CustomEvent('toast', { detail: { message: 'Failed to cancel: ' + errorMsg, type: 'error' } }))
      }
    }
    
    return { canCancel, statusClass, statusBadgeClass, formatDate, formatPrice, cancel }
  }
}
</script>

<style scoped>
.booking-card {
  margin-bottom: 1rem;
  padding: 1.5rem;
  background: var(--bg-card);
  border-left: 4px solid var(--primary);
  transition: all 0.3s ease;
}

.booking-card.status-confirmed {
  border-left-color: var(--success);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, var(--bg-card) 100%);
}

.booking-card.status-completed {
  border-left-color: var(--info);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, var(--bg-card) 100%);
}

.booking-card.status-cancelled {
  border-left-color: var(--danger);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, var(--bg-card) 100%);
}

.booking-card.status-pending {
  border-left-color: var(--warning);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, var(--bg-card) 100%);
}

.booking-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.booking-link {
  flex: 1;
  text-decoration: none;
  color: inherit;
}

.booking-link:hover {
  opacity: 0.9;
}

.cleaner-info {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-light);
}

.price-info {
  margin-top: 0.5rem;
  font-size: 1.125rem;
  color: var(--primary);
}

.booking-main {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.service-badge {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-lg);
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.service-icon {
  font-size: 1.8rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.booking-info {
  flex: 1;
}

.service-name {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  color: var(--text-light);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-pending {
  background: linear-gradient(135deg, var(--warning-light) 0%, var(--warning) 100%);
  color: #ffffff;
}

.badge-confirmed {
  background: linear-gradient(135deg, var(--success-light) 0%, var(--success) 100%);
  color: #ffffff;
}

.badge-completed {
  background: linear-gradient(135deg, var(--info-light) 0%, var(--info) 100%);
  color: #ffffff;
}

.badge-cancelled {
  background: linear-gradient(135deg, var(--danger-light) 0%, var(--danger) 100%);
  color: #ffffff;
}

.actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.actions .btn-sm {
  white-space: nowrap;
}

@media (max-width: 768px) {
  .booking-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .actions {
    width: 100%;
  }
  
  .actions .btn {
    flex: 1;
  }
  
  .booking-main {
    flex-direction: column;
    text-align: center;
  }
}
</style>
