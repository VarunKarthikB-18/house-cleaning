<template>
  <section class="hero">
    <div class="hero-content">
      <h1 class="hero-title">House Cleaning Made Easy</h1>
      <p class="hero-subtitle">Book trusted cleaners quickly and easily. Professional, reliable service at your fingertips.</p>
      <div class="hero-cta">
        <router-link class="btn btn-primary btn-lg" to="/register">Get Started</router-link>
        <router-link class="btn btn-secondary btn-lg" to="/login">Sign In</router-link>
      </div>
    </div>
  </section>
</template>

<script>
export default { }
</script>

<style scoped>
.hero {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 2rem;
}

.hero-content {
  max-width: 600px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: white;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2.5rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.hero-cta {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-cta .btn {
  min-width: 150px;
}

.hero-cta .btn-primary {
  background-color: #ffffff;
  color: #667eea;
  border-color: #ffffff;
  font-weight: 600;
}

.hero-cta .btn-primary:hover {
  background-color: rgba(255, 255, 255, 0.9);
  color: #667eea;
}

.hero-cta .btn-secondary {
  background-color: transparent;
  color: white;
  border-color: white;
  font-weight: 600;
}

.hero-cta .btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  border-color: white;
}

@media (max-width: 768px) {
  .hero {
    min-height: auto;
    padding: 3rem 1.5rem;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.1rem;
  }

  .hero-cta {
    flex-direction: column;
  }

  .hero-cta .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }
}
</style>
