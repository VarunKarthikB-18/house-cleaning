<template>
  <div class="reviews-page">
    <h1>Reviews</h1>
    
    <div v-if="loading" class="loading">Loading reviews...</div>
    <div v-else>
      <div v-if="reviews.length === 0" class="empty-state">
        <p>No reviews yet. Check back after completing a booking!</p>
      </div>
      
      <div v-else class="reviews-list">
        <div v-for="review in reviews" :key="review.id" class="review-card card">
          <div class="review-header">
            <div class="reviewer-info">
              <h3>{{ review.user?.name || 'Anonymous' }}</h3>
              <div class="review-meta">
                <span class="review-date">{{ formatDate(review.created_at) }}</span>
                <span v-if="review.booking" class="booking-link">
                  for {{ review.booking.service?.name || 'Booking' }}
                </span>
              </div>
            </div>
            <div class="review-rating">
              <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= review.rating }">
                ⭐
              </span>
              <span class="rating-number">{{ review.rating }}/5</span>
            </div>
          </div>
          
          <div v-if="review.comment" class="review-comment">
            <p>{{ review.comment }}</p>
          </div>
          
          <div v-if="review.booking" class="review-booking-details">
            <small>
              Service Date: {{ formatDateTime(review.booking.start_datetime) }}
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import * as auth from '../services/auth'

export default {
  setup() {
    const reviews = ref([])
    const loading = ref(true)

    async function fetchReviews() {
      loading.value = true
      try {
        const user = auth.currentUser.value
        let url = '/reviews'
        
        // If user is not admin, only show their own reviews
        // Or show all reviews if admin
        if (user && user.role !== 'admin') {
          url = `/reviews?user_id=${user.id}`
        }
        
        const res = await api.get(url)
        reviews.value = res.data?.data || res.data?.reviews || []
        // Sort by most recent first
        reviews.value.sort((a, b) => 
          new Date(b.created_at) - new Date(a.created_at)
        )
      } catch (err) {
        console.error('Failed to fetch reviews:', err)
        window.dispatchEvent(new CustomEvent('toast', {
          detail: { message: 'Failed to load reviews', type: 'error' }
        }))
      } finally {
        loading.value = false
      }
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

    function formatDateTime(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
      })
    }

    onMounted(fetchReviews)

    return {
      reviews,
      loading,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.reviews-page {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: 0;
}

.reviews-page h1 {
  margin-bottom: var(--spacing-xl);
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: var(--font-size-3xl);
  font-weight: 700;
}

.loading {
  text-align: center;
  padding: var(--spacing-2xl);
  font-size: var(--font-size-lg);
  color: #6b7280 !important;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-3xl);
  background: #f9fafb;
  border-radius: var(--border-radius-lg);
  color: #6b7280 !important;
  border: 2px dashed #e5e7eb;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.review-card {
  padding: var(--spacing-xl);
  transition: all var(--transition-base);
}

.review-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--border-color);
}

.reviewer-info h3 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: #1f2937 !important;
}

.review-meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: #6b7280 !important;
}

.booking-link {
  color: var(--color-primary);
  font-weight: 500;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.star {
  font-size: var(--font-size-xl);
  opacity: 0.3;
}

.star.filled {
  opacity: 1;
}

.rating-number {
  font-weight: 700;
  font-size: var(--font-size-lg);
  color: var(--color-text);
  margin-left: var(--spacing-xs);
}

.review-comment {
  margin-top: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.review-comment p {
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: #374151 !important;
  margin: 0;
}

.review-booking-details {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}

.review-booking-details small {
  color: #6b7280 !important;
  font-size: var(--font-size-sm);
}

@media (max-width: 768px) {
  .review-header {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .review-rating {
    width: 100%;
  }
}
</style>

