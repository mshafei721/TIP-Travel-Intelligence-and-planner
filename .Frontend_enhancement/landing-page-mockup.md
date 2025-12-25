# Landing Page Mockup - B2B Support AI (Single-Column)

This mockup applies `.Frontend_enhancement/visual-style-guide.md` to `.Frontend_enhancement/landing-page-content-b2b-support.md`. It is structured for a clean, single-column flow with mobile-first readability.

---

## Global Layout and Style
Layout:
- Desktop grid: 12 columns, 72px margins, 24px gutters. Max container width 1200px.
- Tablet: 8 columns, 48px margins, 20px gutters.
- Mobile: 4 columns, 20px margins, 16px gutters.
- Text block width: 640 to 720px max for long paragraphs.
- Section spacing: 96px top/bottom desktop, 64px mobile.

Typography:
- Typeface: Manrope (fallback: system-ui, Segoe UI, Arial, sans-serif).
- H1: 48/56, 700, letter-spacing -0.5px, color `#0C1B2A`.
- H2: 36/44, 700, letter-spacing -0.3px, color `#0C1B2A`.
- H3: 28/36, 600, letter-spacing -0.2px, color `#0C1B2A`.
- Subhead: 20/30, 500, color `#2C4A64`.
- Body: 16/26, 400, color `#101828`.
- Small: 14/22, 400, color `#475467`.

Color usage:
- Primary CTA: Signal Teal `#00B3A4` with white text.
- Secondary accents: Slate Blue `#2C4A64` and Mist `#F6F8FB`.
- Borders/dividers: Fog `#E6ECF2`.

Buttons:
- Primary: background `#00B3A4`, text `#FFFFFF`, radius 10px, padding 14px 22px (desktop), 12px 18px (mobile), font 16px/600.
- Hover: `#009686`. Active: `#007C70`. Focus ring: 2px `#7FE5DC` with 2px offset.
- Secondary: transparent, 1px border `#00B3A4`, text `#00B3A4`, hover bg `#E6FBF9`.

Cards:
- Background `#FFFFFF`, border 1px `#E6ECF2`, radius 12px, padding 24px.
- Shadow: 0 6px 18px rgba(12, 27, 42, 0.08).

Icons:
- Line icons, 1.5 to 2px stroke, rounded ends, size 24 to 32px.
- Color: Slate Blue `#2C4A64` or Signal Teal `#00B3A4` for emphasis.

---

## 1. Hero Section (Above the Fold)
Background: White.
Layout (desktop):
- Two-column within the 12-col grid: text on left (7 columns), visual on right (5 columns).
- Mobile: single-column stack, text first, visual second.

Hierarchy and spacing:
- Section padding: 96px top/bottom desktop, 64px mobile.
- H1 to subhead: 12 to 16px.
- Subhead to bullets: 24px.
- Bullets to CTA: 24px.
- CTA to trust signal: 12px.

Text content (left column):
- H1 (48/56, 700):
  Stop Drowning in Support Tickets. Delays Cost Renewals. Meet [Product].
- Subhead paragraph (20/30, 500):
  You can resolve most questions instantly, even after hours. [Company]'s [Product] uses your trusted knowledge base to deliver accurate, cited answers, so your team can focus on high-impact issues.
- Key benefit bullets (16/26, 400), each with 24px icon:
  - Icon: Clock (Slate Blue). Resolve ~60% of inquiries instantly, 24/7. [cite: 598]
  - Icon: Shield/Checkmark (Slate Blue). Deliver accurate answers with citations from your content.
  - Icon: Puzzle piece or platform logo (Slate Blue). Activate inside your existing system. No code required.

CTA block:
- Primary button (left aligned): Request Your Personalized Demo.
- Secondary text link below (Signal Teal): See [Product] in Action.
- Subtle trust signal in small text (14/22, Steel `#475467`) directly below CTA:
  Join 1,000+ B2B teams using [Product] to reduce ticket volume and response time.

Visual (right column):
- 15 to 30 second looping GIF or video thumbnail of [Product] resolving a ticket.
- Frame style: white card with 12px radius and soft shadow (0 8px 24px rgba(12, 27, 42, 0.12)).
- Include a visible callout tag inside the UI, such as "Resolved in 12 sec" in a badge (background `#E6FBF9`, text `#007C70`).

---

## 2. Problem / Agitation Section
Background: Mist `#F6F8FB` to create rhythm.
Layout:
- Single-column text centered within max width 720px.

Hierarchy and spacing:
- 96px vertical padding desktop, 64px mobile.
- H2 to body: 16px.

Text content:
- H2: Is Your Support Team Overwhelmed by Repetitive Questions?
- Body (16/26):
  You are dealing with a growing ticket queue, slow responses after hours, and inconsistent answers across channels. Costs rise, CSAT slips, and your best agents burn out answering the same questions. Meanwhile, disconnected tools force your team to jump between systems just to respond.

Visual notes:
- Optional single supporting icon (line icon of stacked tickets) aligned left of the headline on desktop, above on mobile.

---

## 3. Solution / Benefits Section ("How [Product] Transforms Your Support")
Background: White.
Layout:
- Single-column intro text.
- Followed by a 2-column grid of feature cards on desktop (6 columns each).
- Mobile: stack cards in one column.

Hierarchy and spacing:
- Section padding: 96px desktop, 64px mobile.
- H2 to intro: 16px.
- Intro to card grid: 32px.
- Card spacing: 24px gaps.

Text content:
- H2: How [Product] Transforms Your Support
- Intro (Subhead 20/30):
  [Product] eliminates the bottlenecks by automating the repetitive, so your team can focus on complex and high-value conversations.

Cards (each card includes 28px icon, H3, body text):
1) 24/7 Automated Support
   - Feature: AI answers instantly.
   - Benefit: Improve CSAT with immediate responses, anytime. Scale globally without adding headcount.
2) Quick Setup with Existing Content
   - Feature: Uses your KB and docs.
   - Benefit: Go live in minutes, not months. Leverage the knowledge you already trust, no coding needed.
3) Trusted, Cited Answers
   - Feature: Answers from approved content with sources.
   - Benefit: Build customer trust with accurate, verifiable information and consistent brand voice.
4) Seamless Handoff to Humans
   - Feature: Escalates complex issues.
   - Benefit: Route edge cases to experts fast with full context, while AI handles the routine.
5) CRM Integration and Personalization
   - Feature: Native CRM connection.
   - Benefit: Deliver personalized support based on customer history, all in one platform.
6) Analytics and Reporting
   - Feature: Performance insights.
   - Benefit: Understand what customers ask, identify gaps, and continuously improve.

Visual:
- Place a clean dashboard screenshot below the cards on desktop or between rows, aligned center.
- Use 12px radius and soft shadow.

---

## 4. Social Proof and Trust ("Trusted by Leading B2B Teams")
Background: Mist `#F6F8FB`.
Layout:
- Single-column for headline.
- Logo strip row.
- Testimonial card.
- Badge row and security note.

Hierarchy and spacing:
- H2 to logo strip: 24px.
- Logos to testimonial: 32px.
- Testimonial to badges: 24px.

Text content:
- H2: Trusted by Leading B2B Teams

Logo strip:
- 4 to 8 grayscale logos, consistent height 28 to 32px.
- Use `#475467` tint for uniform look.

Testimonial card:
- Quote (Body 16/26):
  "[Product] automated 55% of our tier-1 inquiries and freed up 10+ hours per agent each week."
- Attribution (Small 14/22):
  Jordan Lee, VP Customer Support, AtlasHQ
- Optional 48px headshot on left.

Badges:
- Row of 2 to 3 badges (SOC 2 Type II, GDPR, ISO 27001) in small chips.

Security assurance (Small text):
Data encrypted in transit and at rest. Role-based access and audit logs available.

---

## 5. Differentiation Section ("Why [Product]?")
Background: White.
Layout:
- Single-column text with a simple icon row beneath.

Hierarchy and spacing:
- H2 to body: 16px.
- Body to icon row: 24px.

Text content:
- H2: More Than Just a Chatbot: Fully Integrated AI Support
- Body (16/26):
  [Product] is built into your workflow, not bolted on. Set it up without code, manage it in minutes, and trust every answer because it is grounded in your approved content with citations.

Icon row:
- Three icons with captions: Native Integration, No-Code Setup, Cited Answers.
- Use Slate Blue icons and small labels in Steel.

---

## 6. FAQ Section
Background: Mist `#F6F8FB`.
Layout:
- Single-column with accordion list.

Hierarchy and spacing:
- H2 to accordion: 24px.
- Accordion items: 16px vertical spacing.

Text content:
- H2: Have Questions? We've Got Answers.

Accordion items (question in 16/26, 600; answer in 16/26, 400):
1) How quickly can I set up [Product]?
   - Most teams are live in under an hour with existing content.
2) What content sources does [Product] use?
   - Your knowledge base, help docs, and approved internal content.
3) How does [Product] ensure answers are accurate and on-brand?
   - Responses are grounded in your sources with citations and guardrails.
4) What happens if [Product] can't answer a question?
   - It escalates to a human with full context and conversation history.
5) Is my customer data secure when using [Product]?
   - Yes. Data is encrypted, access is controlled, and retention is configurable.
6) Does [Product] require technical expertise to manage?
   - No. Non-technical teams can launch and update it with simple workflows.

---

## 7. Final Call-to-Action (CTA) Section
Background: White.
Layout:
- Centered text block with CTA button.

Hierarchy and spacing:
- H2 to CTA: 24px.
- CTA to secondary link: 12px.

Text content:
- H2: Ready to cut ticket volume and deliver instant, trusted answers?

CTA:
- Primary button centered: Request Your Personalized Demo
- Secondary text link below: Or Watch a 2-Minute Overview Video

Trust note (optional small text):
- Small line under CTA: No credit card required. Response in 1 business day.

---

## 8. Footer (Minimal)
Background: Mist `#F6F8FB`.
Layout:
- Single row, left aligned on desktop, stacked on mobile.

Content:
- Small text: (c) 2025 [Company]. All rights reserved.
- Links: Privacy Policy | Terms of Service (Signal Teal, underline on hover).

Spacing:
- 32px top/bottom padding.

Note:
- No main navigation in footer.
