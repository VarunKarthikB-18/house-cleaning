# House Cleaner — Full-stack Appointment Booking App

Production-ready house cleaning appointment system with JWT authentication, admin dashboard, and full booking management.

## Tech Stack

**Backend:**
- Flask 2.3.3
- Flask-SQLAlchemy 3.0.3
- Flask-Migrate 4.0.4
- flask-jwt-extended 4.4.4
- Werkzeug 2.3.4

**Frontend:**
- Vue 3
- Vite
- Axios
- Vue Router

**Database:**
- SQLite (development)

## Project Structure

```
house-cleaner/
├── backend/
│   ├── app.py                 # App factory
│   ├── config.py              # Configuration
│   ├── extensions.py          # Extensions initialization
│   ├── models.py              # Database models
│   ├── seeds.py               # Seed script
│   ├── routes/
│   │   ├── auth.py            # Auth endpoints
│   │   ├── services.py        # Services listing
│   │   ├── bookings.py        # User booking endpoints
│   │   └── admin.py           # Admin endpoints
│   ├── tests/
│   │   ├── test_basic.py      # Basic tests
│   │   └── conftest.py        # Pytest fixtures
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router.js          # Vue Router setup
│   │   ├── services/
│   │   │   ├── api.js         # Axios instance + interceptors
│   │   │   └── auth.js        # Auth service
│   │   ├── pages/
│   │   │   ├── Home.vue       # Services listing
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Bookings.vue       # User bookings list
│   │   │   ├── NewBooking.vue     # Create booking form
│   │   │   ├── BookingDetail.vue  # Booking details + review
│   │   │   ├── Reviews.vue        # Reviews listing
│   │   │   ├── UserDashboard.vue  # User dashboard
│   │   │   └── AdminDashboard.vue # Admin dashboard
│   │   └── components/
│   │       ├── ServiceCard.vue    # Service package display
│   │       ├── BookingCard.vue    # Booking summary card
│   │       ├── BookingForm.vue    # Booking creation/editing form
│   │       ├── TimeSlotPicker.vue # Time slot selection component
│   │       ├── CleanerCard.vue    # Cleaner info card (admin)
│   │       ├── AdminBookingRow.vue # Admin booking table row
│   │       ├── HeaderBar.vue      # Navigation header
│   │       └── FooterBar.vue      # Footer with links
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── README.md
├── .gitignore
└── README.md (this file)
```

## Quick Start (All-in-one)

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your secrets (or use defaults for dev)

# Set Flask app environment variable
export FLASK_APP=app:create_app

# Initialize database with migrations
flask db init
flask db migrate -m "initial"
flask db upgrade

# Seed demo data
python seeds.py

# Run backend server
python app.py
```

Backend will be available at `http://127.0.0.1:5001` (port 5001 to avoid conflicts with macOS AirPlay Receiver)

### Step 2: Frontend Setup (in a new terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Step 3: Test the Application

**In a third terminal, run tests:**
```bash
cd backend
pytest
```

## Authentication

The app uses JWT (JSON Web Tokens) for authentication.

### User Roles:
- `user` — Regular user, can create and manage own bookings
- `admin` — Admin user, can manage all bookings and assign cleaners
- `cleaner` — Cleaner user (not yet used in MVP)

### Demo Credentials (after seeding):
- Admin: `admin@example.com` / `admin123`
- User: `user@example.com` / `user123`

## Key Features

### User Features
- **Register and Login**: Secure JWT-based authentication
- **Browse Services**: View 5-6 service packages (Basic, Standard, Deep Clean, Move-Out, Post-Party, Premium) with pricing
- **Create Bookings**:
  - Select service package
  - Choose areas to clean (multi-checkbox: Bathroom, Kitchen, Living Room, Bedroom, Balcony, Other)
  - Pick date and time slot (30-min increments, business hours 8 AM - 7 PM)
  - Set payment method (Cash on Arrival, COD, or Online)
  - View real-time price breakdown (base price + area extras + tax)
  - Add notes and special instructions
- **Manage Bookings**: 
  - View all bookings (upcoming and past)
  - Edit pending bookings
  - Cancel bookings (within cancellation window)
  - View booking details with full invoice
- **Reviews**: Leave reviews for completed bookings (1-5 stars + comment)
- **Profile Management**: Update name, phone, and default address

### Admin Features
- **Dashboard**: Professional admin interface with statistics
- **Booking Management**:
  - View all bookings with filters (date, status, service, cleaner)
  - Assign cleaners to bookings (with conflict detection)
  - Update booking status (pending → confirmed → in_progress → completed → cancelled)
  - Export bookings to CSV
- **Service Management**: Create, edit, and deactivate service packages
- **Cleaner Management**: 
  - Add/edit/activate/deactivate cleaners
  - View cleaner's upcoming assigned bookings
- **User Management**: View user list with booking counts
- **Statistics**: 
  - Booking counts by status
  - Daily booking counts (past 7 days)
  - Revenue estimates
  - Top services
- **Review Moderation**: View and delete inappropriate reviews

### Backend Features
- **Business Rules Enforcement**:
  - Minimum lead time: 3 hours before booking start
  - Business hours: 8 AM - 7 PM UTC
  - Cancellation window: Cannot cancel within 2 hours of start
  - Cleaner conflict detection (no overlapping bookings)
- **Pricing Calculation**: Base price + area extras ($10 per additional area) + 8% tax
- **Timezone Handling**: UTC storage with local time conversion
- **Comprehensive Validation**: Service availability, datetime validation, payment method validation
- **Role-Based Access Control**: JWT tokens with user roles (user/admin)
- **Error Handling**: Consistent JSON error responses
- **Review System**: Users can only review completed bookings

## API Examples

### User Registration
```bash
curl -X POST http://127.0.0.1:5001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"secure123","name":"John","phone":"555-1234","address":"123 Main St"}'
```

### User Login
```bash
curl -X POST http://127.0.0.1:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"secure123"}'
```

Returns: `{"access_token": "eyJ...", "user": {...}}`

### List Services
```bash
curl -X GET http://127.0.0.1:5001/services
```

### Create Booking (requires token)
```bash
curl -X POST http://127.0.0.1:5001/bookings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN_HERE" \
  -d '{
    "service_id": 1,
    "start_datetime": "2025-12-15T14:00:00+00:00",
    "address": "456 Oak Ave",
    "areas": ["Bathroom", "Kitchen", "Living Room"],
    "payment_method": "cash",
    "notes": "Please bring eco-friendly supplies"
  }'
```

### List User Bookings (requires token)
```bash
curl -X GET http://127.0.0.1:5001/bookings \
  -H "Authorization: Bearer TOKEN_HERE"
```

### Admin: Assign Cleaner to Booking
```bash
curl -X PUT http://127.0.0.1:5001/admin/bookings/1/assign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -d '{"cleaner_id": 1}'
```

### Admin: Get Statistics
```bash
curl -X GET http://127.0.0.1:5001/admin/stats \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

### Create Review (requires token, booking must be completed)
```bash
curl -X POST http://127.0.0.1:5001/reviews \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN_HERE" \
  -d '{
    "booking_id": 1,
    "rating": 5,
    "comment": "Excellent service! Very thorough and professional."
  }'
```

### Get Reviews
```bash
curl -X GET http://127.0.0.1:5001/reviews?booking_id=1
```

## Database Schema

### Users
- `id` (PK), `email` (unique), `password_hash`, `name`, `phone`, `address`, `role`, `created_at`

### ServiceTypes
- `id` (PK), `name`, `duration_mins`, `price`, `description`

### Cleaners
- `id` (PK), `name`, `phone`, `active`

### Bookings
- `id` (PK), `user_id` (FK), `service_id` (FK), `cleaner_id` (FK, nullable), 
  `start_datetime`, `end_datetime`, `status`, `areas` (JSON), `payment_method`, 
  `price_total`, `address`, `notes`, `created_at`

Statuses: `pending`, `confirmed`, `in_progress`, `completed`, `cancelled`

Payment Methods: `cash`, `cod`, `online`

### Reviews
- `id` (PK), `user_id` (FK), `booking_id` (FK, unique), `rating` (1-5), 
  `comment`, `moderated` (bool), `created_at`

## Environment Variables

Create a `.env` file in the `backend/` directory (copy from `.env.example`):

```env
SECRET_KEY=your-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-change-this
DATABASE_URL=sqlite:///house_cleaner.db
```

For production, use strong random secrets:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Running Tests

```bash
cd backend
pytest -v                    # Verbose output
pytest tests/test_basic.py  # Run specific test file
pytest -k test_register     # Run tests matching pattern
```

## Troubleshooting

### Port Already in Use
- Backend (5000): `lsof -i :5000` then `kill -9 PID`
- Frontend (5173): `lsof -i :5173` then `kill -9 PID`

### Database Issues
- Reset: Remove `backend/house_cleaner.db` and `backend/migrations/`, then re-run `flask db init/migrate/upgrade`
- Check schema: `sqlite3 backend/house_cleaner.db ".schema"`

### CORS Issues
- Frontend can't reach backend: Check backend is running on `127.0.0.1:5000`
- Update `src/services/api.js` baseURL if backend is on different host

### JWT Errors
- Clear localStorage in browser: `localStorage.clear()` in browser console
- Generate new tokens by logging in again

## Production Deployment

### Backend (Flask)
- Use production WSGI server: `gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"`
- Use environment-specific config (PostgreSQL, Redis, etc.)
- Set `DEBUG=False`
- Use strong `SECRET_KEY` and `JWT_SECRET_KEY`

### Frontend (Vue)
- Build: `npm run build` (outputs to `dist/`)
- Serve via Nginx or static hosting
- Update `src/services/api.js` baseURL to production backend URL

### Database
- Use PostgreSQL instead of SQLite
- Update `DATABASE_URL` to PostgreSQL connection string

## Development Workflow

1. **Backend changes**: Edit files in `backend/`, server hot-reloads (debug mode)
2. **Frontend changes**: Edit files in `frontend/`, Vite hot-reloads
3. **New database model**: Add to `backend/models.py`, then:
   ```bash
   flask db migrate -m "add new model"
   flask db upgrade
   ```
4. **New API endpoint**: Add to `backend/routes/`, import in `backend/app.py`

## UI Features

- **Professional Theme**: Not plain white - uses soft gray background (#f4f6f8) with white cards
- **Modern Design**: Gradient accents, smooth transitions, hover effects
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Time Slot Picker**: Visual time slot selection with business hours and lead time validation
- **Price Calculator**: Real-time price breakdown showing base price, area extras, and tax
- **Status Badges**: Color-coded booking status indicators
- **Review System**: Star ratings and comments for completed bookings

## Business Rules

- **Minimum Lead Time**: Bookings must be at least 3 hours in the future
- **Business Hours**: 8:00 AM - 7:00 PM UTC (customizable in code)
- **Cancellation Window**: Cannot cancel within 2 hours of booking start time
- **Cleaner Conflicts**: System prevents double-booking the same cleaner
- **Review Eligibility**: Users can only review completed bookings, one review per booking
- **Pricing**: Base service price + $10 per additional area + 8% tax

## Notes

- Datetimes are stored as UTC in database; frontend handles timezone conversion
- Frontend sends ISO datetime strings; backend validates and converts to UTC
- Service packages include: Basic (30m), Standard (60m), Deep Clean (120m), Move-Out (180m), Post-Party (90m), Premium (180m)
- Area selection: First area included in base price, additional areas cost $10 each
- Payment methods: Cash on Arrival (default), COD, or Online (for future integration)

## License

MIT

## Support

For issues or questions, check backend/README.md and frontend/README.md for detailed docs.
