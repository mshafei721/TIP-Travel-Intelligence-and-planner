# DR-002: Map Provider

**Decision ID:** DR-002
**Title:** Map Provider for Embedded Maps and Location Services
**Status:** ✅ **Accepted**
**Date:** 2025-12-22 (Session 1)
**Owner:** TIP Team
**Due Date:** N/A (Decision already made)

---

## Context

The TIP platform requires map functionality for:
- **Interactive country maps** (embedded in reports)
- **Restaurant and attraction locations** (clickable map links)
- **Navigation links** (deep links to map apps)
- **Offline capabilities** (for travelers without internet)
- **Customization** (travel-specific styling and layers)

The map provider must support:
- High-volume usage (potentially millions of map loads)
- Embedded map widgets in web reports
- Marker clustering for multiple locations
- Custom styling for travel use case
- Reasonable pricing at scale

---

## Decision

**Selected Provider:** **Mapbox**

**Pricing Plan:**
- **MVP (Phases 1-11):** Free Tier (50,000 loads/month)
- **Production (Phase 12+):** Pay-as-you-go
  - $0.50 per 1,000 loads after free tier
  - Estimated: $25-50/month (100K-200K loads)

**Use Cases:**
- Embedded country maps in reports (Mapbox GL JS)
- Restaurant/attraction markers with clustering
- Clickable navigation links (Mapbox URLs)
- Custom travel-themed map styles

---

## Options Considered

### Option 1: Mapbox (SELECTED)
**Pros:**
- ✅ Better pricing for high volume ($0.50/1K loads vs Google's $7/1K loads)
- ✅ Offline map capabilities (critical for travelers)
- ✅ Better customization (custom styles, layers, data overlays)
- ✅ Travel-focused use case (adventure, navigation themes)
- ✅ Vector maps (faster loading, smoother zoom)
- ✅ Free tier: 50,000 loads/month (generous for MVP)
- ✅ No per-user tracking (better privacy)
- ✅ Open-source friendly (Mapbox GL JS)

**Cons:**
- ❌ Smaller ecosystem than Google Maps
- ❌ Less familiar to users (Google Maps is default)
- ❌ Fewer POI details compared to Google Maps

**Cost Estimate:**
- MVP: $0/month (within free tier)
- Production: $25-50/month (100K-200K loads)
- High Scale: $250/month (1M loads)

### Option 2: Google Maps
**Pros:**
- ✅ Most familiar to users
- ✅ Largest ecosystem and POI database
- ✅ Street View integration
- ✅ Extensive documentation

**Cons:**
- ❌ Expensive at scale ($7/1K map loads after free tier)
- ❌ No offline capabilities
- ❌ Limited customization (fixed Google styling)
- ❌ Complex pricing structure (multiple products)
- ❌ Requires Google Cloud Platform account
- ❌ Privacy concerns (user tracking)

**Cost Estimate:**
- MVP: $0/month (within free $200 credit)
- Production: $350-700/month (100K-200K loads)
- High Scale: $3,500/month (1M loads) 🚨

### Option 3: OpenStreetMap (OSM)
**Pros:**
- ✅ Completely free and open-source
- ✅ No vendor lock-in
- ✅ Community-driven data

**Cons:**
- ❌ Requires self-hosting (infrastructure costs)
- ❌ Manual tile server setup
- ❌ No official support
- ❌ Less polished than commercial providers
- ❌ Potential performance issues at scale

**Cost Estimate:**
- MVP: ~$10/month (tile server hosting)
- Production: ~$50/month (dedicated server)

---

## Decision Criteria

| Criterion | Weight | Mapbox | Google Maps | OpenStreetMap |
|-----------|--------|--------|-------------|---------------|
| Pricing (High Volume) | Critical | ✅ Low | ❌ High | ✅ Free* |
| Offline Capabilities | High | ✅ Yes | ❌ No | ✅ Yes** |
| Customization | High | ✅ Excellent | ❌ Limited | ✅ Full |
| Travel Use Case Fit | High | ✅ Excellent | ⚠️ Good | ⚠️ Good |
| POI Data Quality | Medium | ✅ Good | ✅ Excellent | ⚠️ Variable |
| Developer Experience | Medium | ✅ Excellent | ✅ Excellent | ⚠️ Complex |
| Free Tier for MVP | Medium | ✅ 50K/month | ✅ $200 credit | ✅ Unlimited* |

*Requires self-hosting infrastructure
**Requires manual tile download

**Winner:** Mapbox (best balance of cost, features, and travel fit)

---

## Analysis

### Why Mapbox Wins:

1. **Pricing at Scale (Critical):**
   - Mapbox: $0.50/1K loads = $250 for 500K loads
   - Google Maps: $7/1K loads = $3,500 for 500K loads
   - **Cost Savings:** 93% cheaper at 500K+ loads

2. **Offline Capabilities:**
   - Mapbox supports offline maps (travelers can download tiles)
   - Google Maps requires constant internet connection
   - Critical for users in remote areas or with limited data

3. **Customization for Travel:**
   - Mapbox allows custom map styles (e.g., highlight tourist attractions)
   - Can add custom data layers (visa difficulty heatmaps, safety zones)
   - Google Maps has fixed styling (limited to light/dark themes)

4. **Privacy:**
   - Mapbox doesn't require user tracking or cookies
   - Google Maps tracks user behavior for advertising
   - Better for GDPR compliance

5. **Developer Experience:**
   - Mapbox GL JS is modern, lightweight, and well-documented
   - Easy integration with React (react-map-gl library)
   - Vector maps provide smoother interactions than raster tiles

### Why Not Google Maps:

- **Cost Prohibitive:** $3,500/month for 1M loads is 14x more expensive than Mapbox
- **No Offline Support:** Dealbreaker for travelers in remote areas
- **Limited Customization:** Can't create travel-specific map styles

### Why Not OpenStreetMap:

- **Infrastructure Complexity:** Requires tile server setup, monitoring, and scaling
- **Support Risk:** No official support channel for critical issues
- **Development Time:** Building OSM infrastructure would delay MVP by 2-4 weeks

---

## Consequences

### Positive:
- ✅ Significant cost savings at scale (93% cheaper than Google Maps)
- ✅ Offline maps enable better user experience for travelers
- ✅ Custom styling aligns with travel-focused brand
- ✅ Generous free tier (50K loads/month) enables extensive MVP testing
- ✅ Better privacy compliance (no user tracking)

### Negative:
- ⚠️ Less POI data than Google Maps (may need to supplement with additional APIs)
- ⚠️ Users may be less familiar with Mapbox (Google Maps is default)
- ⚠️ Smaller ecosystem (fewer third-party integrations)

### Mitigation:
- **POI Data:** Use Google Places API or TripAdvisor API for POI details (keep Mapbox for visualization)
- **User Familiarity:** Mapbox UI is intuitive and similar enough to Google Maps
- **Ecosystem:** Mapbox has mature React, Vue, and Angular libraries

---

## Implementation Notes

**Phase 1 (MVP Setup):**
1. Create Mapbox account
2. Get Mapbox Access Token (public key)
3. Install `react-map-gl` library in Next.js frontend
4. Configure map component for country maps
5. Add marker clustering for restaurants/attractions
6. Test offline map downloads

**Phase 9 (Attractions) and Phase 8 (Food):**
1. Integrate Mapbox with restaurant/attraction data
2. Implement clickable markers with info popups
3. Generate Mapbox deep links for navigation
4. Add custom map styles (travel theme)

**Phase 13 (Report Generation):**
1. Embed Mapbox maps in interactive reports
2. Optimize map rendering for PDF export
3. Implement marker clustering for multiple locations

**Future Enhancements:**
- Custom travel-themed map styles (Phase 15)
- Visa difficulty heatmap overlay (Phase 15)
- Safety zone highlighting (Phase 15)

---

## References

- **Research Sources:**
  - [Mapbox vs Google Maps pricing comparison (2025)](https://www.mapbox.com/pricing)
  - [Mapbox offline maps documentation](https://docs.mapbox.com/help/tutorials/offline-maps/)
  - [Google Maps Pricing](https://mapsplatform.google.com/pricing/)
  - [Travel app use cases - Mapbox](https://www.mapbox.com/solutions/travel)

- **Internal Documentation:**
  - claude-progress.txt:Session 1:46-50 (Map provider decision)
  - docs/services_config.md:201-220 (Map provider configuration)
  - PRD.md:649 (Tech stack - Maps section)

- **Related Decisions:**
  - DR-001: Backend Hosting (Render)

---

**Approved By:** TIP Team
**Effective Date:** 2025-12-22
**Review Date:** Phase 9 (Attractions Agent implementation)

