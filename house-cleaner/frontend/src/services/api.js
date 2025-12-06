import axios from 'axios'

const baseURL = 'http://127.0.0.1:5001'
const api = axios.create({ baseURL, timeout: 10000 })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => Promise.reject(error))

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response && err.response.status === 401) {
      try {
        localStorage.removeItem('access_token')
      } catch (e) {}
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
