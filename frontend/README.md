Frontend README

Run frontend:

```bash
cd frontend
npm install
npm run dev
```

Notes:
- Ensure backend is running on http://127.0.0.1:5000 (default baseURL in `src/services/api.js`).
- To change backend location, update `baseURL` in `src/services/api.js`.
# House Cleaner Frontend

Vue 3 + Vite frontend for house cleaning appointments.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

## Build for Production
```bash
npm run build
npm run preview
```

## Pages

- `/` — Home page listing all services
- `/login` — User login
- `/register` — User registration
- `/bookings` — User's bookings
- `/bookings/new` — Create new booking
- `/admin` — Admin dashboard (admin-only)

## Features

- **JWT Authentication** — Token stored in localStorage, attached to all API requests
- **Service Browsing** — View available services with pricing
- **Booking Management** — Create, view, edit, cancel bookings
- **Admin Dashboard** — Assign cleaners, update booking status, view stats
- **Responsive** — Works on desktop and mobile

## API Integration

Frontend calls backend at `http://127.0.0.1:5000`. If backend is on different host, update `src/services/api.js`:

```javascript
const api = axios.create({
  baseURL: 'http://your-backend-host:port',
  ...
})
```

## Development Notes

- Axios interceptors handle token attachment and 401 redirects
- Router guards protect admin pages (meta: { admin: true })
- Components use scoped CSS for styling
- No external UI library — minimal, functional CSS
