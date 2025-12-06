<template>
  <div class="home-page">
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
  </div>
</template>

<script>
export default { }
</script>

<style scoped>
.home-page {
  width: 100vw;
  margin: 0;
  padding: 0;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
}

.hero {
  min-height: calc(100vh - 120px);
  width: 100vw;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
  background-size: 400% 400%;
  background-attachment: fixed;
  animation: gradientShift 15s ease infinite;
  color: white;
  text-align: center;
  padding: 4rem 2rem;
  position: relative;
  overflow: hidden;
  margin: 0;
}

.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.hero-content {
  max-width: 700px;
  position: relative;
  z-index: 1;
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
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
  color: #ffffff !important;
  border: 2px solid transparent !important;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4);
  padding: 1rem 2rem;
  font-size: 1.1rem;
  text-decoration: none;
  display: inline-block;
}

.hero-cta .btn-primary:hover {
  background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
  color: #ffffff !important;
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(79, 70, 229, 0.5);
}

.hero-cta .btn-secondary {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
  color: #ffffff !important;
  border: 2px solid transparent !important;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4);
  padding: 1rem 2rem;
  font-size: 1.1rem;
  text-decoration: none;
  display: inline-block;
}

.hero-cta .btn-secondary:hover {
  background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
  color: #ffffff !important;
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(79, 70, 229, 0.5);
}

@media (max-width: 768px) {
  .home-page {
    margin-left: 0;
    margin-right: 0;
  }
  
  .hero {
    min-height: calc(100vh - 120px);
    padding: 3rem 1.5rem;
    margin: 0;
    width: 100vw;
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
