 - Trip creation is likely broken due to frontend payload shape mismatching backend schemas.
  - Several report sections rely on mock data or placeholders, conflicting with “official sources only” requirements.                                                                                                           
  - Agent execution has placeholders and non‑real‑time data sources (flight, advisories).
  - Auto‑deletion and privacy settings are not fully wired to backend logic.                                                                                                                                                    
  - Celery task tests explicitly mark missing validation/integration coverage.                                                                                                                                                  
                                                                                                                                                                                                                                
  Findings                                                                                                                                                                                                                      
  | ID | Severity | Category | Area | File:Line | Evidence | Impact | Suggested fix |                                                                                                                                           
  |---|---|---|---|---|---|---|---|                                                                                                                                                                                             
  | F-01 | Critical | Wrong implementation | Trip creation | frontend/components/trip-wizard/TripCreationWizard.tsx:253 frontend/components/trip-wizard/TripCreationWizard.tsx:258 frontend/components/trip-wizard/             
  TripCreationWizard.tsx:274 backend/app/models/trips.py:59 backend/app/models/trips.py:129 | Frontend posts camelCase fields (residencyCountry, originCity, budgetCurrency, tripPurposes) while backend expects snake_case     
  (residence_country, origin_city, currency, trip_purpose). | Trip creation via backend /api/trips likely 422s or drops critical data. | Align API contract: add Pydantic aliases or transform payload; update frontend to      
  snake_case. |                                                                                                                                                                                                                 
  | F-02 | High | Missing item | Trip inputs | docs/PRD.md:173 docs/PRD.md:176 docs/PRD.md:180 docs/PRD.md:184 backend/app/models/trips.py:59 | PRD requires residency status, origin country, and traveler age categories, but 
  trip models only include nationality/residence country and party ages. | Required intake data cannot be captured/stored for agents. | Add fields to trip models + DB + UI; clarify age categories vs numeric ages. |
  | F-03 | Medium | Gap | Validation | docs/PRD.md:208 backend/app/models/trips.py:129 | Backend validates return date > departure but does not enforce “future dates”. | Past trips can be created when frontend validation is 
  bypassed. | Add server‑side validator for future dates. |                                                                                                                                                                     
  | F-04 | High | Missing implementation | Agent jobs | backend/app/tasks/agent_jobs.py:162 | Generic agent job task is TODO and returns placeholder status/data. | Async job pipeline can’t produce real report sections. |    
  Implement agent execution or disable endpoint/queue until ready. |                                                                                                                                                            
  | F-05 | High | Wrong implementation | Destination report | frontend/app/(app)/trips/[id]/destination/page.tsx:41 frontend/app/(app)/trips/[id]/destination/page.tsx:45 | Page explicitly merges mock data for weather,       
  currency, culture, food, laws, safety, news. | Users see sample data for major report sections. | Fetch real sections or hide sections until data exists. |                                                                   
  | F-06 | High | Wrong implementation | Visa report | frontend/app/(app)/trips/[id]/page.tsx:27 frontend/app/(app)/trips/[id]/page.tsx:87 frontend/app/(app)/trips/[id]/page.tsx:89 docs/PRD.md:244 | Visa page falls back to  
  mock data and includes third‑party source “Schengen Visa Info”. | Conflicts with “official sources only” requirement. | Remove third‑party sources from visa UI and gate mock data to dev only. |                             
  | F-07 | Medium | Missing item | Visa advisories | backend/app/agents/visa/tools.py:187 backend/app/agents/visa/tools.py:190 | Travel advisory tool is a placeholder with TODO. | No official advisory data; incomplete visa  
  intelligence. | Integrate official advisory API and surface attribution. |                                                                                                                                                    
  | F-08 | High | Gap | Flight intelligence | backend/app/agents/flight/agent.py:54 docs/PRD.md:461 | Flight agent uses AI knowledge base, not real‑time flight data. | Does not meet “real‑time flight price discovery”        
  requirement. | Integrate live flight pricing API or downgrade feature scope. |                                                                                                                                                
  | F-09 | High | Wrong implementation | Visa fallback | backend/app/agents/visa/agent.py:280 backend/app/agents/visa/agent.py:294 docs/PRD.md:264 | Fallback infers visa_required from text and uses internal sources. |       
en frontend validation is
  bypassed. | Add server‑side validator for future dates. |
  | F-04 | High | Missing implementation | Agent jobs | backend/app/tasks/agent_jobs.py:162 | Generic agent job task is TODO and returns placeholder status/data. | Async job pipeline can’t produce real report sections. |
  Implement agent execution or disable endpoint/queue until ready. |
  | F-05 | High | Wrong implementation | Destination report | frontend/app/(app)/trips/[id]/destination/page.tsx:41 frontend/app/(app)/trips/[id]/destination/page.tsx:45 | Page explicitly merges mock data for weather,
  currency, culture, food, laws, safety, news. | Users see sample data for major report sections. | Fetch real sections or hide sections until data exists. |
  | F-06 | High | Wrong implementation | Visa report | frontend/app/(app)/trips/[id]/page.tsx:27 frontend/app/(app)/trips/[id]/page.tsx:87 frontend/app/(app)/trips/[id]/page.tsx:89 docs/PRD.md:244 | Visa page falls back to
  mock data and includes third‑party source “Schengen Visa Info”. | Conflicts with “official sources only” requirement. | Remove third‑party sources from visa UI and gate mock data to dev only. |   
  | F-07 | Medium | Missing item | Visa advisories | backend/app/agents/visa/tools.py:187 backend/app/agents/visa/tools.py:190 | Travel advisory tool is a placeholder with TODO. | No official advisory data; incomplete visa
  intelligence. | Integrate official advisory API and surface attribution. |
  | F-08 | High | Gap | Flight intelligence | backend/app/agents/flight/agent.py:54 docs/PRD.md:461 | Flight agent uses AI knowledge base, not real‑time flight data. | Does not meet “real‑time flight price discovery”
  requirement. | Integrate live flight pricing API or downgrade feature scope. |
  | F-09 | High | Wrong implementation | Visa fallback | backend/app/agents/visa/agent.py:280 backend/app/agents/visa/agent.py:294 docs/PRD.md:264 | Fallback infers visa_required from text and uses internal sources. |
  Violates “no assumptions” policy; potential compliance risk. | On parse failure, mark data incomplete and avoid inferences. |
  | F-10 | Medium | Missing item | Privacy controls | frontend/app/(app)/profile/page.tsx:82 frontend/app/(app)/profile/page.tsx:83 | Privacy flags are TODO with no backend support. | GDPR/privacy acknowledgements not
  persisted. | Add backend fields + API + DB for privacy flags. |
  | F-11 | High | Gap | Auto‑deletion | backend/app/api/trips.py:304 backend/app/tasks/cleanup.py:317 docs/PRD.md:517 | Trips are created without auto_delete_at, and deletion scheduling exists but is not invoked. |
  Auto‑deletion policy is not enforced. | Set auto_delete_at on creation and schedule deletion. |
  | F-12 | Medium | Test gap | Celery tasks | backend/tests/test_celery_tasks.py:94 backend/tests/test_celery_tasks.py:158 backend/tests/test_celery_tasks.py:202 | Tests explicitly mark validation/integration as failing or
  skipped. | Missing coverage for task validation, retries, timeouts, integration. | Implement validations and unskip integration tests once Redis available. |
  | F-13 | Low | Documentation gap | Onboarding | README.md:115 README.md:164 | README references missing root PRD.md and notes missing Unix init script. | Broken links and incomplete setup guidance. | Fix README link to
  docs/PRD.md; add init.sh or remove TODO. |

  Test and QA Gaps

  - Celery task validation/integration tests are explicitly marked as failing or skipped in backend/tests/test_celery_tasks.py:94, backend/tests/test_celery_tasks.py:158, backend/tests/test_celery_tasks.py:202.

  - Broken PRD link and missing Unix init script in README.md:115, README.md:164.

  Assumptions and Questions

  - Should the backend accept camelCase trip payloads from the wizard, or should the wizard be updated to snake_case?
  - Do you want to capture residency status and origin country at trip creation (as per PRD), or rely on profile data?
  - Should mock data be strictly dev‑only, or can it appear in production with explicit “sample data” labeling?

    User Flows                                                                                                                                                                                          
                                                                                                                                                                                                      
  Legend: [OK]=wired, [PARTIAL]=mixed/mocks, [BROKEN]=contract/schema mismatch                                                                                                                        
                                                                                                                                                                                                      
  Auth                                                                                                                                                                                                
  Login/Signup UI -> Supabase Auth -> session/JWT -> middleware gate -> app routes [OK]                                                                                                               
                                                                                                                                                                                                      
  Trips                                                                                                                                                                                               
  Trip Wizard -> POST Railway /api/trips -> Supabase trips [BROKEN]                                                                                                                                   
  Trip Wizard -> Next.js /api/trips -> Supabase trips [OK but unused]                                                                                                                                 
  Trips Page -> Supabase client -> trips table [OK]                                                                                                                                                   
  Dashboard -> Railway /api/trips -> Supabase trips [PARTIAL]                                                                                                                                         
                                                                                                                                                                                                      
  Reports                                                                                                                                                                                             
  Generate Page -> POST /api/trips/{id}/generate -> Celery orchestrator -> report_sections [PARTIAL]                                                                                                  
  Trip Report (visa) -> Supabase trip read + /report/visa [PARTIAL]
  Trip Report (destination) -> /report/destination + mock sections [PARTIAL]                                                                                                                          
  Itinerary -> /report/itinerary + /report/flight + fallback sample [PARTIAL]                                                                                                                         
                                                                                                                                                                                                      
  History / Analytics / Settings / Templates / Profile                                                                                                                                                
  History -> /api/history* [BROKEN]                                                                                                                                                                   
  Analytics -> /api/analytics* [BROKEN]                                                                                                                                                               
  Settings -> /api/settings* [OK]                                                                                                                                                                     
  Templates -> /api/templates* [PARTIAL]                                                                                                                                                              
  Profile -> /api/profile + /api/templates [BROKEN]                                                                                                                                                   
                                                                                                                                                                                                      
  Backend Logic                                                                                                                                                                                       
                                                                                                                                                                                                      
  Client (Vercel) -> FastAPI (Railway)                                                                                                                                                                
    -> verify_jwt_token (SUPABASE_JWT_SECRET)                                                                                                                                                         
    -> Supabase service-role client                                                                                                                                                                   
    -> trips / agent_jobs / report_sections tables                                                                                                                                                    
    -> Celery (Redis) -> Orchestrator -> agents -> upsert report_sections                                                                                                                             
    -> /report/* endpoints read report_sections -> PDF/export/share                                                                                                                                   
                                                                                                                                                                                                      
  Breakpoints: report_sections.section_type enum mismatch; trips table missing columns used by history/versioning; request/response shapes differ from frontend expectations.                         
                                                                                                                                                                                                      
  Breakpoints & Misalignments (core)                                                                                                                                                                  
                                                                                                                                                                                                      
  - Trip create payload doesn’t match backend model (residencyCountry vs residence_country, budgetCurrency vs currency, companionAges vs party_ages, tripPurposes array vs trip_purpose), so POST /   
    api/trips will 422 or drop fields: frontend/components/trip-wizard/TripCreationWizard.tsx, backend/app/models/trips.py, backend/app/api/trips.py.                                                 
  - Trip update + versioning UI expects {trip, version, recalculation} and full version snapshots, but backend PUT /trips/{id} returns TripResponse only and /versions returns summaries: frontend/   
    lib/api/trips.ts, frontend/app/(app)/trips/[id]/overview/page.tsx, backend/app/api/trips.py.                                                                                                      
  - Change preview + recalculation contracts diverge (frontend sends sections, expects impact object; backend expects agents, returns affected_agents/requires_recalculation): frontend/lib/api/      
    trips.ts, frontend/components/trip-update, backend/app/models/trips.py, backend/app/api/trips.py.                                                                                                 
  - Generation status fields don’t line up (agents_completed/agents_failed vs completed_agents/pending_agents), so progress UI can’t render real status: frontend/lib/api/reports.ts, frontend/       
    components/reports/TripGenerationProgress.tsx, backend/app/api/trips.py.
  - Report section types conflict (country stored by agents vs enum destination in schema/OpenAPI), likely breaking inserts/queries if enum enforced: backend/app/tasks/agent_jobs.py, db/schema.sql, 
    contracts/openapi.yaml.                                                                                                                                                                           
  - Profile page expects templates response shape {templates: []}, backend returns a list directly, so profile templates fail to load: frontend/app/(app)/profile/page.tsx, backend/app/api/          
    templates.py.                                                                                                                                                                                     
                                                                                                                                                                                                      
  Schema/Type Drift (DB vs API vs Frontend)                                                                                                                                                           
                                                                                                                                                                                                      
  - trips columns used by backend/history/ratings/versioning aren’t in repo schema (e.g., is_archived, archived_at, user_rating, user_notes, version, recalc_task_id, template_id, idempotency_key):  
    db/schema.sql, db/migrations, backend/app/api/history.py, backend/app/api/trips.py, frontend/types/database.ts.                                                                                   
  - trip_templates fields expected by UI/API (tags, is_public, use_count, currency, typical_duration, estimated_budget) are missing from schema: db/schema.sql, backend/app/api/templates.py,         
    frontend/types/profile.ts.                                                                                                                                                                        
  - Analytics response shape mismatch (budget_analysis vs avg_budget/budget_ranges, seasonal_trends vs seasonal_distribution): frontend/types/analytics.ts, backend/app/models/analytics.py, backend/ 
    app/api/analytics.py.                                                                                                                                                                             
  - OpenAPI contract is camelCase and uses PATCH while backend uses snake_case and PUT; frontend follows OpenAPI more than backend: contracts/openapi.yaml, backend/app/api/trips.py, backend/app/    
    models/trips.py.                                                                                                                                                                                  
                                                                                                                                                                                                      
  Supabase / Railway / Vercel Gap                                                                                                                                                                     
                                                                                                                                                                                                      
  - Three data paths exist: browser -> Supabase (direct), Vercel API routes -> Supabase, Vercel -> Railway -> Supabase; they write/read different JSON shapes and bypass consistent validation:       
    frontend/app/(app)/trips/page.tsx, frontend/app/api/trips/route.ts, frontend/lib/api/client.ts, backend/app/core/supabase.py.                                                                     
  - Backend assumes service-role access and JWT secret validation; frontend assumes RLS and direct reads, so data constraints differ between paths: backend/app/core/auth.py, backend/app/core/       
    supabase.py, frontend/lib/supabase/client.ts.                                                                                                                                                     
  - Docs still mention Render in places despite Railway/Vercel being current, increasing config drift risk: README.md, DEPLOYMENT.md, SSOT.md.                                                        
                                                                                                                                                                                                      
  If you want fixes, I’d recommend:                                                                                                                                                                   
                                                                                                                                                                                                      
  1. Pick a single canonical contract (OpenAPI or backend Pydantic), then update both frontend and backend to match it (including JSON casing and endpoint shapes).                                   
  2. Normalize data access to one path (either all via Railway API or all via Supabase with RLS), and remove the other two to stop shape drift.                                                       
  3. Update DB migrations to add the missing columns/enum values and regenerate frontend/types/database.ts from Supabase.  