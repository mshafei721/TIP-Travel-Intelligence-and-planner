Based on the comprehensive project documentation and the current status of the **TIP (Travel Intelligence & Planner)** application, the following development plan is structured into sequential phases. This plan utilizes three specialized agents: **Frontend Developer (FE)**, **Backend Developer (BE)**, and **Integration Agent (INT)**.

### **Phase 1: Security Remediation & Core Fixes (Immediate)**
*Priority: Addressing the "NO-SHIP" audit and critical user testing bugs.*

*   **Task 1.1 [BE]: Critical Security & Environment Hardening**
    *   **Action:** Remove `SUPABASE_SERVICE_ROLE_KEY` from any client-side files and move strictly to Railway environment variables. Enable leaked password protection in Supabase.
    *   **Acceptance:** Backend starts without configuration errors; service role key is not found in frontend build.
*   **Task 1.2 [FE]: Dashboard & Layout Polish**
    *   **Action:** Center the empty state text on the dashboard. Update the "Create Your First Trip" button to route correctly to the wizard. Replace "Demo User" with real authenticated user data from Supabase Auth.
    *   **Acceptance:** UI matches design specs; authenticated name appears in the top-right menu.
*   **Task 1.3 [INT]: CI/CD & Performance Baseline**
    *   **Action:** Remove `continue-on-error` from CI workflows to ensure linting and type checks block deployments. Execute initial k6 load tests for `/api/health` and `/api/profile`.
    *   **Acceptance:** CI/CD pipeline turns red on failure; p95 latency documented for core endpoints.

---

### **Phase 2: Milestone I2 Completion (User Profile & Settings)**
*Priority: Finalizing the 90% complete profile system.*

*   **Task 2.1 [BE]: Profile API Stabilization**
    *   **Action:** Ensure all 7 profile endpoints (GET/PUT/DELETE) are fully operational and return correct data from the `user_profiles` and `traveler_profiles` tables.
    *   **Acceptance:** Swagger UI returns 200 OK for all profile CRUD operations.
*   **Task 2.2 [FE]: Profile UI & Photo Integration**
    *   **Action:** Implement the Supabase Storage photo upload flow in `ProfileSettingsPage`. Ensure traveler details (nationality/residency) use searchable dropdowns rather than text inputs.
    *   **Acceptance:** Photo persists after refresh; public URL is correctly updated in the database.
*   **Task 2.3 [INT]: End-to-End Profile Validation**
    *   **Action:** Run the automated integration test script (`integration_test_manual.py`) to verify the full flow from UI to Supabase RLS.
    *   **Acceptance:** 100% of the 19 manual and 11 automated test cases pass.

---

### **Phase 3: Milestone I4 (Trip Creation Wizard)**
*Priority: Building the multi-step input engine.*

*   **Task 3.1 [BE]: Trip CRUD & Draft Logic**
    *   **Action:** Implement `POST /api/trips` and `PATCH /api/trips/{id}` with idempotency headers. Build the draft auto-save backend to store partial trip data.
    *   **Acceptance:** Drafts are saved in the `trips` table with `status: 'draft'`.
*   **Task 3.2 [FE]: 4-Step Wizard UI**
    *   **Action:** Build the `TripCreationWizard` with progressive logic: Step 1 (Traveler), Step 2 (Destination/Multi-city), Step 3 (Details), and Step 4 (Preferences). Use searchable dropdowns for countries and cities.
    *   **Acceptance:** Wizard handles multi-city toggles and validates dates (future only) in real-time.
*   **Task 3.3 [INT]: Sync & Validation Integration**
    *   **Action:** Connect the frontend wizard to the backend API, ensuring debounced auto-saving works across sessions.
    *   **Acceptance:** User can close the browser and resume the trip creation from the last saved step.

---

### **Phase 4: Milestone I5 & I6 (AI Agent Implementation)**
*Priority: Orchestrating the 10 specialized intelligence agents.*

*   **Task 4.1 [BE]: Multi-Agent Pipeline & Scraping**
    *   **Action:** Implement the `OrchestratorAgent` using CrewAI to coordinate agents in parallel. Set up the 4-layer scraping strategy: official APIs, then SerpAPI/Playwright as fallbacks.
    *   **Acceptance:** Orchestrator validates outputs and retries failed agents up to 3 times.
*   **Task 4.2 [FE]: Report Display UI**
    *   **Action:** Build the interactive report with expandable cards for Visa, Weather, and Country intelligence. Add the real-time `GenerationStatus` polling component.
    *   **Acceptance:** UI displays partial results as agents finish; confidence badges (green/yellow/gray) are visible.
*   **Task 4.3 [INT]: Data Synthesis & Accuracy Check**
    *   **Action:** Verify that agents correctly pass data to the `ItineraryAgent` (e.g., WeatherAgent informing indoor/outdoor activities).
    *   **Acceptance:** The final report synthesized by the Orchestrator has an overall confidence score ≥ 70.

---

### **Phase 5: Milestone I7 & I8 (Itinerary & Management)**
*Priority: Providing actionable travel plans and offline access.*

*   **Task 5.1 [BE]: PDF Generation Service**
    *   **Action:** Implement server-side HTML-to-PDF rendering using Playwright. Set up the daily cron job for the `DeletionSchedule` to purge data 7 days after trip end.
    *   **Acceptance:** PDF includes all report sections and static Mapbox images; files are deleted after download.
*   **Task 5.2 [FE]: Visual Itinerary Builder**
    *   **Action:** Implement the `ItineraryTimeline` with drag-and-drop support and the Mapbox `MapView` for plotting attractions.
    *   **Acceptance:** User can reorder items; map markers are color-coded by type (attraction, restaurant, activity).
*   **Task 5.3 [INT]: Collaboration & Sharing Integration**
    *   **Action:** Build the `ShareDialog` and backend share-link generation with optional expiry.
    *   **Acceptance:** Public share links render a read-only version of the report outside the app shell.

---

**Analogy for Team Coordination:** Think of the **Backend Developer** as the architect building the hidden foundation and piping, the **Frontend Developer** as the interior designer creating the interactive rooms the user sees, and the **Integration Agent** as the building inspector who ensures the faucets work when turned on and that the structure won't collapse under a crowd.