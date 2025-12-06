<template>
  <div class="cleaner-card" :class="{ inactive: !cleaner.active }">
    <div class="cleaner-header">
      <div class="cleaner-info">
        <h3>{{ cleaner.name }}</h3>
        <p class="cleaner-phone">📞 {{ cleaner.phone || 'No phone' }}</p>
      </div>
      <div class="cleaner-status">
        <span :class="['status-badge', cleaner.active ? 'active' : 'inactive']">
          {{ cleaner.active ? 'Active' : 'Inactive' }}
        </span>
      </div>
    </div>
    
    <div v-if="upcomingBookings.length > 0" class="upcoming-bookings">
      <h4>Upcoming Bookings ({{ upcomingBookings.length }})</h4>
      <ul class="bookings-list">
        <li v-for="booking in upcomingBookings.slice(0, 3)" :key="booking.id" class="booking-item">
          <span class="booking-date">{{ formatDate(booking.start_datetime) }}</span>
          <span class="booking-service">{{ booking.service?.name }}</span>
        </li>
      </ul>
      <p v-if="upcomingBookings.length > 3" class="more-bookings">
        +{{ upcomingBookings.length - 3 }} more booking(s)
      </p>
    </div>
    <div v-else class="no-bookings">
      No upcoming bookings
    </div>
    
    <div v-if="isAdmin" class="cleaner-actions">
      <button 
        class="btn btn-sm" 
        :class="cleaner.active ? 'btn-secondary' : 'btn-success'"
        @click="$emit('toggle-active')"
      >
        {{ cleaner.active ? 'Deactivate' : 'Activate' }}
      </button>
      <button class="btn btn-sm btn-secondary" @click="$emit('edit')">
        Edit
      </button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import * as auth from '../services/auth'

export default {
  props: {
    cleaner: {
      type: Object,
      required: true
    },
    bookings: {
      type: Array,
      default: () => []
    }
  },
  emits: ['toggle-active', 'edit'],
  setup(props) {
    const isAdmin = computed(() => {
      return auth.currentUser.value?.role === 'admin'
    })

    // Filter and sort upcoming bookings for this cleaner
    const upcomingBookings = computed(() => {
      if (!props.bookings || props.bookings.length === 0) return []
      
      const now = new Date()
      return props.bookings
        .filter(b => 
          b.cleaner_id === props.cleaner.id && 
          b.status !== 'cancelled' &&
          new Date(b.start_datetime) > now
        )
        .sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime))
    })

    function formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      })
    }

    return {
      isAdmin,
      upcomingBookings,
      formatDate
    }
  }
}
</script>

<style scoped>
.cleaner-card {
  background: var(--bg-card);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow);
  border: 2px solid var(--border-color);
  transition: all var(--transition-base);
}

.cleaner-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.cleaner-card.inactive {
  opacity: 0.7;
  background: var(--bg-subtle);
}

.cleaner-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--border-color);
}

.cleaner-info h3 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-text);
}

.cleaner-phone {
  margin: 0;
  color: var(--color-text-light);
  font-size: var(--font-size-sm);
}

.cleaner-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
}

.status-badge.inactive {
  background: rgba(107, 114, 128, 0.2);
  color: var(--color-gray-600);
}

.upcoming-bookings {
  margin-top: var(--spacing-md);
}

.upcoming-bookings h4 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--color-text);
}

.bookings-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.booking-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
  background: var(--bg-subtle);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.booking-date {
  font-weight: 600;
  color: var(--color-text);
}

.booking-service {
  color: var(--color-text-light);
}

.more-bookings {
  margin: var(--spacing-sm) 0 0 0;
  text-align: center;
  color: var(--color-text-light);
  font-size: var(--font-size-sm);
  font-style: italic;
}

.no-bookings {
  padding: var(--spacing-md);
  text-align: center;
  color: var(--color-text-light);
  font-size: var(--font-size-sm);
  font-style: italic;
  background: var(--bg-subtle);
  border-radius: var(--border-radius);
}

.cleaner-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 2px solid var(--border-color);
}

.btn-sm {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  flex: 1;
}

@media (max-width: 768px) {
  .cleaner-header {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .cleaner-actions {
    flex-direction: column;
  }
}
</style>

