TIP – Travel Intelligence \& Planner

Product Requirements Document (PRD v1)

1\. Product Overview



Product Name

TIP – Travel Intelligence \& Planner



Product Type

Web-based AI-powered travel intelligence and itinerary planning platform.



Mission

Provide travelers with a single, accurate, legally compliant, and actionable travel intelligence report tailored to their nationality, residency, budget, and travel dates.



Non-goals



Not a booking platform



Not a social travel app



Not a content or inspiration blog



TIP is a decision-grade travel intelligence system.



2\. Target Users



International leisure travelers



Business travelers



Families planning multi-city trips



Digital nomads and frequent travelers



Secondary future users:



Corporate travel managers



Relocation consultants



3\. Core User Journey



User signs up or logs in



User creates a trip



System validates inputs



Multi-agent pipeline executes



Interactive report is generated



User views report



User exports PDF



System auto-deletes data after trip completion



4\. Functional Requirements

4.1 Authentication \& User Accounts



Email and password authentication



Google OAuth sign-in



Password reset flow



Session persistence



Secure logout



Account deletion option



4.2 Trip Creation



Required inputs:



Destination country



One or multiple cities



Travel start and end dates



Budget (total)



Nationality



Country of residence & status


Origin country



Residency status

Age

number of travlers

age of travelers (child, adult)

Optional inputs:



Travel style



Pace preference



Food preferences



Validation rules:



Dates must be future dates



Passport assumed valid unless stated otherwise



Budget must be numeric and positive



4.3 Visa \& Entry Intelligence (Critical)



Visa requirement determination



Visa type classification



Allowed stay duration



Transit visa requirements



Entry conditions



Official government or embassy links only



Confidence indicator



Explicit disclaimer



Failure handling:



If data is incomplete, system must say so explicitly



No assumptions allowed



4.4 Country Intelligence



Country flag



Political system summary



Population and demographics



Religion overview



Safety and stability notes



Interactive country map


latest news & updates

4.5 Weather Intelligence



Weather forecast for trip dates



Historical averages



Temperature ranges



Rain probability



Climate warnings



4.6 Currency \& Budget Intelligence



Origin currency to destination currency conversion



Destination currency to USD conversion



Live exchange rates



Estimated daily cost



Budget utilization indicator



Overspend risk warnings



4.7 Culture, Laws \& Traditions



Cultural etiquette



Religious norms



Special or unusual laws



Prohibited behaviors



High-risk violations flagged clearly



4.8 Food \& Culinary Intelligence



National dish



National drink



Local specialties



Food safety notes



Restaurant recommendations



Clickable map links



4.9 Attractions \& Experiences



Top attractions per city



Categorization by interest



Estimated visit duration



Entry cost ranges



Crowd indicators



Map navigation links



4.10 Smart Itinerary Builder



Day-by-day itinerary



Weather-aware scheduling



Logical city sequencing



Budget alignment



Adjustable pace



Editable blocks



4.11 Flight Intelligence



Real-time flight price discovery



Direct and transit comparisons



Airline reliability notes



Booking links to aggregators



Price range visualization



4.12 Interactive Report



Web-based report



Section-based navigation



Expandable cards



Clickable links



Maps embedded



Tooltips for warnings



PDF export



4.13 Data Lifecycle Management



All trip data auto-deleted after trip end date



User notified of deletion policy



Manual delete option



System-enforced cleanup jobs



5\. Non-Functional Requirements



High accuracy for visa data



Explicit source attribution



Async processing for report generation



Partial results viewable during generation



GDPR-compliant data handling



Rate-limited scraping



Clear error states



6\. Multi-Agent Architecture

Agent Roles



Visa \& Entry Agent



Country Intelligence Agent



Weather Agent



Currency \& Budget Agent



Culture \& Law Agent



Food Agent



Attractions Agent



Itinerary Agent



Flight Agent



Orchestrator Agent



Rules:



Agents run in parallel where possible



Orchestrator validates outputs



Conflicts resolved centrally



Sources mandatory for critical data



7\. Tech Stack (Locked)

Frontend



Next.js (TypeScript)



Tailwind CSS



shadcn/ui



Mapbox (see [DR-002](docs/decisions/DR-002-map-provider.md))



Backend



Python FastAPI



REST APIs



Async task handling



Authentication \& Database



Supabase Auth (email/password + Google)



Supabase Postgres



Row-level security



Background Jobs



Redis + Celery



Job states persisted in DB



AI \& Agents



CrewAI for orchestration



Reuse agent patterns from open-source repositories



Central Orchestrator Agent for quality control



Scraping \& Data Acquisition



Official APIs first



Firecrawl for structured scraping



Secondary scraping APIs as fallback



Vendor abstraction layer



PDF Generation



Server-side HTML to PDF rendering



Stored temporarily then deleted



Hosting



Vercel for frontend



Cloud VM for backend and workers



Managed Redis



8\. Data Model (High Level)



Entities:



User



Trip



AgentJob



ReportSection



SourceReference



DeletionSchedule



All entities scoped to user and auto-expiring.



9\. Risks \& Mitigations

Risk	Mitigation

Visa misinformation	Official sources only

Scraping blocks	Multi-vendor fallback

Long generation time	Async jobs + partial rendering

Cost overruns	Auto-deletion + quotas

User trust	Explicit confidence indicators

10\. Success Metrics



Report generation success rate



Visa data completeness



Time to first usable result



PDF export rate



User retention before auto-deletion

---

## 11. User Stories

This section maps core user journeys to functional requirements and success metrics. Each story follows the format: **As a [user type], I want [goal], so that [benefit]**.

### US-001: Account Management
**As a** traveler
**I want** to create and manage my account with email/password or Google OAuth
**So that** I can securely access my travel reports

**Journey Mapping:** Core Journey Step 1 (Sign up or log in)
**Requirements:** REQ-4.1 (Authentication & User Accounts)
**Success Metrics:** User retention before auto-deletion
**Priority:** Critical

**Functional Requirements Covered:**
- Email and password authentication
- Google OAuth sign-in
- Password reset flow
- Session persistence
- Secure logout
- Account deletion option

**Evidence:** PRD.md:117-142

---

### US-002: Trip Input & Creation
**As a** traveler
**I want** to input my trip details (destination, dates, budget, nationality, etc.)
**So that** I receive a personalized travel intelligence report

**Journey Mapping:** Core Journey Step 2 (Create a trip)
**Requirements:** REQ-4.2 (Trip Creation)
**Success Metrics:** Report generation success rate
**Priority:** Critical

**Functional Requirements Covered:**
- Destination country input
- One or multiple cities
- Travel start and end dates
- Budget (total)
- Nationality
- Country of residence & residency status
- Origin country
- Age, number of travelers, traveler ages
- Optional: Travel style, pace, food preferences

**Evidence:** PRD.md:145-203

---

### US-003: Input Validation & Error Handling
**As a** traveler
**I want** the system to validate my inputs and show clear error messages
**So that** I don't submit invalid trip data

**Journey Mapping:** Core Journey Step 3 (System validates inputs)
**Requirements:** REQ-4.2-VAL (Validation rules), REQ-5.7 (Clear error states)
**Success Metrics:** Report generation success rate
**Priority:** High

**Functional Requirements Covered:**
- Dates must be future dates
- Passport assumed valid unless stated
- Budget must be numeric and positive
- Clear error states for all validation failures

**Evidence:** PRD.md:204-217, PRD.md:561

---

### US-004: Visa & Entry Intelligence (CRITICAL)
**As a** traveler
**I want** accurate, legally compliant visa requirements with official sources
**So that** I know exactly what documents I need for entry

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.3 (Visa & Entry Intelligence)
**Success Metrics:** Visa data completeness, Report generation success rate
**Priority:** Critical

**Functional Requirements Covered:**
- Visa requirement determination
- Visa type classification (visa-free, eVisa, visa on arrival, visa required)
- Allowed stay duration
- Transit visa requirements
- Entry conditions
- Official government or embassy links only
- Confidence indicator (0-100)
- Explicit disclaimer
- No assumptions for incomplete data

**Risks:** Visa misinformation (mitigated by official sources only)

**Evidence:** PRD.md:220-267

---

### US-005: Country Intelligence
**As a** traveler
**I want** key country information (flag, politics, demographics, safety, news)
**So that** I understand the destination's current situation

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.4 (Country Intelligence)
**Success Metrics:** Report generation success rate
**Priority:** High

**Functional Requirements Covered:**
- Country flag
- Political system summary
- Population and demographics
- Religion overview
- Safety and stability notes
- Interactive country map
- Latest news & updates

**Evidence:** PRD.md:268-296

---

### US-006: Weather Intelligence
**As a** traveler
**I want** accurate weather forecasts and historical averages for my trip dates
**So that** I can pack appropriately and plan activities

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.5 (Weather Intelligence)
**Success Metrics:** Report generation success rate
**Priority:** High

**Functional Requirements Covered:**
- Weather forecast for trip dates
- Historical averages
- Temperature ranges
- Rain probability
- Climate warnings

**Evidence:** PRD.md:297-318

---

### US-007: Currency & Budget Intelligence
**As a** traveler
**I want** live exchange rates, daily cost estimates, and budget analysis
**So that** I can manage my travel finances effectively

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.6 (Currency & Budget Intelligence)
**Success Metrics:** Report generation success rate
**Priority:** High

**Functional Requirements Covered:**
- Origin to destination currency conversion
- Destination to USD conversion
- Live exchange rates
- Estimated daily cost
- Budget utilization indicator
- Overspend risk warnings

**Evidence:** PRD.md:321-346

---

### US-008: Cultural & Legal Intelligence
**As a** traveler
**I want** information on cultural etiquette, religious norms, and unusual laws
**So that** I avoid cultural offense and legal violations

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.7 (Culture, Laws & Traditions)
**Success Metrics:** Report generation success rate
**Priority:** High

**Functional Requirements Covered:**
- Cultural etiquette
- Religious norms
- Special or unusual laws
- Prohibited behaviors
- High-risk violations flagged clearly

**Evidence:** PRD.md:349-370

---

### US-009: Food & Culinary Intelligence
**As a** traveler
**I want** information on national dishes, drinks, local specialties, and restaurant recommendations
**So that** I can experience authentic local cuisine

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.8 (Food & Culinary Intelligence)
**Success Metrics:** Report generation success rate
**Priority:** Medium

**Functional Requirements Covered:**
- National dish
- National drink
- Local specialties
- Food safety notes
- Restaurant recommendations
- Clickable map links

**Evidence:** PRD.md:373-398

---

### US-010: Attractions & Experiences Intelligence
**As a** traveler
**I want** top attractions with visit duration, entry costs, and crowd indicators
**So that** I can plan my sightseeing efficiently

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.9 (Attractions & Experiences)
**Success Metrics:** Report generation success rate
**Priority:** High

**Functional Requirements Covered:**
- Top attractions per city
- Categorization by interest (museums, nature, etc.)
- Estimated visit duration
- Entry cost ranges
- Crowd indicators
- Map navigation links

**Evidence:** PRD.md:401-426

---

### US-011: Smart Itinerary Generation
**As a** traveler
**I want** a day-by-day itinerary that is weather-aware, budget-aligned, and editable
**So that** I have a practical, personalized travel plan

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.10 (Smart Itinerary Builder)
**Success Metrics:** Report generation success rate, Time to first usable result
**Priority:** Critical

**Functional Requirements Covered:**
- Day-by-day itinerary
- Weather-aware scheduling (indoor/outdoor based on forecast)
- Logical city sequencing
- Budget alignment
- Adjustable pace (relaxed, moderate, packed)
- Editable blocks (user can modify)

**Dependencies:** Requires US-004 through US-010 (all agents) to complete first

**Evidence:** PRD.md:429-456

---

### US-012: Flight Intelligence
**As a** traveler
**I want** real-time flight prices, direct vs transit comparisons, and booking links
**So that** I can find the best flight options

**Journey Mapping:** Core Journey Step 4 (Multi-agent pipeline executes)
**Requirements:** REQ-4.11 (Flight Intelligence)
**Success Metrics:** Report generation success rate
**Priority:** High

**Functional Requirements Covered:**
- Real-time flight price discovery
- Direct and transit comparisons
- Airline reliability notes
- Booking links to aggregators
- Price range visualization

**Evidence:** PRD.md:457-479

---

### US-013: Interactive Report Display
**As a** traveler
**I want** an interactive web-based report with navigation, maps, tooltips, and expandable sections
**So that** I can easily consume and explore my travel intelligence

**Journey Mapping:** Core Journey Step 5 (View report)
**Requirements:** REQ-4.12 (Interactive Report)
**Success Metrics:** Time to first usable result, PDF export rate
**Priority:** High

**Functional Requirements Covered:**
- Web-based report
- Section-based navigation
- Expandable cards
- Clickable links
- Maps embedded (Mapbox - see DR-002)
- Tooltips for warnings
- Partial results viewable during generation (async rendering)

**Evidence:** PRD.md:481-507, PRD.md:549

---

### US-014: PDF Export
**As a** traveler
**I want** to export my report as a PDF
**So that** I can save it offline and access it during my trip

**Journey Mapping:** Core Journey Step 6 (Export PDF)
**Requirements:** REQ-4.12-PDF (PDF export)
**Success Metrics:** PDF export rate
**Priority:** High

**Functional Requirements Covered:**
- Server-side HTML to PDF rendering
- PDF optimized for print
- Temporary storage (deleted after download)

**Evidence:** PRD.md:509, PRD.md:733-741

---

### US-015: Data Lifecycle Management
**As a** traveler
**I want** my trip data to be automatically deleted after my trip ends
**So that** my data privacy is protected

**Journey Mapping:** Core Journey Step 7 (System auto-deletes data)
**Requirements:** REQ-4.13 (Data Lifecycle Management)
**Success Metrics:** User retention before auto-deletion
**Priority:** Critical (GDPR compliance)

**Functional Requirements Covered:**
- All trip data auto-deleted after trip end date
- User notified of deletion policy
- Manual delete option available
- System-enforced cleanup jobs

**Evidence:** PRD.md:513-530

---

### US-016: System Quality & Non-Functional Requirements
**As a** system administrator
**I want** high accuracy, explicit source attribution, async processing, and GDPR compliance
**So that** the system is trustworthy, performant, and legally compliant

**Journey Mapping:** All steps (cross-cutting concerns)
**Requirements:** REQ-5 (Non-Functional Requirements)
**Success Metrics:** Visa data completeness, Report generation success rate, Time to first usable result
**Priority:** Critical

**Functional Requirements Covered:**
- High accuracy for visa data (>95%)
- Explicit source attribution (all critical data)
- Async processing for report generation
- Partial results viewable during generation
- GDPR-compliant data handling
- Rate-limited scraping (prevent blocks)
- Clear error states

**Evidence:** PRD.md:533-562

---

**Total User Stories:** 16
**Coverage:** All 7 Core Journey Steps, All Functional Requirements (4.1-4.13), All NFRs (Section 5)

---

## 12. Acceptance Criteria

This section defines testable, measurable acceptance criteria for each User Story using the Given-When-Then format. All criteria must pass before a story is considered complete.

### AC-001: Account Management (US-001)

**AC-001-1: Email/Password Signup**
- **Given:** User is on the signup page
- **When:** User enters valid email and password (min 8 chars, 1 uppercase, 1 number)
- **Then:** Account is created and user is redirected to dashboard within 2 seconds
- **Test Method:** E2E automated test

**AC-001-2: Google OAuth Signup**
- **Given:** User is on the signup page
- **When:** User clicks "Sign in with Google" and authorizes
- **Then:** Account is created using Google profile and user is redirected to dashboard
- **Test Method:** E2E automated test

**AC-001-3: Password Reset Flow**
- **Given:** User forgot password
- **When:** User enters registered email and clicks "Reset Password"
- **Then:** Password reset email is sent within 30 seconds containing a secure link
- **Test Method:** Integration test (check email queue)

**AC-001-4: Session Persistence**
- **Given:** User is logged in
- **When:** User closes browser and reopens within 7 days
- **Then:** User is still logged in (session persists)
- **Test Method:** E2E automated test

**AC-001-5: Secure Logout**
- **Given:** User is logged in
- **When:** User clicks "Logout"
- **Then:** Session is terminated and user is redirected to login page
- **Test Method:** E2E automated test

**AC-001-6: Account Deletion**
- **Given:** User is logged in
- **When:** User requests account deletion and confirms
- **Then:** All user data (account, trips, reports) is permanently deleted within 24 hours
- **Test Method:** Integration test (verify database records deleted)

---

### AC-002: Trip Input & Creation (US-002)

**AC-002-1: Required Fields Validation**
- **Given:** User is on trip creation form
- **When:** User submits form with missing required fields
- **Then:** Form shows clear error messages for each missing field
- **Test Method:** Unit test (form validation)

**AC-002-2: Destination Country Input**
- **Given:** User is on trip creation form
- **When:** User selects a destination country from dropdown
- **Then:** Country is selected and form shows city input
- **Test Method:** E2E automated test

**AC-002-3: Multiple Cities Input**
- **Given:** User has selected a country
- **When:** User enters multiple cities (comma-separated or multi-select)
- **Then:** All cities are saved to trip data
- **Test Method:** Integration test

**AC-002-4: Date Selection**
- **Given:** User is on trip creation form
- **When:** User selects start and end dates using date picker
- **Then:** Dates are validated as future dates and trip duration is calculated
- **Test Method:** Unit test (date validation)

**AC-002-5: Budget Input**
- **Given:** User is on trip creation form
- **When:** User enters total budget amount
- **Then:** Budget is validated as numeric and positive
- **Test Method:** Unit test (budget validation)

**AC-002-6: Nationality and Residency Input**
- **Given:** User is on trip creation form
- **When:** User selects nationality, residence country, and residency status
- **Then:** All fields are saved and used for visa determination
- **Test Method:** Integration test

**AC-002-7: Traveler Details Input**
- **Given:** User is on trip creation form
- **When:** User enters number of travelers and age categories (child/adult)
- **Then:** Traveler details are saved and used for budget calculations
- **Test Method:** Integration test

**AC-002-8: Optional Fields**
- **Given:** User is on trip creation form
- **When:** User optionally selects travel style, pace, food preferences
- **Then:** Optional fields are saved and used for personalization
- **Test Method:** Integration test

**AC-002-9: Successful Trip Creation**
- **Given:** User has filled all required fields with valid data
- **When:** User clicks "Generate Report"
- **Then:** Trip is created, multi-agent pipeline is triggered, and user sees progress page
- **Test Method:** E2E automated test

---

### AC-003: Input Validation & Error Handling (US-003)

**AC-003-1: Future Date Validation**
- **Given:** User is entering trip dates
- **When:** User selects a past or current date
- **Then:** Form shows error: "Travel dates must be in the future"
- **Test Method:** Unit test (date validation)

**AC-003-2: Budget Numeric Validation**
- **Given:** User is entering budget
- **When:** User enters non-numeric or negative value
- **Then:** Form shows error: "Budget must be a positive number"
- **Test Method:** Unit test (budget validation)

**AC-003-3: Clear Error States**
- **Given:** Any validation fails
- **When:** Error occurs
- **Then:** Error message is displayed inline with the field, in red, with clear guidance
- **Test Method:** E2E automated test

**AC-003-4: Passport Validity Assumption**
- **Given:** User creates a trip
- **When:** User does not explicitly state passport invalidity
- **Then:** System assumes passport is valid (no validation error)
- **Test Method:** Integration test

---

### AC-004: Visa & Entry Intelligence (US-004) - CRITICAL

**AC-004-1: Visa Requirement Determination**
- **Given:** User has specified nationality, residence, and destination
- **When:** Visa agent executes
- **Then:** Visa requirement is determined with >95% accuracy (against official sources)
- **Test Method:** Integration test (compare against known visa requirements)

**AC-004-2: Visa Type Classification**
- **Given:** Visa agent has determined requirement
- **When:** Classification is performed
- **Then:** Visa type is one of: visa-free, eVisa, visa on arrival, visa required
- **Test Method:** Unit test (classification logic)

**AC-004-3: Allowed Stay Duration**
- **Given:** Visa requirement is visa-free or visa on arrival
- **When:** Visa agent retrieves stay duration
- **Then:** Allowed stay duration (in days) is displayed
- **Test Method:** Integration test

**AC-004-4: Transit Visa Requirements**
- **Given:** User's itinerary includes transit stops
- **When:** Visa agent analyzes transit countries
- **Then:** Transit visa requirements are determined and displayed
- **Test Method:** Integration test

**AC-004-5: Official Sources Only**
- **Given:** Visa data is retrieved
- **When:** Sources are validated
- **Then:** 100% of sources are official government or embassy websites
- **Test Method:** Automated test (URL validation against whitelist)

**AC-004-6: Confidence Indicator**
- **Given:** Visa agent completes execution
- **When:** Confidence score is calculated
- **Then:** Confidence score (0-100) is displayed alongside visa data
- **Test Method:** Unit test (confidence scoring)

**AC-004-7: Explicit Disclaimer**
- **Given:** Visa data is displayed
- **When:** User views visa section
- **Then:** Explicit disclaimer is shown: "Verify with official embassy sources. TIP is not liable for visa errors."
- **Test Method:** E2E automated test (check disclaimer presence)

**AC-004-8: Incomplete Data Handling**
- **Given:** Visa data is incomplete or unavailable
- **When:** Visa agent cannot retrieve full data
- **Then:** Report explicitly states "Incomplete data - verify with embassy" with no assumptions
- **Test Method:** Integration test (mock incomplete API response)

---

### AC-005: Country Intelligence (US-005)

**AC-005-1: Country Flag Display**
- **Given:** Country agent executes
- **When:** Country data is retrieved
- **Then:** Country flag image is displayed (SVG or PNG, min 100x60px)
- **Test Method:** E2E automated test

**AC-005-2: Political System Summary**
- **Given:** Country agent retrieves data
- **When:** Political system is extracted
- **Then:** Political system is displayed in 1-2 sentences
- **Test Method:** Integration test

**AC-005-3: Demographics Display**
- **Given:** Country agent retrieves data
- **When:** Demographics are extracted
- **Then:** Population and major demographics are displayed
- **Test Method:** Integration test

**AC-005-4: Religion Overview**
- **Given:** Country agent retrieves data
- **When:** Religion data is extracted
- **Then:** Major religions and percentages are displayed
- **Test Method:** Integration test

**AC-005-5: Safety and Stability Notes**
- **Given:** Country agent analyzes safety data
- **When:** Safety rating is calculated
- **Then:** Safety rating (High/Medium/Low) and stability notes are displayed
- **Test Method:** Integration test

**AC-005-6: Interactive Country Map**
- **Given:** Country data is complete
- **When:** User views country section
- **Then:** Interactive Mapbox map is embedded showing country borders
- **Test Method:** E2E automated test

**AC-005-7: Latest News**
- **Given:** Country agent scrapes news
- **When:** News data is retrieved
- **Then:** Top 3-5 latest news headlines with links are displayed
- **Test Method:** Integration test

---

### AC-006: Weather Intelligence (US-006)

**AC-006-1: Weather Forecast Display**
- **Given:** Weather agent executes for trip dates
- **When:** Forecast is retrieved
- **Then:** 15-day forecast (or full trip duration) is displayed with daily high/low temps
- **Test Method:** Integration test (mock weather API)

**AC-006-2: Historical Averages**
- **Given:** Weather agent retrieves historical data
- **When:** Averages are calculated
- **Then:** Historical average temps for trip dates are displayed alongside forecast
- **Test Method:** Integration test

**AC-006-3: Temperature Ranges**
- **Given:** Forecast is retrieved
- **When:** Temperature data is parsed
- **Then:** Daily temperature ranges (min-max) are displayed in Celsius and Fahrenheit
- **Test Method:** Unit test (temperature parsing)

**AC-006-4: Rain Probability**
- **Given:** Forecast includes precipitation data
- **When:** Rain probability is extracted
- **Then:** Daily rain probability (%) is displayed
- **Test Method:** Integration test

**AC-006-5: Climate Warnings**
- **Given:** Extreme weather is detected (>40°C or <-10°C or >80% rain)
- **When:** Weather agent analyzes data
- **Then:** Climate warnings are prominently displayed with icons
- **Test Method:** Unit test (warning detection logic)

---

### AC-007: Currency & Budget Intelligence (US-007)

**AC-007-1: Live Exchange Rates**
- **Given:** Currency agent executes
- **When:** Exchange rates are fetched
- **Then:** Live rates (updated within 60 seconds) are displayed with timestamp
- **Test Method:** Integration test (mock currency API)

**AC-007-2: Origin to Destination Conversion**
- **Given:** User has specified origin currency and destination currency
- **When:** Currency agent calculates conversion
- **Then:** Conversion rate and total budget in destination currency are displayed
- **Test Method:** Unit test (conversion calculation)

**AC-007-3: Destination to USD Conversion**
- **Given:** Destination currency is not USD
- **When:** Currency agent calculates USD conversion
- **Then:** Budget is also shown in USD for reference
- **Test Method:** Unit test (conversion calculation)

**AC-007-4: Estimated Daily Cost**
- **Given:** Budget and trip duration are known
- **When:** Currency agent estimates daily cost
- **Then:** Estimated daily cost in destination currency is displayed
- **Test Method:** Unit test (daily cost calculation)

**AC-007-5: Budget Utilization Indicator**
- **Given:** Itinerary and costs are estimated
- **When:** Budget analysis is performed
- **Then:** Budget utilization percentage (e.g., "75% of budget allocated") is displayed
- **Test Method:** Integration test

**AC-007-6: Overspend Risk Warnings**
- **Given:** Budget utilization >90%
- **When:** Budget analysis detects overspend risk
- **Then:** Warning is displayed: "Risk of exceeding budget"
- **Test Method:** Unit test (risk detection)

---

### AC-008: Cultural & Legal Intelligence (US-008)

**AC-008-1: Cultural Etiquette Display**
- **Given:** Culture agent scrapes etiquette data
- **When:** Etiquette is extracted
- **Then:** Top 5-10 cultural etiquette rules are displayed as bullet points
- **Test Method:** Integration test

**AC-008-2: Religious Norms Display**
- **Given:** Culture agent retrieves religious norms
- **When:** Norms are extracted
- **Then:** Key religious practices and restrictions are displayed
- **Test Method:** Integration test

**AC-008-3: Unusual Laws Display**
- **Given:** Culture agent scrapes unusual laws
- **When:** Laws are extracted
- **Then:** Top 5-10 unusual or strict laws are displayed with sources
- **Test Method:** Integration test

**AC-008-4: Prohibited Behaviors Display**
- **Given:** Culture agent identifies prohibitions
- **When:** Prohibitions are extracted
- **Then:** Prohibited behaviors are displayed prominently
- **Test Method:** Integration test

**AC-008-5: High-Risk Violations Flagged**
- **Given:** High-risk violations are detected (e.g., death penalty, imprisonment)
- **When:** Culture agent analyzes risk
- **Then:** High-risk violations are flagged in RED with warning icons
- **Test Method:** E2E automated test (check for red flag UI)

---

### AC-009: Food & Culinary Intelligence (US-009)

**AC-009-1: National Dish Display**
- **Given:** Food agent retrieves culinary data
- **When:** National dish is extracted
- **Then:** National dish name and description are displayed
- **Test Method:** Integration test

**AC-009-2: National Drink Display**
- **Given:** Food agent retrieves culinary data
- **When:** National drink is extracted
- **Then:** National drink name and description are displayed
- **Test Method:** Integration test

**AC-009-3: Local Specialties Display**
- **Given:** Food agent retrieves local specialties
- **When:** Specialties are extracted
- **Then:** Top 5 local specialties are displayed with descriptions
- **Test Method:** Integration test

**AC-009-4: Food Safety Notes**
- **Given:** Food agent analyzes safety data
- **When:** Safety notes are extracted
- **Then:** Food safety warnings (e.g., "Avoid tap water") are displayed
- **Test Method:** Integration test

**AC-009-5: Restaurant Recommendations**
- **Given:** Food agent retrieves restaurant data from Maps API
- **When:** Restaurants are ranked
- **Then:** Top 5-10 restaurants are displayed with ratings and addresses
- **Test Method:** Integration test (mock Maps API)

**AC-009-6: Clickable Map Links**
- **Given:** Restaurants are displayed
- **When:** User views restaurant list
- **Then:** Each restaurant has a clickable Mapbox link to open in maps
- **Test Method:** E2E automated test (check link presence)

---

### AC-010: Attractions & Experiences Intelligence (US-010)

**AC-010-1: Top Attractions Display**
- **Given:** Attractions agent retrieves data
- **When:** Attractions are ranked
- **Then:** Top 10 attractions per city are displayed with names and descriptions
- **Test Method:** Integration test

**AC-010-2: Attraction Categorization**
- **Given:** Attractions are retrieved
- **When:** Categories are assigned
- **Then:** Attractions are categorized (Museums, Nature, Historical, Entertainment, etc.)
- **Test Method:** Unit test (categorization logic)

**AC-010-3: Estimated Visit Duration**
- **Given:** Attractions are displayed
- **When:** Visit duration is estimated
- **Then:** Estimated time to visit (e.g., "2-3 hours") is shown for each attraction
- **Test Method:** Integration test

**AC-010-4: Entry Cost Display**
- **Given:** Attractions have pricing data
- **When:** Costs are retrieved
- **Then:** Entry cost ranges (e.g., "$10-20") are displayed
- **Test Method:** Integration test

**AC-010-5: Crowd Indicators**
- **Given:** Crowd data is available
- **When:** Crowd levels are analyzed
- **Then:** Crowd indicators (e.g., "Peak: 10am-2pm") are displayed
- **Test Method:** Integration test

**AC-010-6: Map Navigation Links**
- **Given:** Attractions are displayed
- **When:** User views attraction list
- **Then:** Each attraction has a clickable Mapbox link to navigate
- **Test Method:** E2E automated test

---

### AC-011: Smart Itinerary Generation (US-011) - CRITICAL

**AC-011-1: Day-by-Day Itinerary**
- **Given:** All agents have completed execution
- **When:** Itinerary agent generates schedule
- **Then:** Itinerary shows day-by-day breakdown with activities, times, and locations
- **Test Method:** Integration test

**AC-011-2: Weather-Aware Scheduling**
- **Given:** Weather forecast shows rain on Day 3
- **When:** Itinerary agent schedules activities
- **Then:** Indoor activities are scheduled for Day 3, outdoor for sunny days
- **Test Method:** Integration test (mock weather data)

**AC-011-3: Logical City Sequencing**
- **Given:** Trip includes multiple cities
- **When:** Itinerary agent sequences cities
- **Then:** Cities are ordered logically (geographic proximity, no backtracking)
- **Test Method:** Unit test (sequencing algorithm)

**AC-011-4: Budget Alignment**
- **Given:** User has specified a budget
- **When:** Itinerary agent allocates costs
- **Then:** Total itinerary cost does not exceed budget (or shows warning if over)
- **Test Method:** Integration test

**AC-011-5: Adjustable Pace**
- **Given:** User has selected a pace (relaxed, moderate, packed)
- **When:** Itinerary agent generates schedule
- **Then:** Itinerary density matches pace (e.g., 2 activities for relaxed, 5 for packed)
- **Test Method:** Integration test

**AC-011-6: Editable Blocks**
- **Given:** Itinerary is displayed
- **When:** User clicks "Edit" on an activity block
- **Then:** User can reorder, remove, or replace activity and changes are saved
- **Test Method:** E2E automated test

**AC-011-7: Dependency Completion**
- **Given:** Itinerary agent starts execution
- **When:** Dependencies are checked
- **Then:** All required agents (Visa, Country, Weather, Currency, Culture, Food, Attractions, Flight) have completed
- **Test Method:** Unit test (dependency validation)

---

### AC-012: Flight Intelligence (US-012)

**AC-012-1: Real-Time Flight Price Discovery**
- **Given:** Flight agent executes
- **When:** Prices are fetched from API
- **Then:** Live flight prices (updated within last 24 hours) are displayed
- **Test Method:** Integration test (mock flight API)

**AC-012-2: Direct vs Transit Comparisons**
- **Given:** Multiple flight options exist
- **When:** Flight agent retrieves data
- **Then:** Both direct and transit (connecting) flights are displayed with price comparison
- **Test Method:** Integration test

**AC-012-3: Airline Reliability Notes**
- **Given:** Flight data includes airline ratings
- **When:** Reliability is assessed
- **Then:** Airline reliability notes (e.g., "High on-time rating") are displayed
- **Test Method:** Integration test

**AC-012-4: Booking Links**
- **Given:** Flights are displayed
- **When:** User views flight options
- **Then:** Each flight has a clickable link to aggregator (Skyscanner, Google Flights)
- **Test Method:** E2E automated test

**AC-012-5: Price Range Visualization**
- **Given:** Multiple flights are available
- **When:** Prices are visualized
- **Then:** Price range chart (e.g., bar chart or line graph) is displayed
- **Test Method:** E2E automated test

---

### AC-013: Interactive Report Display (US-013)

**AC-013-1: Web-Based Report**
- **Given:** Report generation is complete
- **When:** User accesses report
- **Then:** Report is rendered as a web page (not PDF) with responsive design
- **Test Method:** E2E automated test

**AC-013-2: Section-Based Navigation**
- **Given:** Report has multiple sections
- **When:** User views report
- **Then:** Sidebar or top navigation allows jumping to sections (Visa, Weather, etc.)
- **Test Method:** E2E automated test

**AC-013-3: Expandable Cards**
- **Given:** Report sections are displayed
- **When:** User clicks on a section header
- **Then:** Section content expands/collapses
- **Test Method:** E2E automated test

**AC-013-4: Clickable Links**
- **Given:** Report contains external links (sources, booking, maps)
- **When:** User clicks a link
- **Then:** Link opens in new tab
- **Test Method:** E2E automated test

**AC-013-5: Embedded Maps**
- **Given:** Report includes location data
- **When:** User views locations
- **Then:** Mapbox maps are embedded showing attractions, restaurants, etc.
- **Test Method:** E2E automated test

**AC-013-6: Tooltips for Warnings**
- **Given:** Report contains warnings or critical info
- **When:** User hovers over warning icon
- **Then:** Tooltip displays detailed warning text
- **Test Method:** E2E automated test

**AC-013-7: Partial Results Rendering**
- **Given:** Agents are still executing
- **When:** User views report during generation
- **Then:** Completed sections are displayed, pending sections show "Loading..." spinner
- **Test Method:** E2E automated test (simulate slow agent)

---

### AC-014: PDF Export (US-014)

**AC-014-1: PDF Generation**
- **Given:** User clicks "Export PDF"
- **When:** PDF is generated server-side
- **Then:** PDF file is created within 30 seconds and download starts automatically
- **Test Method:** Integration test

**AC-014-2: PDF Content Completeness**
- **Given:** PDF is generated
- **When:** PDF is opened
- **Then:** All report sections are included in PDF with correct formatting
- **Test Method:** Automated test (PDF content validation)

**AC-014-3: PDF Print Optimization**
- **Given:** PDF is generated
- **When:** User prints PDF
- **Then:** PDF is optimized for print (page breaks, margins, readable fonts)
- **Test Method:** Manual test

**AC-014-4: Temporary Storage**
- **Given:** PDF is generated
- **When:** User downloads PDF
- **Then:** PDF is deleted from server within 1 hour
- **Test Method:** Automated test (check file deletion)

---

### AC-015: Data Lifecycle Management (US-015) - CRITICAL

**AC-015-1: Auto-Deletion Schedule**
- **Given:** Trip end date has passed
- **When:** Cleanup job runs (daily cron)
- **Then:** Trip data is deleted 7 days after trip end date
- **Test Method:** Integration test (mock trip end date)

**AC-015-2: Deletion Notification**
- **Given:** Trip data will be deleted in 3 days
- **When:** Notification system runs
- **Then:** User receives email notification: "Your trip data will be deleted in 3 days"
- **Test Method:** Integration test (check email queue)

**AC-015-3: Manual Delete Option**
- **Given:** User wants to delete trip early
- **When:** User clicks "Delete Trip" and confirms
- **Then:** Trip data is deleted immediately (within 1 minute)
- **Test Method:** E2E automated test

**AC-015-4: Deletion Policy Visibility**
- **Given:** User creates a trip
- **When:** User views trip details
- **Then:** Deletion policy is clearly displayed: "Data will be deleted 7 days after trip end"
- **Test Method:** E2E automated test

**AC-015-5: System-Enforced Cleanup**
- **Given:** Cleanup job is scheduled (daily at 2am UTC)
- **When:** Job runs
- **Then:** All expired trip data is deleted and audit log is created
- **Test Method:** Integration test (cron job execution)

---

### AC-016: System Quality & Non-Functional Requirements (US-016) - CRITICAL

**AC-016-1: Visa Data Accuracy**
- **Given:** Visa agent has executed for 100 test cases
- **When:** Accuracy is measured against official sources
- **Then:** Accuracy is >95%
- **Test Method:** Automated test (compare against known visa data)

**AC-016-2: Source Attribution**
- **Given:** Critical data is displayed (visa, laws, safety)
- **When:** User views data
- **Then:** Every critical data point has a visible source link
- **Test Method:** Automated test (check source links presence)

**AC-016-3: Async Processing**
- **Given:** User submits trip creation
- **When:** Backend processes request
- **Then:** Request is queued asynchronously and user sees progress page (not blocking)
- **Test Method:** Integration test

**AC-016-4: Partial Results Rendering**
- **Given:** Report generation is in progress
- **When:** User accesses report
- **Then:** Completed sections are visible, pending sections show "Loading..."
- **Test Method:** E2E automated test

**AC-016-5: GDPR Compliance**
- **Given:** System stores user data
- **When:** GDPR audit is performed
- **Then:** All requirements are met: consent, data portability, right to deletion, encryption
- **Test Method:** Manual audit + automated checks

**AC-016-6: Rate-Limited Scraping**
- **Given:** Scraping agents execute
- **When:** Scraping requests are made
- **Then:** Rate limits are respected (max 1 request per 2 seconds per domain)
- **Test Method:** Integration test (monitor request timing)

**AC-016-7: Clear Error States**
- **Given:** Any error occurs (API failure, scraping failure, etc.)
- **When:** Error is detected
- **Then:** User sees clear error message with guidance (not technical stack trace)
- **Test Method:** E2E automated test (trigger errors)

---

**Total Acceptance Criteria:** 77
**Coverage:** All 16 User Stories
**Testability:** All criteria are measurable with specific test methods (E2E, Integration, Unit, Manual)
