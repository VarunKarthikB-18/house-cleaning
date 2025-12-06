<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <h4>House Cleaner</h4>
        <p>Professional cleaning services at your doorstep. Book trusted cleaners quickly and easily.</p>
      </div>
      
      <div class="footer-section">
        <h4>Quick Links</h4>
        <ul>
          <li><router-link to="/">Home</router-link></li>
          <li v-if="!isAuthed"><router-link to="/login">Login</router-link></li>
          <li v-if="!isAuthed"><router-link to="/register">Register</router-link></li>
          <li v-if="isAuthed"><router-link to="/dashboard">Dashboard</router-link></li>
          <li v-if="isAuthed"><router-link to="/bookings">My Bookings</router-link></li>
        </ul>
      </div>
      
      <div class="footer-section">
        <h4>Contact</h4>
        <ul>
          <li>📧 support@housecleaner.com</li>
          <li>📞 +91 98765 43210</li>
          <li>🕒 Mon-Sat: 8:00 AM - 7:00 PM</li>
        </ul>
      </div>
    </div>
    
    <div class="footer-bottom">
      <p>&copy; {{ currentYear }} House Cleaner. All rights reserved.</p>
    </div>
  </footer>
</template>

<script>
import { computed } from 'vue'
import * as auth from '../services/auth'

export default {
  setup() {
    const isAuthed = computed(() => !!auth.getToken() && !!auth.currentUser.value)
    const currentYear = new Date().getFullYear()
    
    return { isAuthed, currentYear }
  }
}
</script>

<style scoped>
.footer {
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
  color: #ffffff !important;
  margin-top: auto;
  padding: var(--spacing-2xl) var(--spacing-lg);
  width: 100%;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.footer-section h4 {
  font-size: var(--font-size-lg);
  font-weight: 700;
  margin-bottom: var(--spacing-md);
  color: #ffffff !important;
}

.footer-section p {
  color: #e5e7eb !important;
  line-height: 1.8;
  margin: 0;
  font-size: var(--font-size-base);
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section ul li {
  margin-bottom: var(--spacing-sm);
  color: #e5e7eb !important;
  font-size: var(--font-size-base);
  line-height: 1.8;
}

.footer-section ul li a {
  color: #e5e7eb !important;
  text-decoration: none;
  transition: color var(--transition-base);
  font-weight: 500;
}

.footer-section ul li a:hover {
  color: #ffffff !important;
  text-decoration: underline;
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: var(--spacing-lg);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  color: #9ca3af !important;
  font-size: var(--font-size-sm);
}

@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .footer {
    padding: var(--spacing-xl) var(--spacing-md);
  }
}
</style>

