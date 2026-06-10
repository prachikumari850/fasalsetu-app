# 🌾 FasalSetu – AI-Powered Crop Lifecycle Monitoring & Smart Insurance Verification Platform

> **From Crop Monitoring to Trusted Insurance Claims**

FasalSetu is an AI-powered agricultural platform designed to modernize crop monitoring, farmer support, and crop insurance verification under the Pradhan Mantri Fasal Bima Yojana (PMFBY).

The platform creates a complete digital crop journey by continuously tracking crop growth stages, analyzing crop health using AI, detecting diseases and pests, providing personalized advisories, and enabling fraud-resistant insurance claim verification.

Unlike traditional systems that rely on a single damage image and manual surveys, FasalSetu builds a verified crop history throughout the season, enabling faster, transparent, and more reliable claim processing.

---

## 🚀 Key Features

### 👨‍🌾 Farmer Mobile Application

* OTP Authentication
* Farm Registration
* Farm Boundary Mapping
* Crop Lifecycle Tracking
* Geo-Tagged Image Upload
* AI Crop Health Analysis
* Disease Detection
* Pest Detection
* Nutrient Deficiency Detection
* Personalized AI Advisory
* Insurance Claim Submission
* Claim Tracking
* Notifications & Alerts

### 🛡️ Insurance Officer Dashboard

* Claim Management
* Claim Verification
* Crop Timeline Viewer
* AI Damage Reports
* Fraud Risk Reports
* Trust Score Evaluation
* Approve / Reject / Inspect Claims

### 🏛️ Admin Dashboard

* Farmer Analytics
* Claim Analytics
* Disease Analytics
* Fraud Analytics
* Disaster Monitoring
* User Management
* Reports & Exports

---

# 🎯 Problem Statement

Current PMFBY claim verification depends heavily on manual field inspections, resulting in:

* Delayed claim settlement
* High operational costs
* Fraudulent claims
* Difficult ownership verification
* Lack of real-time crop monitoring
* Limited transparency

FasalSetu addresses these challenges through AI-powered crop lifecycle monitoring and smart insurance verification.

---

# 💡 Core Innovation

## Digital Crop Journey

Instead of verifying claims using a single damage image, FasalSetu records the complete crop lifecycle:

Farm Registration
→ Crop Monitoring
→ AI Analysis
→ Advisory
→ Damage Assessment
→ Fraud Detection
→ Trust Score
→ Insurance Verification

This provides a reliable and transparent evidence trail for insurance companies and government agencies.

---

# 🏗️ System Architecture

## High-Level Flow

Farmer App
↓
FastAPI Backend
↓
Supabase Database & Storage
↓
AI Models (YOLOv8 + EfficientNet)
↓
Fraud Detection Engine
↓
Trust Score Engine
↓
Insurance Officer Dashboard
↓
Admin Dashboard

---

## Crop Monitoring Flow

Farmer Uploads Image
↓
FastAPI API
↓
Supabase Storage
↓
OpenCV Preprocessing
↓
YOLOv8 Detection
↓
EfficientNet Classification
↓
Health Score Generation
↓
Database Update
↓
Dashboard Visualization

---

## Insurance Claim Flow

Damage Occurs
↓
Farmer Submits Claim
↓
GPS Validation
↓
Weather Validation
↓
AI Damage Assessment
↓
Fraud Detection
↓
Trust Score Generation
↓
Officer Review
↓
Approve / Reject

---

# 🔍 Fraud Detection Engine

FasalSetu implements a multi-layer fraud detection framework:

### Geo-Fencing Verification

Ensures uploaded images originate from the registered farm boundary.

### Crop Lifecycle Validation

Verifies historical crop growth evidence before claim submission.

### Duplicate Image Detection

Uses ImageHash to identify reused or manipulated images.

### Timestamp Verification

Validates image timestamps against crop season timelines.

### Weather Validation

Cross-checks reported damage with historical weather data using Open-Meteo.

### Multi-Point Farm Sampling

Collects evidence from multiple farm locations:

* North
* South
* East
* West
* Center

---

# 🛡️ Trust Score Engine

Each farm receives a dynamic trust score.

### Scoring Parameters

| Parameter         | Weight |
| ----------------- | ------ |
| GPS Consistency   | 25%    |
| Crop History      | 25%    |
| Image Originality | 20%    |
| Weather Match     | 15%    |
| Documents         | 15%    |

Example:

Trust Score: 91 / 100

Fraud Risk: LOW

---

# 🤖 AI Modules

## YOLOv8

Used for:

* Disease Detection
* Pest Detection
* Crop Damage Detection
* Bounding Box Generation

## EfficientNet

Used for:

* Crop Health Classification
* Damage Severity Classification
* Health Score Prediction

## OpenCV

Used for:

* Image Enhancement
* Image Preprocessing
* Feature Extraction

## ImageHash

Used for:

* Duplicate Detection
* Fraud Prevention

---

# 🗂️ Repository Structure

```bash
fasalsetu/

├── mobile-app/
│   ├── lib/
│   ├── assets/
│   └── test/
│
├── dashboard/
│   ├── src/
│   ├── public/
│   └── components/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── ai/
│   │   ├── fraud/
│   │   └── core/
│   └── tests/
│
├── ai-models/
│   ├── datasets/
│   ├── training/
│   ├── inference/
│   └── trained-models/
│
├── docs/
│
├── architecture/
│
├── scripts/
│
├── .github/
│
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

---

# 🛠️ Technology Stack

## Mobile Application

* Flutter
* Riverpod
* Dio
* GoRouter

## Web Dashboard

* React
* TypeScript
* Vite
* Tailwind CSS
* React Query
* React Router

## Backend

* FastAPI
* SQLAlchemy
* Pydantic
* Alembic

## Database

* Supabase PostgreSQL

## Authentication

* Supabase Auth

## Storage

* Supabase Storage

## AI & ML

* YOLOv8
* EfficientNet
* OpenCV
* PyTorch
* ImageHash

## Maps

* OpenStreetMap
* Leaflet
* Flutter Map

## Weather

* Open-Meteo API

## Deployment

* Vercel
* Render
* GitHub Actions

---

# 🌍 Expected Impact

### Farmers

* Early disease detection
* Improved crop productivity
* Faster claim settlement

### Insurance Companies

* Reduced fraud
* Faster claim verification
* Lower operational costs

### Government

* Transparent PMFBY implementation
* Better agricultural monitoring
* Improved insurance efficiency

---

# 🔮 Future Scope

* Satellite Verification (NDVI)
* Drone-Based Crop Monitoring
* Yield Prediction
* Flood & Drought Assessment
* Voice-Based Farmer Assistant
* Regional Language Support
* National PMFBY Integration

---

# 👥 Contributors

Built with ❤️ for smarter agriculture, transparent insurance verification, and empowered farmers.

---

## License

This project is licensed under the MIT License.
