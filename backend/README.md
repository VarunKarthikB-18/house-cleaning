# House Cleaner Backend

Full Flask + SQLAlchemy backend for house cleaning appointments.

## Setup

### 1. Create Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
Create a `.env` file in `backend/` with:
```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=sqlite:///house_cleaner.db
```

### 4. Initialize Database & Migrations

**First time only:**
```bash
export FLASK_APP=app:create_app
flask db init
flask db migrate -m "initial"
flask db upgrade
```

**After this, you can run:** `python seeds.py`

### 5. Run Server
```bash
python app.py
```

Server runs at `http://127.0.0.1:5000`

## Testing
```bash
pytest
```

## API Endpoints

### Auth
- `POST /auth/register` — register new user
- `POST /auth/login` — login and get JWT token

### Services
- `GET /services` — list all service types

### Bookings (requires JWT)
- `POST /bookings` — create booking
- `GET /bookings` — list user's bookings
- `GET /bookings/<id>` — get booking details
- `PUT /bookings/<id>` — update booking (pending only)
- `DELETE /bookings/<id>` — cancel booking

### Admin (requires JWT + admin role)
- `GET /admin/bookings` — list all bookings
- `PUT /admin/bookings/<id>/assign` — assign cleaner
- `PUT /admin/bookings/<id>/status` — update status
- `GET /admin/stats` — get statistics

## Example Curl Commands

### Register
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123","name":"John"}'
```

### Login
```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'
```

### Create Booking (replace TOKEN)
```bash
curl -X POST http://127.0.0.1:5000/bookings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"service_id":1,"start_datetime":"2025-12-10T14:00:00","address":"123 Main St","notes":"Clean kitchen"}'
```

### List Bookings (replace TOKEN)
```bash
curl -X GET http://127.0.0.1:5000/bookings \
  -H "Authorization: Bearer TOKEN"
```

### Admin: Assign Cleaner (replace TOKEN, BOOKING_ID, CLEANER_ID)
```bash
curl -X PUT http://127.0.0.1:5000/admin/bookings/BOOKING_ID/assign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"cleaner_id":CLEANER_ID}'
```

### Admin: Get Stats (replace TOKEN)
```bash
curl -X GET http://127.0.0.1:5000/admin/stats \
  -H "Authorization: Bearer TOKEN"
```
