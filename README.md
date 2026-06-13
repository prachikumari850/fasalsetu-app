# 🌾 FasalSetu

### AI-Powered Crop Lifecycle Monitoring & Smart Insurance Verification Platform for PMFBY

> **Smart Farming, Secure Future** — FasalSetu bridges the gap between Indian farmers and the PMFBY insurance scheme by creating a complete digital crop journey, making fraud detection automatic and claim processing faster.

---

## Table of Contents

- [Overview](#overview)
- [The Problem We Solve](#the-problem-we-solve)
- [Our Solution](#our-solution)
- [Key Innovations](#key-innovations)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Features](#features)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Fraud Detection Engine](#fraud-detection-engine)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Supabase Setup](#2-supabase-setup)
  - [3. Backend Setup (FastAPI)](#3-backend-setup-fastapi)
  - [4. Flutter App Setup](#4-flutter-app-setup)
  - [5. React Dashboard Setup](#5-react-dashboard-setup)
- [Running the Project](#running-the-project)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Deployment](#deployment)
- [Development Roadmap](#development-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

FasalSetu (फसलसेतु — meaning "Crop Bridge") is a full-stack AI-powered platform that digitises the entire crop lifecycle for Indian farmers enrolled in PMFBY (Pradhan Mantri Fasal Bima Yojana). Instead of verifying insurance claims only after crop damage occurs, FasalSetu creates a **complete digital crop journey** — from sowing to harvest — that serves as tamper-proof evidence for insurance verification.

The platform serves three user types:

| User | Surface | Purpose |
|---|---|---|
| **Farmer** | Flutter mobile app (Android/iOS) | Register farms, track crop stages, upload geo-tagged photos, submit claims |
| **Insurance Officer** | React web dashboard | Review claims, view AI analysis, approve/reject/inspect |
| **Admin** | React web dashboard | Analytics, user management, fraud monitoring, reports |

---

## The Problem We Solve

Current PMFBY challenges that FasalSetu addresses:

- Manual crop damage assessment — slow and subjective
- Fraudulent insurance claims with recycled or fake images
- No crop lifecycle tracking before damage occurs
- No real-time crop health monitoring
- High dependency on physical surveyors
- Difficult land ownership and damage verification
- Slow claim processing — farmers wait months

---

## Our Solution

```
Farm Registration
      ↓
Crop Lifecycle Tracking (5 stages)
      ↓
AI Crop Health Analysis (YOLOv8 + EfficientNet)
      ↓
Disease & Pest Detection
      ↓
AI Advisory to Farmer
      ↓
Damage Detection
      ↓
Fraud Detection Engine
      ↓
Trust Score Generation
      ↓
Insurance Verification & Claim Decision
```

---

## Key Innovations

**1. Crop Lifecycle-Based Insurance Verification**
Instead of a single damage image, officers see the complete 5-stage crop journey — sowing, germination, vegetative, flowering, and pre-harvest — as evidence.

**2. Farm Trust Score**
Each farm receives a 0–100 trust score based on GPS consistency (25 pts), lifecycle completeness (25 pts), weather validation (20 pts), image originality (20 pts), and document validity (10 pts).

**3. Geo-Fenced Evidence**
Every photo uploaded is GPS-verified against the registered farm boundary using Shapely polygon containment with a 50-metre buffer.

**4. AI Advisory System**
Farmers receive bilingual (Hindi + English) disease and pest advisories automatically after each AI analysis — helping them act before damage becomes irreversible.

**5. Faster PMFBY Processing**
Farms with high trust scores receive fast-track claim processing. Officers see AI-generated recommendations (Approve / Reject / Needs Inspection) alongside each claim.

---

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│  Flutter App     │    │  React Dashboard  │    │   React Dashboard  │
│  (Farmer)        │    │  (Officer)        │    │   (Admin)          │
└────────┬────────┘    └────────┬─────────┘    └──────────┬─────────┘
         │                      │                          │
         └──────────────────────┼──────────────────────────┘
                                │  REST API (JWT Auth)
                    ┌───────────▼───────────┐
                    │   FastAPI Backend      │
                    │   (Render)             │
                    │                        │
                    │  ┌─────────────────┐  │
                    │  │  Auth Service   │  │
                    │  │  Farm Service   │  │
                    │  │  Crop Service   │  │
                    │  │  Claim Service  │  │
                    │  │  Fraud Engine   │  │
                    │  │  AI Pipeline    │  │
                    │  └─────────────────┘  │
                    └───────────┬───────────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
    ┌──────────▼───┐  ┌────────▼──────┐  ┌─────▼──────────┐
    │  Supabase    │  │  Supabase     │  │  Open-Meteo    │
    │  PostgreSQL  │  │  Storage      │  │  Weather API   │
    │  + Auth      │  │  (Images)     │  │                │
    └──────────────┘  └───────────────┘  └────────────────┘
```

---

## Tech Stack

### Mobile App
| Technology | Purpose |
|---|---|
| Flutter 3.19+ | Cross-platform mobile framework |
| Riverpod 2.5 | State management |
| GoRouter 13 | Navigation with auth guards |
| Flutter Map 6 | OpenStreetMap boundary drawing |
| Dio 5 | HTTP client with JWT interceptor |
| Supabase Flutter 2 | Auth + Realtime |
| flutter_localizations | English + Hindi i18n |
| Geolocator 11 | GPS for geo-tagged images |
| Image Picker 1 | Camera + gallery upload |

### Web Dashboard
| Technology | Purpose |
|---|---|
| React 18 + TypeScript | UI framework |
| Vite 5 | Build tool |
| Tailwind CSS 3 | Styling |
| React Router 6 | Role-based routing |
| TanStack Query 5 | Server state management |
| Axios | API client |
| React Leaflet 4 | Farm maps |
| Recharts | Analytics charts |
| Headless UI 2 | Accessible modals |
| React Hook Form + Zod | Form validation |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI 0.111 | REST API framework |
| SQLAlchemy 2 (async) | ORM |
| asyncpg | PostgreSQL async driver |
| Alembic | Database migrations |
| Pydantic v2 | Request/response validation |
| Supabase Python 2.4 | Auth + Storage SDK |
| httpx | Async HTTP (Supabase REST) |
| Shapely 2 | GPS geo-fence verification |
| ImageHash 4 | pHash for duplicate detection |
| Pillow 10 | Image processing |
| structlog | Structured JSON logging |

### Database & Infrastructure
| Technology | Purpose |
|---|---|
| Supabase PostgreSQL | Primary database with RLS |
| Supabase Auth | Email OTP + password auth |
| Supabase Storage | Crop & claim image storage |
| Open-Meteo API | Historical weather validation |
| Vercel | React dashboard hosting |
| Render | FastAPI backend hosting |
| GitHub Actions | CI/CD |

### AI / ML
| Technology | Purpose |
|---|---|
| YOLOv8 | Crop disease & pest detection |
| EfficientNet | Crop health classification |
| OpenCV | Image preprocessing |
| PyTorch | Model inference |
| Google Colab | Model training |

---

## Repository Structure

```
fasalsetu/
│
├── mobile-app/                    # Flutter Farmer App
│   ├── lib/
│   │   ├── core/
│   │   │   ├── constants/         # App constants, colors
│   │   │   ├── extensions/        # Dart extensions
│   │   │   ├── network/           # Dio client with interceptors
│   │   │   ├── providers/         # Auth + language providers
│   │   │   ├── router/            # GoRouter with auth guards
│   │   │   ├── theme/             # Material 3 theme
│   │   │   └── utils/             # Utility functions
│   │   ├── features/
│   │   │   ├── auth/              # Email OTP login
│   │   │   ├── farm/              # Farm registration + boundary map
│   │   │   ├── crop/              # Lifecycle tracking + image upload
│   │   │   ├── advisory/          # AI recommendations
│   │   │   ├── claims/            # Insurance claim submission
│   │   │   └── profile/           # Settings, language toggle
│   │   ├── l10n/                  # English + Hindi ARB files (80+ keys)
│   │   └── shared/                # Reusable widgets
│   ├── assets/
│   │   ├── fonts/                 # NotoSansDevanagari
│   │   ├── images/
│   │   └── lottie/
│   └── pubspec.yaml
│
├── dashboard/                     # React Officer + Admin Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                # Button, Input, Badge, Card, Modal, Skeleton
│   │   │   ├── layout/            # Sidebar, Navbar, PageHeader
│   │   │   └── charts/            # StatCard, analytics components
│   │   ├── context/               # AuthContext (JWT + role management)
│   │   ├── hooks/                 # useAuth, useMediaQuery
│   │   ├── layouts/               # DashboardLayout, AuthLayout
│   │   ├── pages/
│   │   │   ├── auth/              # Login page
│   │   │   ├── officer/           # Claims, fraud dashboard
│   │   │   └── admin/             # Analytics, users, settings
│   │   ├── routes/                # ProtectedRoute, RoleGuard
│   │   ├── services/              # Axios API clients
│   │   ├── types/                 # TypeScript interfaces
│   │   └── utils/                 # formatDate, formatCurrency, cn()
│   ├── .env.example
│   └── package.json
│
├── backend/                       # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/routes/         # auth, farms, crops, images, claims, fraud, admin
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic settings from .env
│   │   │   ├── security.py        # JWT validation via Supabase secret
│   │   │   ├── supabase.py        # Auth client (anon) + admin client (service key)
│   │   │   ├── geofence.py        # Shapely GPS boundary check
│   │   │   ├── image_utils.py     # pHash, image validation
│   │   │   ├── storage.py         # Supabase Storage upload
│   │   │   ├── logging.py         # structlog setup
│   │   │   └── exceptions.py      # Custom exceptions + handlers
│   │   ├── models/                # SQLAlchemy ORM models (14 tables)
│   │   ├── schemas/               # Pydantic v2 DTOs
│   │   ├── repositories/          # Database query layer
│   │   ├── services/              # Business logic layer
│   │   ├── ai/                    # AI inference pipelines (Phase 10+)
│   │   └── fraud/                 # Fraud + trust score engine (Phase 11+)
│   ├── alembic/                   # Database migrations
│   ├── tests/                     # pytest test suite
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
│
├── ai-models/                     # AI Training & Inference
│   ├── notebooks/                 # Google Colab training notebooks
│   │   ├── 01_disease_detection_yolov8.ipynb
│   │   └── 02_health_classification_efficientnet.ipynb
│   ├── datasets/                  # Dataset labels and splits
│   ├── trained/                   # Exported .pt / .onnx models
│   └── inference/                 # FastAPI-ready inference wrappers
│
├── docs/                          # Documentation
│   ├── architecture/              # System diagrams
│   ├── api/                       # OpenAPI spec
│   └── adr/                       # Architecture Decision Records
│
├── scripts/                       # Automation scripts
│   ├── setup.sh                   # One-command dev environment setup
│   └── seed.sql                   # Test data seeding
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml         # Python lint + test
│       └── dashboard-ci.yml       # TypeScript lint + build
│
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore
```

---

## Features

### Farmer Mobile App (Flutter)

- **Authentication** — Email OTP login via Supabase Auth (no SMS, fully free)
- **Bilingual UI** — Complete English and Hindi support with runtime language switching
- **Farm Registration** — 3-step form: location details → crop info → GPS boundary drawing on OpenStreetMap
- **Boundary Drawing** — Tap-to-add polygon points, undo/clear, auto-locate to current GPS position
- **Crop Lifecycle Tracking** — 5 stages: Sowing → Germination → Vegetative → Flowering → Pre-Harvest
- **Geo-Tagged Image Upload** — Camera/gallery with automatic GPS tagging and fence verification
- **Visual Stage Timeline** — Color-coded cards with expand/collapse, image thumbnails, outside-fence warnings
- **AI Advisory** — Disease and pest alerts with Hindi/English descriptions
- **Insurance Claims** — Damage photo upload, damage type selection, estimated loss, real-time status
- **Profile & Settings** — Language toggle, notification preferences

### Officer Dashboard (React)

- **Role-Based Access** — Only officers and admins can login; farmers are blocked
- **Claim Management** — List, filter, and review submitted claims
- **Crop Timeline Viewer** — Complete 5-stage photo timeline per farm
- **AI Analysis Display** — Disease reports, health scores, confidence levels
- **Fraud Dashboard** — GPS score, lifecycle score, weather score, hash score, trust score
- **Claim Decision** — Approve / Reject / Needs Inspection with officer notes
- **Responsive Design** — Desktop sidebar, mobile hamburger drawer

### Admin Dashboard (React)

- **Analytics** — Farmer registrations, claim statistics, disease trends
- **User Management** — View and manage all farmers, officers, and admins
- **Fraud Analytics** — District-level fraud patterns
- **Disaster Monitoring** — Active weather events affecting registered farms
- **Reports** — Exportable claim and analytics reports

---

## Database Schema

FasalSetu uses 14 tables in Supabase PostgreSQL with Row-Level Security (RLS) on every table.

```
users               — Farmer, officer, admin profiles
farms               — Registered farm details
farm_boundaries     — GeoJSON polygon boundaries
crop_stages         — 5 lifecycle stages per farm
crop_images         — Geo-tagged uploaded images
disease_reports     — YOLOv8 AI detection results
advisories          — Bilingual farmer recommendations
claims              — Insurance claim submissions
claim_images        — Damage evidence photos
fraud_reports       — 5-signal fraud scoring per claim
trust_scores        — Composite farm trust scores
notifications       — Bilingual push notifications
audit_logs          — Complete action history
```

**RLS Policies:**
- Farmers only see their own farms, images, advisories, and claims
- Officers and admins see all farms and claims
- Only admins can view audit logs and fraud reports

---

## API Reference

All endpoints are prefixed with `/api/v1`. Interactive documentation is available at `http://localhost:8000/docs` when running locally.

### Authentication
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/otp/send` | Send OTP to farmer email | None |
| POST | `/auth/otp/verify` | Verify OTP → receive JWT | None |
| POST | `/auth/login` | Email + password login (officer/admin) | None |
| GET | `/auth/me` | Get current user profile | Bearer |
| PUT | `/auth/me` | Update current user profile | Bearer |

### Farms
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/farms` | Register farm with GPS boundary | Farmer |
| GET | `/farms/my` | List current farmer's farms | Farmer |
| GET | `/farms` | List all farms (paginated) | Officer/Admin |
| GET | `/farms/{id}` | Get farm details | Farmer/Officer |
| PUT | `/farms/{id}` | Update farm details | Farmer |
| PUT | `/farms/{id}/boundary` | Update GPS boundary | Farmer |
| DELETE | `/farms/{id}` | Soft delete farm | Farmer |

### Crop Lifecycle
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/crops/{farm_id}/stages` | Create/update a crop stage | Farmer |
| PUT | `/crops/{farm_id}/stages/{id}` | Update stage details | Farmer |
| POST | `/crops/{farm_id}/stages/{id}/complete` | Mark stage complete | Farmer |
| GET | `/crops/{farm_id}/timeline` | Full 5-stage timeline with images | Farmer/Officer |
| GET | `/crops/{farm_id}/images` | All uploaded images for a farm | Farmer/Officer |

### Images
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/images/upload` | Upload geo-tagged crop image (multipart) | Farmer |

### Claims
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/claims` | Submit insurance claim | Farmer |
| GET | `/claims` | List claims (role-filtered) | Officer/Admin |
| GET | `/claims/{id}` | Claim details with AI report | Farmer/Officer |
| PUT | `/claims/{id}/decision` | Approve/Reject/Inspect | Officer |

### Fraud & Trust
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/fraud/{claim_id}` | Fraud report for a claim | Officer/Admin |
| GET | `/trust/{farm_id}` | Farm trust score breakdown | Officer/Admin |

### Admin
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/admin/analytics/overview` | Dashboard KPIs | Admin |
| GET | `/admin/users` | User management list | Admin |
| PUT | `/admin/users/{id}/role` | Change user role | Admin |

---

## Fraud Detection Engine

FasalSetu scores every claim across five weighted signals:

| Signal | Weight | How It Works |
|---|---|---|
| **GPS Consistency** | 25 pts | All uploaded images must have GPS coordinates inside the registered farm boundary (Shapely polygon + 50m buffer) |
| **Lifecycle Completeness** | 25 pts | At least 3 of 5 lifecycle stages must have verified uploads before the claim date |
| **Weather Validation** | 20 pts | Open-Meteo historical data must match the declared damage type (drought/flood/hail) at the farm coordinates |
| **Image Originality** | 20 pts | pHash (perceptual hash) comparison detects duplicate or recycled images across different farmers |
| **Document Validity** | 10 pts | Land records and KYC documents must be present and not expired |

**Output:**
- `fraud_score` (0–100): Higher = more suspicious
- `trust_score` (0–100): Higher = more trustworthy
- `grade`: A (80+), B (60+), C (40+), D (20+), F (below 20)
- `flags`: List of specific anomalies detected

---

## Prerequisites

Ensure the following are installed before setup:

| Tool | Version | Download |
|---|---|---|
| Flutter | 3.19+ | https://flutter.dev/docs/get-started/install |
| Dart | 3.3+ | Included with Flutter |
| Python | 3.11+ | https://python.org |
| Node.js | 20+ | https://nodejs.org |
| npm | 10+ | Included with Node.js |
| Git | Any | https://git-scm.com |
| Android Studio / Xcode | Latest | For Flutter emulators |

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/fasalsetu.git
cd fasalsetu
```

### 2. Supabase Setup

**a) Create a Supabase project**

1. Go to [supabase.com](https://supabase.com) → New Project
2. Name: `fasalsetu`, Region: `ap-south-1` (South Asia)
3. Save your database password

**b) Configure Auth**

Go to **Authentication → Providers → Email**:
- Enable Email provider ✓
- Disable "Confirm email" (we use OTP magic link)
- Set OTP expiry to 600 seconds

**c) Run the database schema**

Open **Supabase Dashboard → SQL Editor** and run these files in order:

```sql
-- Run Block 1: Extensions and enums
-- Run Block 2: Users table + trigger
-- Run Block 3: Farms and boundaries
-- Run Block 4: Crop stages and images
-- Run Block 5: Disease reports and advisories
-- Run Block 6: Claims and claim images
-- Run Block 7: Fraud reports and trust scores
-- Run Block 8: Notifications and audit logs
```

The complete SQL is in `docs/schema.sql`.

**d) Run RLS policies**

```sql
-- Run docs/rls_policies.sql
```

**e) Create storage buckets**

Go to **Storage → New Bucket** and create:
- `crop-images` (private, 10MB limit)
- `claim-images` (private, 10MB limit)
- `documents` (private, 5MB limit)

Then run `docs/storage_policies.sql`.

**f) Create test accounts**

Go to **Authentication → Users → Add user → Create new user** (not Invite):

| Email | Password | Role |
|---|---|---|
| `farmer@fasalsetu.com` | `123456` | farmer |
| `officer@fasalsetu.com` | `Test@1234` | officer |
| `admin@fasalsetu.com` | `Test@1234` | admin |

Then run in SQL Editor:
```sql
UPDATE public.users SET role = 'officer', full_name = 'Test Officer'
WHERE email = 'officer@fasalsetu.com';

UPDATE public.users SET role = 'admin', full_name = 'Test Admin'
WHERE email = 'admin@fasalsetu.com';
```

---

### 3. Backend Setup (FastAPI)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `backend/.env` with your values:

```bash
# Supabase — from Settings → API
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-secret-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Database — use Transaction Pooler from Settings → Database → Connection string
# IMPORTANT: Use the pooler URL (port 6543), not direct connection (port 5432)
DATABASE_URL=postgresql+asyncpg://postgres.your-project-id:your-password@aws-0-ap-south-1.pooler.supabase.com:6543/postgres

# App
APP_ENV=development
APP_SECRET_KEY=generate-a-random-64-char-string-here
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Open-Meteo (no key needed)
OPEN_METEO_BASE_URL=https://archive-api.open-meteo.com/v1
```

> ⚠️ **Important**: Use the **Transaction Pooler** connection string from Supabase (port 6543), not the direct connection string (port 5432). The direct connection fails DNS resolution in some network environments.

---

### 4. Flutter App Setup

```bash
cd mobile-app

# Install dependencies
flutter pub get

# Generate localisation files
flutter gen-l10n

# Generate Riverpod providers (if using code generation)
dart run build_runner build --delete-conflicting-outputs
```

Download NotoSansDevanagari fonts from [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari) and place in `mobile-app/assets/fonts/`:
- `NotoSansDevanagari-Regular.ttf`
- `NotoSansDevanagari-Medium.ttf`
- `NotoSansDevanagari-Bold.ttf`

Create a `.env` equivalent by editing `lib/core/constants/app_constants.dart`:

```dart
static const String apiBaseUrl = 'http://10.0.2.2:8000/api/v1'; // Android emulator
// static const String apiBaseUrl = 'http://localhost:8000/api/v1'; // iOS simulator
static const String supabaseUrl = 'https://your-project-id.supabase.co';
static const String supabaseAnonKey = 'your-anon-key';
```

Or pass via `--dart-define` at run time:

```bash
flutter run \
  --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1 \
  --dart-define=SUPABASE_URL=https://your-project-id.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=your-anon-key
```

---

### 5. React Dashboard Setup

```bash
cd dashboard

# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

Edit `dashboard/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_APP_NAME=FasalSetu Dashboard
```

---

## Running the Project

You need three terminals running simultaneously for full local development.

### Terminal 1 — FastAPI Backend

```bash
cd fasalsetu/backend
source venv/bin/activate    # Windows: venv\Scripts\activate
python run.py
```

Backend runs at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

Expected output:
```
INFO: Started server process
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 — React Dashboard

```bash
cd fasalsetu/dashboard
npm run dev
```

Dashboard runs at: **http://localhost:5173**

Login with:
- Officer: `officer@fasalsetu.com` / `Test@1234` → redirects to `/officer`
- Admin: `admin@fasalsetu.com` / `Test@1234` → redirects to `/admin`

### Terminal 3 — Flutter App

```bash
cd fasalsetu/mobile-app

# List available devices
flutter devices

# Run on Android emulator
flutter run

# Run on specific device
flutter run -d <device-id>

# Run with hot reload
flutter run --hot
```

Login with:
- Farmer: `farmer@fasalsetu.com` → OTP sent to email → enter 6-digit code

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | ✓ | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | ✓ | Supabase anon/public key (for auth) |
| `SUPABASE_SERVICE_KEY` | ✓ | Supabase service role key (for admin ops) |
| `SUPABASE_JWT_SECRET` | ✓ | JWT secret from Supabase Settings → API |
| `DATABASE_URL` | ✓ | asyncpg connection string (use pooler URL) |
| `APP_ENV` | ✓ | `development` or `production` |
| `APP_SECRET_KEY` | ✓ | Random 64-char secret for the app |
| `ALLOWED_ORIGINS` | ✓ | Comma-separated CORS origins |
| `OPEN_METEO_BASE_URL` | — | Defaults to Open-Meteo archive URL |

### Dashboard (`dashboard/.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | ✓ | FastAPI backend base URL |
| `VITE_SUPABASE_URL` | ✓ | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | ✓ | Supabase anon key |
| `VITE_APP_NAME` | — | Defaults to "FasalSetu Dashboard" |

> ⚠️ Never commit `.env` files. They are in `.gitignore`.

---

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Test Individual API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Officer login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"officer@fasalsetu.com","password":"Test@1234"}'

# Get my farms (with JWT token)
curl http://localhost:8000/api/v1/farms/my \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Flutter Tests

```bash
cd mobile-app
flutter test
```

### Dashboard Tests

```bash
cd dashboard
npm run build   # TypeScript compile check
```

---

## Deployment

### Backend → Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repository
4. Set Root Directory to `backend`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Add all environment variables from `backend/.env`
8. Deploy

### Dashboard → Vercel

```bash
cd dashboard
npm install -g vercel
vercel --prod
```

Or connect GitHub repo in Vercel dashboard and set:
- Root Directory: `dashboard`
- Build Command: `npm run build`
- Output Directory: `dist`
- Add all environment variables

### Flutter App → Play Store / App Store

```bash
cd mobile-app

# Android APK
flutter build apk --release --dart-define=API_BASE_URL=https://your-render-url.onrender.com/api/v1

# Android App Bundle (for Play Store)
flutter build appbundle --release

# iOS (requires macOS + Xcode)
flutter build ios --release
```

---

## Development Roadmap

| Phase | Description | Status |
|---|---|---|
| 1 | Project Planning & Architecture | ✅ Complete |
| 2 | Supabase Setup (schema, RLS, storage) | ✅ Complete |
| 3 | FastAPI Backend Scaffold | ✅ Complete |
| 4 | Flutter App Scaffold | ✅ Complete |
| 5 | React Dashboard Scaffold | ✅ Complete |
| 6 | Authentication (OTP + password + JWT) | ✅ Complete |
| 7 | Farm Registration + GPS Boundary | ✅ Complete |
| 8 | Crop Lifecycle + Image Upload | ✅ Complete |
| 9 | AI Model Training (YOLOv8 + EfficientNet) | 🔄 In Progress |
| 10 | AI Integration with FastAPI | ⏳ Pending |
| 11 | Fraud Detection Engine | ⏳ Pending |
| 12 | Claim Management | ⏳ Pending |
| 13 | Admin Dashboard | ⏳ Pending |
| 14 | Testing | ⏳ Pending |
| 15 | Deployment | ⏳ Pending |
| 16 | Documentation | ⏳ Pending |

---

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add: your feature description'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please read `CONTRIBUTING.md` for code style guidelines and branch naming conventions.

---

## Troubleshooting

**Backend fails to start with `ImportError`**
Make sure your virtual environment is activated and all packages are installed: `pip install -r requirements.txt`

**`[Errno 11003] getaddrinfo failed` on Windows**
Your `DATABASE_URL` is using the direct Supabase connection string. Switch to the Transaction Pooler URL (port 6543) from Supabase → Settings → Database → Connection string → Transaction tab.

**Flutter `flutter gen-l10n` fails**
Ensure `l10n.yaml` is in the `mobile-app/` root directory and both `lib/l10n/app_en.arb` and `lib/l10n/app_hi.arb` exist.

**React dashboard stays on `/login` after signing in**
Check that `dashboard/.env` exists (not just `.env.example`) and `VITE_API_BASE_URL` points to your running backend.

**Supabase invite fails with "Database error saving new user"**
Use **Create new user** (not Invite) in Supabase Auth UI, with Auto Confirm enabled.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

<div align="center">

**Built with ❤️ for Indian Farmers**

FasalSetu — फसलसेतु — Bridging the Gap Between Farming and Insurance

</div>
