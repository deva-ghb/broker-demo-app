# SellSmart — Architecture Document

SellSmart is a full-stack, AI-powered real estate sales intelligence platform. It consists of a FastAPI asynchronous backend, a Vite + React frontend, and uses MongoDB and Qdrant for data persistence and vector search. 

This document outlines the architecture for both the backend and frontend.

## 1. System Overview

```mermaid
graph TD
    Client[React Frontend (WebApp)] --> |REST / WebSockets| API[FastAPI Backend]
    API --> |Async Motor| DB[(MongoDB)]
    API --> |qdrant-client| Qdrant[(Qdrant Vector DB)]
    API --> |REST API| AzureOpenAI[Azure OpenAI]
```

## 2. Backend Architecture

The backend is built with **FastAPI** leveraging modern Python asynchronous (async/await) features. 

### 2.1 Directory Structure
- `api/`: FastAPI application setup (`main.py`) and API routers (`*_router.py`)
- `services/`: Core business logic and external integrations (`ai_client.py`, `database.py`, `qdrant_client.py`, etc.)
- `models/`: Pydantic models mapping directly to MongoDB schemas.
- `schemas/`: Pydantic models for API requests and responses.
- `templates/`: Jinja2 HTML templates used to render microsites.
- `static/`: Static files such as the vanilla JS tracking script (`tracker.js`).

### 2.2 Core Services

#### AI Client (`services/ai_client.py`)
A unified wrapper around Azure OpenAI supporting standard chat completions, structured JSON output (`response_format={"type": "json_object"}`), and streaming.

#### Database Service (`services/database.py`)
A singleton utilizing the `motor` asynchronous MongoDB driver. Exposes `connect_db()`, `close_db()`, and `get_collection()`.

#### Knowledge Base (`services/knowledge_base.py`)
Handles retrieving structured property data from MongoDB and performing semantic vector searches using Qdrant (based on property USP embeddings) to enrich AI prompts with grounded context.

#### The Four Core Modules
1. **Persona Service**: Handles multi-turn chat, injects knowledge base context, and orchestrates the final AI synthesis to generate a structured `PersonaDocument`.
2. **Microsite Service**: Takes a `PersonaDocument` and a `PropertyDocument`, uses AI to generate personalized image captions, and renders `templates/microsite.html`.
3. **Engagement Service**: Receives batched telemetry data from the client via POST requests. Aggregates dwell times and scroll metrics to update the `PersonaDocument` engagement history in MongoDB.
4. **Trigger Service**: A rules engine that runs post-aggregation. Evaluates engagement thresholds to spawn alerts (High Intent, Specific Interest, Completion). Leverages AI to generate custom talking points for the broker. Streams updates via WebSockets.

### 2.3 Data Models (MongoDB)
- **Persona**: Demographics, explicit motivations, and AI-inferred trust scores.
- **Property**: Static details, price ranges, available media assets, and USPs.
- **Microsite**: Links Persona + Property, stores rendered HTML and URL slug.
- **Engagement**: Raw telemetry events (`page_view`, `section_focus`, `cta_click`).
- **Trigger**: Marketable event fired by the rules engine with a confidence score.

## 3. Frontend Architecture

The frontend is a Single Page Application (SPA) built using **React and Vite**.

### 3.1 Design Philosophy
- **No external UI libraries**: The entire UI is built natively with vanilla CSS (`index.css`) containing a dark-mode theme, CSS variables for theming, and fully responsive layouts.
- **Hash-based Routing**: Built a custom routing layer (`window.location.hash`) inside `App.jsx` to avoid external dependencies like `react-router-dom` and cleanly integrate without advanced server-side routing setups.
- **Component-based Layout**: 
  - A persistent Sidebar layout wrapper.
  - Page-level React components representing the key domains.

### 3.2 Key Screens

1. **Dashboard (`Dashboard.jsx`)**
   - Renders top-level KPIs (Total Personas, Active Leads, Unread Triggers).
   - Polls `/api/v1/triggers/get` and `/api/v1/persona/` to display active pipelines.
   - Shows system health check (MongoDB/Qdrant connectivity).

2. **Persona Builder (`PersonaBuilder.jsx`)**
   - Iterative chat interface communicating with `POST /api/v1/persona/text-chat`.
   - Maintains a `session_id`. Renders a loading state during AI processing.
   - Upon completion, dynamically updates the UI to show a Persona Profile card featuring trust score and AI-recommended angles.

3. **Microsite Builder (`MicrositeBuilder.jsx`)**
   - Form for linking a `persona_id` with a `property_id`.
   - Displays real-time generated tracking links.

4. **Engagement Dashboard (`EngagementDashboard.jsx`)**
   - Looks up aggregated engagement via Tracking ID.
   - Renders scroll depth as a visual horizontal progress bar.
   - Lists relative section dwell times.

5. **Trigger Panel (`TriggerPanel.jsx`)**
   - Uses native `WebSocket` API to stream `/api/v1/triggers/stream`.
   - Renders unread broker notifications. Displays synthesized talking points.
   - Includes stateful filtering (Hot Lead vs Interest Signals vs Completions).
