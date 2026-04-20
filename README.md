# Wedding Invitation System — Backend API

Production-ready FastAPI backend for wedding guest management, QR code check-in, RSVP, and comments.

---

## Project Structure

```
wedding-backend/
├── app/
│   ├── main.py                    # FastAPI app + router registration
│   ├── core/
│   │   ├── config.py              # Settings via pydantic-settings (.env)
│   │   └── security.py            # Password hashing, JWT, QR signing
│   ├── db/
│   │   ├── session.py             # SQLAlchemy engine + Base + get_db
│   │   ├── models/
│   │   │   └── models.py          # ORM models (Guest, RSVP, Comment, User…)
│   │   └── repositories/
│   │       ├── guest_repository.py
│   │       ├── comment_repository.py
│   │       ├── rsvp_repository.py
│   │       └── user_repository.py
│   ├── services/
│   │   ├── guest_service.py       # Business logic: create, check-in, search
│   │   ├── comment_service.py
│   │   ├── rsvp_service.py
│   │   └── auth_service.py
│   ├── api/
│   │   ├── deps.py                # JWT auth dependency
│   │   └── routes/
│   │       ├── auth.py            # POST /auth/login
│   │       ├── guests.py          # CRUD + manual check-in
│   │       ├── checkin.py         # GET  /checkin?code=xxx
│   │       ├── rsvp.py            # POST /rsvp
│   │       └── comments.py        # POST/GET /comments
│   └── schemas/
│       └── schemas.py             # Pydantic request/response models
├── scripts/
│   └── init_db.py                 # Create tables + seed WO user
├── schema.sql                     # Raw MySQL schema (alternative to ORM migration)
├── gunicorn.conf.py
├── wedding.service                # systemd unit
├── nginx.conf                     # Nginx reverse proxy config
├── requirements.txt
└── .env.example
```

---

## QR Code Design

Each guest QR code is non-predictable and tamper-proof:

```
Format:  {guest_id}:{HMAC-SHA256-signature}
Example: 42:9f3a1c8d2b7e...

Signature = HMAC-SHA256(key=QR_HMAC_SECRET, msg=str(guest_id))
```

- Signature is never stored in the database
- Verified server-side on every scan using `hmac.compare_digest` (timing-safe)
- Tampering any character makes it INVALID

---

## API Reference

All protected endpoints require:
```
Authorization: Bearer <token>
```

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/login` | No | WO login, returns JWT |

### Guests (WO only)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/guests` | Yes | Create guest (auto QR + entitlements) |
| GET | `/api/v1/guests` | Yes | List all guests |
| GET | `/api/v1/guests/search?name=xxx` | Yes | Search guests by name |
| GET | `/api/v1/guests/{id}` | Yes | Get guest detail with entitlements |
| POST | `/api/v1/guests/{id}/checkin` | Yes | Manual check-in by guest ID |

### Check-in (WO only)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/checkin?code=xxx` | Yes | QR scan check-in |

### RSVP (Public)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/rsvp` | No | Submit RSVP |

### Comments (Public)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/comments` | No | Post a comment/wish |
| GET | `/api/v1/comments` | No | Get latest comments |

### System

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |

---

## Sample curl Requests

### 1. Login as WO
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme123!"}' | jq .

# Response:
# { "access_token": "eyJ...", "token_type": "bearer" }

TOKEN="eyJ..."   # save for subsequent requests
```

### 2. Create a VIP Guest
```bash
curl -s -X POST http://localhost:8000/api/v1/guests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Budi Santoso",
    "phone": "081234567890",
    "category": "VIP",
    "invitation_type": "QR"
  }' | jq .

# Response includes:
# - qr_code: "42:9f3a1c8d..."
# - entitlements: [FOOD, SOUVENIR]
```

### 3. Create a Regular Guest
```bash
curl -s -X POST http://localhost:8000/api/v1/guests \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Siti Rahayu",
    "category": "REGULAR",
    "invitation_type": "QR"
  }' | jq .

# entitlements: [SOUVENIR only]
```

### 4. QR Check-in (WO scans QR)
```bash
curl -s "http://localhost:8000/api/v1/checkin?code=42:9f3a1c8d2b7e..." \
  -H "Authorization: Bearer $TOKEN" | jq .

# Status OK:
# { "status": "OK", "guest_name": "Budi Santoso", "category": "VIP",
#   "entitlements": [{"type":"FOOD","qty":1},{"type":"SOUVENIR","qty":1}] }

# Status ALREADY_USED:
# { "status": "ALREADY_USED", "message": "This QR was already used at ..." }

# Status INVALID:
# { "status": "INVALID", "message": "QR code is not valid." }
```

### 5. Manual Check-in (by guest ID)
```bash
curl -s -X POST http://localhost:8000/api/v1/guests/42/checkin \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### 6. Search Guests by Name
```bash
curl -s "http://localhost:8000/api/v1/guests/search?name=budi" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### 7. Submit RSVP
```bash
curl -s -X POST http://localhost:8000/api/v1/rsvp \
  -H "Content-Type: application/json" \
  -d '{"guest_id": 42, "attendance": "YES", "guest_count": 2}' | jq .
```

### 8. Post a Comment
```bash
curl -s -X POST http://localhost:8000/api/v1/comments \
  -H "Content-Type: application/json" \
  -d '{"name": "Budi Santoso", "message": "Selamat menempuh hidup baru!", "guest_id": 42}' | jq .
```

### 9. Get Latest Comments
```bash
curl -s "http://localhost:8000/api/v1/comments?limit=20" | jq .
```

---

## EC2 Deployment Guide

### Step 1 — Launch EC2 Instance

- AMI: **Ubuntu 22.04 LTS**
- Instance type: `t3.small` (minimum for production)
- Security Group inbound rules:
  - Port 22 (SSH) — your IP only
  - Port 80 (HTTP) — 0.0.0.0/0
  - Port 443 (HTTPS) — 0.0.0.0/0

### Step 2 — Initial Server Setup

```bash
ssh ubuntu@<EC2-PUBLIC-IP>

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip mysql-server nginx git

# Create log directory
sudo mkdir -p /var/log/wedding
sudo chown ubuntu:ubuntu /var/log/wedding
```

### Step 3 — Configure MySQL

```bash
sudo mysql_secure_installation   # follow prompts

sudo mysql -u root -p <<EOF
CREATE DATABASE wedding_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wedding_user'@'localhost' IDENTIFIED BY 'strong_db_password_here';
GRANT ALL PRIVILEGES ON wedding_db.* TO 'wedding_user'@'localhost';
FLUSH PRIVILEGES;
EOF
```

### Step 4 — Deploy Application

```bash
# Clone / upload your project
cd /home/ubuntu
git clone https://github.com/yourrepo/wedding-backend.git
cd wedding-backend

# Create virtualenv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env   # Fill in all secrets — use strong random values!
```

### Step 5 — Initialize Database

```bash
# Option A: via SQLAlchemy ORM (recommended)
python scripts/init_db.py --seed --username admin --password "YourStrongPass!"

# Option B: via raw SQL
mysql -u wedding_user -p wedding_db < schema.sql
# Then manually seed a WO user via the init script
```

### Step 6 — Test Locally on EC2

```bash
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
# Ctrl+C when verified working
```

### Step 7 — Configure Nginx

```bash
sudo cp nginx.conf /etc/nginx/sites-available/wedding
sudo ln -s /etc/nginx/sites-available/wedding /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t          # test config
sudo systemctl restart nginx
```

### Step 8 — Configure systemd Service

```bash
sudo cp wedding.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wedding
sudo systemctl start wedding

# Check status
sudo systemctl status wedding
sudo journalctl -u wedding -f   # live logs
```

### Step 9 — Optional: HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com

# Auto-renewal (already set up by certbot, verify with):
sudo certbot renew --dry-run
```

---

## Security Checklist

- [x] Passwords hashed with bcrypt
- [x] QR codes signed with HMAC-SHA256 (unpredictable, tamper-proof)
- [x] Double check-in prevention (atomic DB flag)
- [x] JWT tokens with expiry
- [x] Input sanitized with `bleach` (XSS prevention)
- [x] All secrets in `.env` (never committed)
- [ ] Change default WO password after first login
- [ ] Rotate `SECRET_KEY`, `QR_HMAC_SECRET`, `JWT_SECRET_KEY` before go-live
- [ ] Restrict `/docs` and `/redoc` in Nginx for production

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | General app secret | random 40+ char string |
| `QR_HMAC_SECRET` | QR signing key | random 40+ char string |
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_NAME` | Database name | `wedding_db` |
| `DB_USER` | DB username | `wedding_user` |
| `DB_PASSWORD` | DB password | strong password |
| `JWT_SECRET_KEY` | JWT signing key | random 40+ char string |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiry | `480` (8 hours) |
| `ALLOWED_ORIGINS` | CORS origins | `https://yourdomain.com` |

Generate strong secrets with:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
