<template>
  <div class="service-card" :class="cardClass">
    <div class="service-icon">{{ icon }}</div>
    <h3>{{ title }}</h3>
    <p>{{ desc }}</p>
    <div class="price">{{ price }}</div>
    <slot />
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  props: { 
    title: String, 
    desc: String, 
    price: String,
    variant: {
      type: Number,
      default: 0
    }
  },
  setup(props) {
    const icons = ['🧹', '🏠', '✨', '🌟', '💎', '🎨']
    const gradients = [
      'gradient-primary',
      'gradient-secondary', 
      'gradient-accent',
      'gradient-success',
      'gradient-warm',
      'gradient-cool'
    ]
    
    const icon = computed(() => icons[props.variant % icons.length])
    const cardClass = computed(() => gradients[props.variant % gradients.length])
    
    return { icon, cardClass }
  }
}
</script>

<style scoped>
.service-card {
  background: var(--bg-card);
  padding: 2rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  text-align: center;
}

.service-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  background: var(--gradient-primary);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.service-card.gradient-primary::before {
  background: var(--gradient-primary);
}

.service-card.gradient-secondary::before {
  background: var(--gradient-secondary);
}

.service-card.gradient-accent::before {
  background: var(--gradient-accent);
}

.service-card.gradient-success::before {
  background: var(--gradient-success);
}

.service-card.gradient-warm::before {
  background: var(--gradient-warm);
}

.service-card.gradient-cool::before {
  background: var(--gradient-cool);
}

.service-card:hover::before {
  transform: scaleX(1);
}

.service-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: var(--shadow-lg);
}

.service-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

.service-card h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: var(--text);
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.service-card p {
  color: var(--text-light);
  margin-bottom: 1rem;
  line-height: 1.6;
}

.price {
  margin-top: 1rem;
  font-weight: 700;
  font-size: 1.5rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@media (max-width: 768px) {
  .service-card {
    padding: 1.5rem;
  }
  
  .service-icon {
    font-size: 2.5rem;
  }
}
</style>
