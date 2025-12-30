This updated **Single Source of Truth (SSOT)** document for the **TIP (Travel Intelligence & Planner)** application has been revised to reflect that the backend is hosted on **Railway**, as confirmed in the current session context and infrastructure status,.

---

### **1. Project Identity & Mission**
*   **Project Name:** TIP - Travel Intelligence & Planner.
*   **Mission:** A decision-grade system providing travelers with accurate, legally compliant, actionable travel intelligence reports tailored to nationality, residency, budget, and dates.
*   **Non-Goals:** TIP is **not** a booking platform, social app, or travel blog.

---

### **2. Core Technology Stack**
| Layer | Technology | Key Details |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 16 (App Router)** | Tailwind v4, Radix UI, shadcn/ui. |
| **Backend** | **FastAPI (Python 3.11+)** | REST API, Pydantic V2, Asyncio,. |
| **Background Jobs** | **Celery + Redis** | Hosted on **Railway**,. |
| **Database** | **Supabase (PostgreSQL)** | 9 tables with Row-Level Security (RLS). |
| **Auth** | **Supabase Auth** | Email/Password + Google OAuth (PKCE Flow),. |
| **AI Agents** | **CrewAI** | Orchestration of 10 specialized agents using Claude 3.5 and GPT-4,,. |
| **Hosting** | **Vercel / Railway** | **Frontend on Vercel; Backend on Railway**,. |

---

### **3. Mandatory Developer Workflow (Rules)**
**Before Writing ANY Code:**
1.  Read the **Session Context** (`00-session-context.md`) to verify hosting and tech status.
2.  Follow the **TDD Workflow**: Write tests for each component/feature before implementation,.
3.  Use **PowerShell commands only** (e.g., use `ls`, not `dir /b`).

**Design System Compliance:**
*   **Colors:** **Blue** (Primary), **Amber** (Secondary), and **Slate** (Neutral),.
*   **Fonts:** **DM Sans** (Body) and **IBM Plex Mono** (Code),.
*   **Mode:** Support **Dark Mode** on ALL components,.

---

### **4. System Architecture: The Multi-Agent Pipeline**
The system uses an **Orchestrator Agent** to manage 10 specialized agents in a topological execution graph:
1.  **Visa & Entry:** (Critical) Requirements, stay duration, and official links.
2.  **Country:** Flag, politics, demographics, and safety.
3.  **Weather:** Forecasts and historical averages.
4.  **Currency:** Exchange rates and daily cost estimates.
5.  **Culture:** Etiquette, laws, and religious norms.
6.  **Food:** National dishes and restaurant recommendations.
7.  **Attractions:** Top sites, costs, and crowd indicators.
8.  **Itinerary:** (Critical) Synthesizes data into a weather-aware, budget-aligned schedule.
9.  **Flight:** Real-time prices and booking links.
10. **Orchestrator:** Coordinates parallel execution and validates outputs.

---

### **5. Milestone / Increment Map (Status)**
| ID | Name | Overall Status | Key Features |
| :--- | :--- | :--- | :--- |
| **I1** | **Foundation** | 85% | App shell, design tokens, routing,. |
| **I2** | **User Profile** | 25% | Traveler details, preferences, and account settings,. |
| **I3** | **Dashboard** | 75% | Recent trips, stats, and quick actions,. |
| **I4** | **Trip Wizard** | 0% | Multi-step form with auto-save and multi-city support,. |
| **I5-I7** | **Reports & Agents**| 0% | Backend agent implementation and report display,. |
| **I8-I10** | **Management** | 0% | PDF export, deletion scheduling, and analytics,. |

---

### **6. Critical Data & Security Constraints**
*   **Data Lifecycle:** All trip data is **automatically deleted 7 days after the trip ends** for GDPR compliance,.
*   **Security Blocker:** Never expose the `SUPABASE_SERVICE_ROLE_KEY` in the frontend; it is strictly for backend use.
*   **Validation:** All country codes must be 2-letter ISO uppercase (e.g., "US", "GB").

---

### **7. Infrastructure Status (Local & Production)**
*   **Local Development:** Uses Docker Compose; Backend runs on `localhost:8000` (Swagger docs at `/api/docs`),.
*   **Production Hosting:** 
    *   **Frontend:** Vercel (https://your-app.vercel.app).
    *   **Backend:** **Railway** (https://tip-backend.railway.app), which hosts the FastAPI app, Redis, and Celery workers,.
*   **Map Provider:** **Mapbox** is the canonical provider for interactive maps.

***

**Analogy:** If the TIP application were a high-performance vehicle, **Vercel** is the sleek dashboard and steering wheel the user interacts with, while **Railway** is the powerful engine room where the FastAPI "engine," Celery "transmission," and Redis "fuel line" all work together to power the heavy AI lifting.