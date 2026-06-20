# EcoSphere: Carbon Footprint Awareness Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi&logoColor=white)](#)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?logo=react&logoColor=black)](#)
[![Vite](https://img.shields.io/badge/Vite-5.3.1-646CFF?logo=vite&logoColor=white)](#)
[![Gemini](https://img.shields.io/badge/Gemini%20API-google--genai-orange)](#)

EcoSphere is a production-grade, full-stack application designed to educate and empower individuals to track, understand, and reduce their carbon footprint. The platform combines a robust multi-source Python ETL pipeline, a responsive FastAPI backend, a state-of-the-art React/Vite dashboard, and an AI Climate Coach powered by the modern Google `google-genai` SDK.

---

## 📖 Table of Contents
1. [Key Features](#-key-features)
2. [Architecture Overview](#%EF%B8%8F-architecture-overview)
3. [Folder Structure](#-folder-structure)
4. [Environment Variables](#-environment-variables)
5. [Local Development Setup](#%EF%B8%8F-local-development-setup)
6. [Running the Data Pipeline](#-running-the-data-pipeline)
7. [Running Tests](#-running-tests)
8. [Future Roadmap](#-future-roadmap)

---

## ✨ Key Features

### 1. Robust Data Pipeline (ETL)
- **Ingestion & Validation**: Cleans raw datasets (FAO dietary logs, EPA GHG Hub files, UN country metrics) with strict type coercions and range validators.
- **Feature Engineering**: Derives advanced variables like commute carbon intensity, clean energy mix shares, and diet-based carbon tiers.
- **Lineage Tracking**: Autogenerates a `feature_lineage.json` and a data dictionary documenting formulas and parent sources for all features.

### 2. AI Climate Coach (Gemini & RAG)
- **Modern SDK Integration**: Uses the official Google `google-genai` library.
- **Tiered Fallback Strategy**: Guarantees helpful, user-friendly responses. Fallbacks degrade gracefully from RAG Q&A (using FAISS index matching EPA guidelines) to user profile facts, and finally to simulated demo data.
- **Dynamic Clarification**: Automatically prompts for guided clarification on vague user prompts.
- **Personalized Greetings**: Dynamically greets authenticated users by name instead of using hardcoded mock placeholders.

### 3. Analytics Dashboard & UX
- **Page-by-Page Polish**: Clean UI rendering realistic mock cards and charts (using Recharts) whenever backend data is missing or empty.
- **Theme Selection**: Dark/Light mode toggle with unified CSS variables.
- **Dynamic Carbon Calculator**: Inputs travel, home energy, waste, and food to immediately calculate a detailed footprint breakdown.

---

## 🛠️ Architecture Overview

```
 ┌───────────────────────┐       ┌──────────────────────┐
 │   React / Vite UI     │ ◄───► │   FastAPI Backend    │
 │ (Recharts, Tailored)  │       │ (App Core & Routes)  │
 └───────────────────────┘       └──────────┬───────────┘
                                            │
                                  ┌─────────▼─────────┐
                                  │  AI Climate Coach │
                                  │   (Gemini + RAG)  │
                                  └─────────┬─────────┘
                                            │
                                  ┌─────────▼─────────┐
                                  │    FAISS Index    │
                                  │ (EPA Guidelines)  │
                                  └───────────────────┘
```

---

## 📁 Folder Structure

```
carbon_footprint_platform/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # API Route Controllers (Health, Carbon, Users, LLM, RAG)
│   │   ├── core/             # App Config, Logging, Security
│   │   ├── db/               # SQLAlchemy Session and Database Models
│   │   ├── schemas/          # Pydantic Schemas for Requests/Responses
│   │   └── services/         # Business Logic Layer (RAG Service, Carbon Engine)
│   └── tests/                # FastAPI Endpoint Integration Tests
├── datasets/                 # Datasets Managed by the Pipeline
│   ├── raw/                  # Raw Source CSV/XLSX Files
│   ├── cleaned/              # Standardized Datasets (Ignored in Git)
│   ├── engineered/           # Calculated Features (Ignored in Git)
│   └── merged/               # Final Master CSV and Summary Reports (Ignored in Git)
├── docs/                     # Data Dictionary and Feature Reference Documentation
├── frontend/                 # React & Vite Frontend Codebase
│   ├── src/
│   │   ├── api/              # Axios Client Instances
│   │   ├── components/       # Custom Skeletons, Empty States, Charts, Cards
│   │   ├── context/          # Global App Context & Themes
│   │   ├── pages/            # Dashboard, CarbonBreakdown, Journey, Profile, Settings
│   │   └── services/         # Frontend Data Layer with Centralized Fallback Helpers
├── knowledge_base/           # RAG Source Documents (e.g., epa_guidelines.md)
├── src/                      # Core Shared Python Logic
│   ├── cleaning/             # Dataset Loaders & Cleaners
│   ├── feature_engineering/  # Category-specific Feature Builders
│   ├── integration/          # Safe Merging & Feature Lineage Trackers
│   ├── llm/                  # Gemini Client & Fallback Logic
│   ├── rag/                  # Retriever & FAISS Vectorizer
│   └── utils/                # Logging, safe I/O, Country Maps
├── tests/                    # Backend Unit and Integration Tests (pytest)
├── pipeline.py               # ETL Pipeline Executable Entry Point
├── config.py                 # Central Pipeline Configuration file
├── requirements.txt          # Pinned Backend Dependencies
└── README.md                 # Project Documentation
```

---

## 🔑 Environment Variables

To run the backend and connect to Google Gemini, copy `.env.example` to `.env` and fill in the values:

```env
# Gemini API Key (Generate at: https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Frontend API URL configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## ⚙️ Local Development Setup

### Prerequisites
- Python 3.10 or higher
- Node.js v18+ and npm v9+

### 1. Backend Setup
Navigate to the root directory and set up a virtual environment:
```bash
# Navigate to platform directory
cd carbon_footprint_platform

# Create virtual env
python -m venv .venv

# Activate virtual env
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn backend.app.main:app --reload
```
The backend API docs will be active at `http://localhost:8000/docs`.

### 2. Frontend Setup
Open a separate terminal window:
```bash
# Navigate to frontend folder
cd carbon_footprint_platform/frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Open your browser and navigate to the local address displayed (typically `http://localhost:5173/`).

---

## 🚀 Running the Data Pipeline

The data pipeline can be run in stages or end-to-end:

```bash
# Run the entire pipeline (all 3 stages)
python pipeline.py

# Run only Stage 1 (Data Cleaning)
python pipeline.py --stage clean

# Run Stage 1 & Stage 2 (Cleaning + Feature Engineering)
python pipeline.py --stage features

# Run with verbose debugging logs
python pipeline.py --verbose
```

---

## 🧪 Running Tests

Ensure your virtual environment is active, then run pytest from the root folder:

```bash
# Run all unit tests
pytest tests/ -v

# Run backend API integration tests
pytest backend/tests/ -v
```

---

## 🗺️ Future Roadmap

1. **Production Vector Store**: Migrate RAG indexing from standard FAISS memory buffers to a production vector database (e.g. Pinecone or pgvector).
2. **Real-time Electricity Grid API Integration**: Connect home energy calculations directly to regional grid APIs (like Electricity Maps) for live grid carbon intensity tracking.
3. **Peer Comparison League**: Implement user groups and leaderboard comparisons based on national/regional carbon footprint averages.
4. **Mobile Apps**: Package the responsive web app using React Native/Capacitor for mobile deployment.
