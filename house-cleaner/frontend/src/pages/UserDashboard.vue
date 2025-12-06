<template>
  <div class="user-dashboard">
    <h2>Dashboard</h2>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else>
      <!-- Statistics Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <div class="stat-content">
            <h3>{{ stats.totalBookings }}</h3>
            <p>Total Bookings</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏳</div>
          <div class="stat-content">
            <h3>{{ stats.pendingBookings }}</h3>
            <p>Pending</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <h3>{{ stats.completedBookings }}</h3>
            <p>Completed</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <h3>{{ formatPrice(stats.totalSpent) }}</h3>
            <p>Total Spent</p>
          </div>
        </div>
      </div>

      <!-- Chart Section -->
      <div class="chart-section card">
        <h3>Booking Status Overview</h3>
        <div class="chart-container">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </div>

      <!-- Recent Bookings -->
      <div class="recent-bookings">
        <h3>Recent Bookings</h3>
        <div v-if="bookings.length === 0" class="empty">No bookings yet. <router-link to="/bookings/new">Book now</router-link></div>
        <div v-else class="bookings-list">
          <BookingCard v-for="b in recentBookings" :key="b.id" :booking="b" @cancelled="fetchBookings" />
        </div>
        <div class="actions">
          <router-link class="btn btn-primary" to="/bookings">View All Bookings</router-link>
          <router-link class="btn btn-secondary" to="/bookings/new">New Booking</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'
import api from '../services/api'
import BookingCard from '../components/BookingCard.vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  components: { BookingCard },
  setup() {
    const bookings = ref([])
    const loading = ref(true)
    const chartCanvas = ref(null)
    let chartInstance = null

    const stats = computed(() => {
      const total = bookings.value.length
      const pending = bookings.value.filter(b => b.status === 'pending').length
      const confirmed = bookings.value.filter(b => b.status === 'confirmed').length
      const completed = bookings.value.filter(b => b.status === 'completed').length
      const cancelled = bookings.value.filter(b => b.status === 'cancelled').length
      const totalSpent = bookings.value
        .filter(b => b.status === 'completed')
        .reduce((sum, b) => sum + (b.price_total || 0), 0)

      return {
        totalBookings: total,
        pendingBookings: pending,
        confirmedBookings: confirmed,
        completedBookings: completed,
        cancelledBookings: cancelled,
        totalSpent
      }
    })

    const recentBookings = computed(() => {
      return bookings.value
        .sort((a, b) => new Date(b.start_datetime) - new Date(a.start_datetime))
        .slice(0, 3)
    })

    function formatPrice(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }

    function renderChart() {
      if (!chartCanvas.value) return

      // Destroy existing chart
      if (chartInstance) {
        chartInstance.destroy()
      }

      const ctx = chartCanvas.value.getContext('2d')
      chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Pending', 'Confirmed', 'Completed', 'Cancelled'],
          datasets: [{
            data: [
              stats.value.pendingBookings,
              stats.value.confirmedBookings,
              stats.value.completedBookings,
              stats.value.cancelledBookings
            ],
            backgroundColor: [
              'rgba(245, 158, 11, 0.8)',
              'rgba(16, 185, 129, 0.8)',
              'rgba(59, 130, 246, 0.8)',
              'rgba(239, 68, 68, 0.8)'
            ],
            borderColor: [
              'rgb(245, 158, 11)',
              'rgb(16, 185, 129)',
              'rgb(59, 130, 246)',
              'rgb(239, 68, 68)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 15,
                font: {
                  size: 14
                }
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const label = context.label || ''
                  const value = context.parsed || 0
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0
                  return `${label}: ${value} (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }

    async function fetchBookings() {
      loading.value = true
      try {
        const res = await api.get('/bookings')
        bookings.value = res.data?.data || res.data?.bookings || []
        await nextTick()
        renderChart()
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || err.message
        window.dispatchEvent(new CustomEvent('toast', { 
          detail: { message: 'Failed to load bookings: ' + errorMsg, type: 'error' } 
        }))
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchBookings()
    })

    return {
      bookings,
      loading,
      stats,
      recentBookings,
      chartCanvas,
      formatPrice,
      fetchBookings
    }
  }
}
</script>

<style scoped>
.user-dashboard {
  width: 100%;
}

h2 {
  background: var(--gradient-primary);
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
  color: #1f2937;
  margin: 0;
}

.stat-content p {
  color: #6b7280;
  margin: 0.25rem 0 0 0;
  font-size: 0.9rem;
}

.chart-section {
  margin-bottom: 2rem;
  padding: 2rem;
}

.chart-section h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1.5rem;
  text-align: center;
}

.chart-container {
  max-width: 500px;
  margin: 0 auto;
  height: 300px;
}

.recent-bookings {
  margin-top: 2rem;
}

.recent-bookings h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
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

.empty a {
  color: var(--primary);
  font-weight: 700;
  text-decoration: none;
}

.empty a:hover {
  text-decoration: underline;
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
  
  .chart-container {
    height: 250px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .actions .btn {
    width: 100%;
  }
}
</style>
