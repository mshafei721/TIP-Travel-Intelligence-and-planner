# One-Shot Implementation Prompt for TIP

I need you to implement **TIP (Travel Intelligence & Planner)**, a complete web-based AI-powered travel intelligence platform based on detailed design specifications and UI components I'm providing.

## Instructions

Please carefully read and analyze the following files:

1. **@product-plan/product-overview.md** — Product summary with sections and data model overview
2. **@product-plan/instructions/one-shot-instructions.md** — Complete implementation instructions for all milestones

After reading these, also review:
- **@product-plan/design-system/** — Color and typography tokens
- **@product-plan/data-model/** — Entity types and relationships
- **@product-plan/shell/** — Application shell components
- **@product-plan/sections/** — All section components, types, sample data, and test instructions

## Before You Begin

Please ask me clarifying questions about:

1. **Tech Stack Preferences**
   - Frontend framework? (React/Next.js, Vue/Nuxt, Svelte/SvelteKit, etc.)
   - Backend framework? (Node.js/Express, Next.js API routes, Python/FastAPI, etc.)
   - Database? (PostgreSQL, MySQL, MongoDB, Firebase, Supabase, etc.)
   - Authentication provider? (NextAuth, Auth0, Firebase Auth, Supabase Auth, custom JWT, etc.)

2. **Deployment Target**
   - Hosting platform? (Vercel, Netlify, AWS, Google Cloud, self-hosted, etc.)
   - Environment setup? (development, staging, production)

3. **External Services**
   - AI provider for report generation? (OpenAI, Anthropic, local model, etc.)
   - Email service for notifications? (SendGrid, Mailgun, AWS SES, etc.)
   - Map provider for itinerary visualization? (Mapbox, Google Maps, OpenStreetMap, etc.)
   - File storage for uploads? (AWS S3, Cloudinary, local filesystem, etc.)

4. **Testing Approach**
   - Testing framework? (Jest, Vitest, Playwright, Cypress, etc.)
   - Test coverage expectations?

5. **User Modeling**
   - Single-tenant or multi-tenant architecture?
   - User roles and permissions needed beyond basic user?
   - Team/organization support required?

Once I answer your questions, create a comprehensive implementation plan following the milestone structure in @product-plan/instructions/one-shot-instructions.md. Use Test-Driven Development: write tests first (using the test specs in each section's tests.md), then implement features.
