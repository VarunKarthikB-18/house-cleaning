<template>
  <div v-if="loading" class="loading">Loading booking details...</div>
  <div v-else-if="error" class="error-message">{{ error }}</div>
  <div v-else-if="booking" class="booking-detail">
    <div class="detail-header">
      <h1>Booking Details</h1>
      <router-link to="/bookings" class="btn btn-secondary">← Back to Bookings</router-link>
    </div>

    <div class="detail-content">
      <!-- Booking Information Card -->
      <div class="card detail-card">
        <h2>Booking Information</h2>
        
        <div class="info-grid">
          <div class="info-item">
            <label>Service</label>
            <div class="value">{{ booking.service?.name || 'N/A' }}</div>
          </div>
          
          <div class="info-item">
            <label>Status</label>
            <span :class="['status-badge', `status-${booking.status}`]">
              {{ booking.status }}
            </span>
          </div>
          
          <div class="info-item">
            <label>Date & Time</label>
            <div class="value">{{ formatDateTime(booking.start_datetime) }}</div>
            <div class="value-sub">{{ formatDuration(booking.start_datetime, booking.end_datetime) }}</div>
          </div>
          
          <div class="info-item">
            <label>Cleaner</label>
            <div class="value">{{ booking.cleaner?.name || 'Not assigned yet' }}</div>
            <div v-if="booking.cleaner?.phone" class="value-sub">📞 {{ booking.cleaner.phone }}</div>
          </div>
          
          <div class="info-item">
            <label>Address</label>
            <div class="value">{{ booking.address || 'N/A' }}</div>
          </div>
          
          <div class="info-item">
            <label>Payment Method</label>
            <div class="value">{{ formatPaymentMethod(booking.payment_method) }}</div>
          </div>
          
          <div v-if="booking.areas && booking.areas.length > 0" class="info-item full-width">
            <label>Areas to Clean</label>
            <div class="areas-list">
              <span v-for="area in booking.areas" :key="area" class="area-tag">{{ area }}</span>
            </div>
          </div>
          
          <div v-if="booking.notes" class="info-item full-width">
            <label>Notes</label>
            <div class="value notes-text">{{ booking.notes }}</div>
          </div>
        </div>

        <!-- Price Breakdown -->
        <div class="price-section">
          <h3>Price Breakdown</h3>
          <div class="price-breakdown">
            <div class="price-row">
              <span>Base Price</span>
              <span>{{ formatPrice(booking.service?.price || 0) }}</span>
            </div>
            <div v-if="booking.areas && booking.areas.length > 1" class="price-row">
              <span>Additional Areas ({{ booking.areas.length - 1 }} × $10)</span>
              <span>{{ formatPrice((booking.areas.length - 1) * 10) }}</span>
            </div>
            <div class="price-row subtotal">
              <span>Subtotal</span>
              <span>{{ formatPrice(calculateSubtotal()) }}</span>
            </div>
            <div class="price-row">
              <span>Tax (8%)</span>
              <span>{{ formatPrice(calculateTax()) }}</span>
            </div>
            <div class="price-row total">
              <span><strong>Total</strong></span>
              <span><strong>{{ formatPrice(booking.price_total || 0) }}</strong></span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div v-if="canEdit" class="actions">
          <router-link :to="`/bookings/${booking.id}/edit`" class="btn btn-primary">
            Edit Booking
          </router-link>
          <button v-if="canCancel" class="btn btn-danger" @click="cancelBooking">
            Cancel Booking
          </button>
        </div>
      </div>

      <!-- Review Section -->
      <div v-if="booking.status === 'completed'" class="card review-section">
        <h2>Review</h2>
        
        <div v-if="existingReview" class="existing-review">
          <div class="review-rating">
            <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= existingReview.rating }">
              ⭐
            </span>
            <span class="rating-value">{{ existingReview.rating }}/5</span>
          </div>
          <p class="review-comment">{{ existingReview.comment }}</p>
          <div class="review-date">
            Reviewed on {{ formatDate(existingReview.created_at) }}
          </div>
        </div>
        
        <div v-else class="review-form">
          <p>Share your experience! How was the cleaning service?</p>
          <form @submit.prevent="submitReview">
            <div class="rating-input">
              <label>Rating</label>
              <div class="star-selector">
                <button
                  v-for="i in 5"
                  :key="i"
                  type="button"
                  :class="['star-btn', { active: i <= reviewRating }]"
                  @click="reviewRating = i"
                >
                  ⭐
                </button>
              </div>
            </div>
            
            <label>
              Comment (optional)
              <textarea v-model="reviewComment" placeholder="Tell us about your experience..." rows="4"></textarea>
            </label>
            
            <button type="submit" class="btn btn-primary" :disabled="reviewRating === 0 || reviewLoading">
              {{ reviewLoading ? 'Submitting...' : 'Submit Review' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import * as auth from '../services/auth'

export default {
  setup() {
    const route = useRoute()
    const router = useRouter()
    const booking = ref(null)
    const existingReview = ref(null)
    const loading = ref(true)
    const error = ref('')
    const reviewRating = ref(0)
    const reviewComment = ref('')
    const reviewLoading = ref(false)

    const canEdit = computed(() => {
      if (!booking.value) return false
      const user = auth.currentUser.value
      return user && 
             (booking.value.user_id === user.id || user.role === 'admin') &&
             booking.value.status === 'pending'
    })

    const canCancel = computed(() => {
      if (!booking.value) return false
      const user = auth.currentUser.value
      if (!user) return false
      if (user.role === 'admin') return true
      if (booking.value.user_id !== user.id) return false
      return booking.value.status === 'pending' || booking.value.status === 'confirmed'
    })

    async function fetchBooking() {
      loading.value = true
      error.value = ''
      try {
        const res = await api.get(`/bookings/${route.params.id}`)
        booking.value = res.data?.data || res.data?.booking || res.data
        
        // Fetch review if booking is completed
        if (booking.value && booking.value.status === 'completed') {
          try {
            const reviewRes = await api.get(`/reviews?booking_id=${booking.value.id}`)
            const reviews = reviewRes.data?.data || reviewRes.data || []
            existingReview.value = reviews.find(r => r.booking_id === booking.value.id) || null
          } catch (err) {
            // Review might not exist yet, that's okay
            console.log('No review found for this booking')
          }
        }
      } catch (err) {
        error.value = err.response?.data?.msg || err.response?.data?.message || 'Failed to load booking'
      } finally {
        loading.value = false
      }
    }

    async function cancelBooking() {
      if (!confirm('Are you sure you want to cancel this booking?')) return
      
      try {
        await api.delete(`/bookings/${booking.value.id}`)
        window.dispatchEvent(new CustomEvent('toast', {
          detail: { message: 'Booking cancelled successfully', type: 'success' }
        }))
        router.push('/bookings')
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || 'Failed to cancel booking'
        window.dispatchEvent(new CustomEvent('toast', {
          detail: { message: errorMsg, type: 'error' }
        }))
      }
    }

    async function submitReview() {
      if (reviewRating.value === 0) {
        window.dispatchEvent(new CustomEvent('toast', {
          detail: { message: 'Please select a rating', type: 'error' }
        }))
        return
      }

      reviewLoading.value = true
      try {
        await api.post('/reviews', {
          booking_id: booking.value.id,
          rating: reviewRating.value,
          comment: reviewComment.value
        })
        
        window.dispatchEvent(new CustomEvent('toast', {
          detail: { message: 'Review submitted successfully', type: 'success' }
        }))
        
        // Reload booking to show the new review
        await fetchBooking()
        reviewRating.value = 0
        reviewComment.value = ''
      } catch (err) {
        const errorMsg = err.response?.data?.msg || err.response?.data?.message || 'Failed to submit review'
        window.dispatchEvent(new CustomEvent('toast', {
          detail: { message: errorMsg, type: 'error' }
        }))
      } finally {
        reviewLoading.value = false
      }
    }

    function formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      })
    }

    function formatDuration(start, end) {
      if (!start || !end) return ''
      const startDate = new Date(start)
      const endDate = new Date(end)
      const durationMs = endDate - startDate
      const durationMins = Math.round(durationMs / (1000 * 60))
      return `Duration: ${durationMins} minutes`
    }

    function formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    function formatPaymentMethod(method) {
      const methods = {
        'cash': 'Cash on Arrival',
        'cod': 'Cash on Delivery',
        'online': 'Online Payment'
      }
      return methods[method] || method
    }

    function formatPrice(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }

    function calculateSubtotal() {
      if (!booking.value?.service) return 0
      const basePrice = booking.value.service.price
      const areaCount = booking.value.areas?.length || 0
      const areaExtra = Math.max(0, (areaCount - 1) * 10)
      return basePrice + areaExtra
    }

    function calculateTax() {
      return calculateSubtotal() * 0.08
    }

    onMounted(fetchBooking)

    return {
      booking,
      existingReview,
      loading,
      error,
      reviewRating,
      reviewComment,
      reviewLoading,
      canEdit,
      canCancel,
      cancelBooking,
      submitReview,
      formatDateTime,
      formatDuration,
      formatDate,
      formatPaymentMethod,
      formatPrice,
      calculateSubtotal,
      calculateTax
    }
  }
}
</script>

<style scoped>
.booking-detail {
  max-width: 900px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.detail-header h1 {
  margin: 0;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.detail-card {
  padding: var(--spacing-xl);
}

.detail-card h2 {
  margin: 0 0 var(--spacing-lg) 0;
  font-size: var(--font-size-2xl);
  color: var(--color-text);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: var(--spacing-md);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-light);
  margin-bottom: var(--spacing-xs);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item .value {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
}

.info-item .value-sub {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
  margin-top: var(--spacing-xs);
}

.status-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-sm);
  font-weight: 600;
  text-transform: capitalize;
}

.status-pending {
  background: rgba(245, 158, 11, 0.2);
  color: var(--color-warning);
}

.status-confirmed {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
}

.status-in_progress {
  background: rgba(59, 130, 246, 0.2);
  color: var(--color-info);
}

.status-completed {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
}

.status-cancelled {
  background: rgba(239, 68, 68, 0.2);
  color: var(--color-danger);
}

.areas-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-xs);
}

.area-tag {
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--color-primary);
  color: white;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.notes-text {
  white-space: pre-wrap;
  line-height: 1.6;
}

.price-section {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-xl);
  border-top: 2px solid var(--border-color);
}

.price-section h3 {
  margin: 0 0 var(--spacing-md) 0;
  font-size: var(--font-size-xl);
}

.price-breakdown {
  background: var(--bg-subtle);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius);
}

.price-row {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--border-color);
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
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-xl);
  border-top: 2px solid var(--border-color);
}

.review-section {
  padding: var(--spacing-xl);
}

.review-section h2 {
  margin: 0 0 var(--spacing-lg) 0;
  font-size: var(--font-size-2xl);
  border-bottom: 2px solid var(--border-color);
  padding-bottom: var(--spacing-md);
}

.existing-review {
  padding: var(--spacing-lg);
  background: var(--bg-subtle);
  border-radius: var(--border-radius);
}

.review-rating {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.star {
  font-size: var(--font-size-xl);
  opacity: 0.3;
}

.star.filled {
  opacity: 1;
}

.rating-value {
  font-weight: 600;
  font-size: var(--font-size-lg);
  color: var(--color-text);
}

.review-comment {
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
}

.review-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-light);
}

.review-form {
  padding: var(--spacing-lg);
  background: var(--bg-subtle);
  border-radius: var(--border-radius);
}

.rating-input {
  margin-bottom: var(--spacing-lg);
}

.rating-input label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: 600;
}

.star-selector {
  display: flex;
  gap: var(--spacing-xs);
}

.star-btn {
  background: none;
  border: none;
  font-size: var(--font-size-2xl);
  cursor: pointer;
  opacity: 0.3;
  transition: all var(--transition-base);
  padding: var(--spacing-xs);
}

.star-btn.active,
.star-btn:hover {
  opacity: 1;
  transform: scale(1.2);
}

.review-form label {
  display: block;
  margin-bottom: var(--spacing-sm);
  font-weight: 600;
}

.review-form textarea {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  font-family: var(--font-family);
  resize: vertical;
}

.review-form button {
  margin-top: var(--spacing-md);
}

.loading,
.error-message {
  text-align: center;
  padding: var(--spacing-2xl);
  font-size: var(--font-size-lg);
}

.error-message {
  color: var(--color-danger);
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>

