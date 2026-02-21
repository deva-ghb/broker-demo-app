# SellSmart — Walkthrough & User Guide

Welcome to the SellSmart platform. This guide explains how to get the application up and running, block by block, and how to use the core features.

## Prerequisites
- Docker & Docker Compose
- Conda / Python environment manager
- Node.js & npm
- An Azure OpenAI Endpoint & Key

## 1. Setup & Installation

### Infrastructure
Ensure you have the `.env` file populated with your Azure OpenAI credentials. Start the supporting databases (MongoDB and Qdrant):
```bash
docker-compose up -d mongodb qdrant
```

### Backend (FastAPI)
Activate the provided conda environment, install dependencies, and seed the mock real estate data:
```bash
conda activate smartsell
pip install -r requirements.txt
python scripts/seed_data.py
```
Start the backend server on `localhost:8000`:
```bash
uvicorn api.main:app --reload
```

### Frontend (React + Vite)
In a separate terminal window, start the frontend development server:
```bash
cd webapp
npm install
npm run dev
```
Navigate to `http://localhost:5173`. The Vite proxy will automatically route `/api/*` and `/m/*` requests to your backend on port 8000.

---

## 2. Using the Platform

The UI is divided into 4 primary modules reflecting the broker lifecycle. 

### Step 1: Persona Builder (Lead Profiling)
Navigate to the **Persona Builder** tab.
1. Type details about an interaction with a client (e.g., "I met an investor from the UK looking for waterfront properties around $5M with a payment plan.")
2. The AI will ask follow-up questions to understand the exact motivation and filtering criteria.
3. Once satisfied, tell the AI "That's everything. Generate."
4. The backend will synthesize a structured `PersonaDocument` and present a Persona Card displaying the calculated Trust Score and an AI Sales Angle.

### Step 2: Microsite Generation
Navigate to the **Microsite Builder** tab.
1. Select the Persona you just generated from the dropdown.
2. Enter `prop_dubai_creek` or `prop_palm_villa` (from the seed data) into the Property ID field.
3. Click Generate.
4. SellSmart will construct a responsive, mobile-first HTML URL customized to that user's interests. E.g., if they emphasized ROI, the financial sections will be placed prominently in the generated layout.

### Step 3: Tracking Engagement
Copy the generated Microsite URL and open it in a new window to simulate the buyer.
1. Scroll through the page slowly.
2. Pause on the "Amenities" or "Pricing" section. The embedded `tracker.js` relies on standard `IntersectionObserver` to track exactly how many seconds you spend reading specific blocks.
3. Click the "Talk to Broker" CTA button at the top/bottom of the page.
4. When you leave or close the page, the batch of telemetry events is instantly fired to the backend.

### Step 4: Engagement Intelligence
Navigate to the **Engagement Dashboard**.
1. Select the Lead.
2. View metrics like: Total Page Views, Return Visit Count, Max Scroll Depth (e.g. 75%), and horizontal progress bars indicating high dwell time (e.g., spent 45s on "ROI Details").

### Step 5: AI Follow-Up Triggers
Navigate to the **Trigger Panel**.
1. If the engagement metrics hit configured thresholds (e.g., high dwell time on pricing + CTA click but no inbound call), the backend Trigger rules engine fires an event.
2. You will see an unread notification pop up in real-time (via WebSockets).
3. The notification will label the user configuration (e.g., `HOT LEAD`) and provide an exact **AI-generated Talking Point**. 
   > *Example: "Hi John, I saw you were heavily reviewing the payment plans for Dubai Creek. They actually just relaxed the post-handover terms—do you have 5 minutes to discuss?"*
