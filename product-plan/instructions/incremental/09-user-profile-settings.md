# Milestone 9: User Profile & Settings

## What's Provided

This export package includes:

- **Product Overview** (`product-overview.md`) — Product description, problems solved, and planned sections
- **Design System** (`design-system/`) — Design tokens (colors, typography)
- **Data Model** (`data-model/`) — Entity descriptions, relationships, TypeScript types, sample data
- **Shell Components** (`shell/components/`) — Pre-built React components for the application shell (navigation, layout)
- **Section Components** (`sections/[section-id]/components/`) — Pre-built React components for each feature section
- **Section Types** (`sections/[section-id]/types.ts`) — TypeScript interfaces for each section
- **Section Sample Data** (`sections/[section-id]/sample-data.json`) — Example data for development/testing
- **Screenshots** (`shell/*.png`, `sections/[section-id]/*.png`) — Visual references for each screen

## What You Need to Build

This milestone implements the centralized settings page where users manage their profile, default traveler details, travel preferences, saved templates, notification settings, privacy controls, and account deletion. This is a comprehensive settings hub with auto-save functionality.

## Overview

Key functionality in this section:

- Profile information management (name, email, photo)
- Default traveler details (nationality, residency, DOB)
- Travel preferences (style, dietary restrictions, accessibility needs)
- Saved trip templates (view, create, edit, delete)
- Notification preferences (email toggles)
- Privacy controls and data deletion policy acknowledgment
- Account deletion with warning
- Auto-save with "Saved" indicators

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/user-profile-settings/components/`

Build the following components based on the provided references:

- **ProfileSettingsPage.tsx** — Main page container with all sections
- **ProfileSection.tsx** — Name, email, photo upload
- **TravelerDetailsSection.tsx** — Nationality, residency, residency status, DOB
- **TravelPreferencesSection.tsx** — Travel style, dietary restrictions, accessibility needs
- **SavedTemplatesSection.tsx** — Template cards with edit/delete actions
- **TemplateCard.tsx** — Individual template display
- **TemplateModal.tsx** — Create/edit template form
- **NotificationsSection.tsx** — Email notification toggles
- **PrivacySection.tsx** — Data deletion policy info and privacy controls
- **AccountSection.tsx** — Delete account button with warning
- **AutoSaveIndicator.tsx** — "Saved" message that appears after changes
- **ProfilePhotoUpload.tsx** — Photo upload with preview

### 2. Data Layer

**Files:** `sections/user-profile-settings/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface UserProfile {
  id: string;
  name: string;
  email: string;
  photoUrl?: string;
  authProvider: 'email' | 'google';
}

interface TravelerDetails {
  nationality: string;
  residenceCountry: string;
  residencyStatus: string;
  dateOfBirth: string;
}

interface TravelPreferences {
  travelStyle: 'relaxed' | 'balanced' | 'packed' | 'budget-focused';
  dietaryRestrictions: string[];
  accessibilityNeeds?: string;
}

interface TripTemplate {
  id: string;
  name: string;
  destinations: string[];
  datePattern: string; // e.g., "Weekend getaway", "1 week"
  preferences: TravelPreferences;
}

interface NotificationSettings {
  deletionReminders: boolean;
  reportCompletion: boolean;
  productUpdates: boolean;
}
```

### 3. Callbacks and Integration

Implement these callback props:

- `onProfileUpdate(data: Partial<UserProfile>): Promise<void>` — Update profile info with auto-save
- `onTravelerDetailsUpdate(data: TravelerDetails): Promise<void>` — Update traveler details with auto-save
- `onPreferencesUpdate(data: TravelPreferences): Promise<void>` — Update preferences with auto-save
- `onPhotoUpload(file: File): Promise<string>` — Upload photo, return URL
- `onTemplateCreate(template: TripTemplate): Promise<void>` — Create new template
- `onTemplateEdit(id: string, template: TripTemplate): Promise<void>` — Update template
- `onTemplateDelete(id: string): Promise<void>` — Delete template after confirmation
- `onNotificationToggle(setting: string, value: boolean): Promise<void>` — Update notification preference
- `onAccountDelete(): Promise<void>` — Delete account after confirmation
- `onChangePassword(): void` — Navigate to change password flow (from auth section)

### 4. Auto-Save Behavior

- Save changes automatically as user types/selects (debounced by 1-2 seconds)
- Show "Saved" indicator briefly (2-3 seconds fade) next to modified field/section
- Display loading spinner during save
- Show error message if save fails with retry option

### 5. Template Management

**Saved Templates Section:**
- Display templates as cards in grid layout
- Each card shows: template name, destination(s), date pattern, preference summary
- "Edit" and "Delete" buttons on each card
- "Create Template" button to add new template (requires active trip context or manual entry)

**Template Modal (Create/Edit):**
- Template name input
- Destination selection (can add multiple)
- Date pattern input (e.g., "Weekend", "1 week", "2 weeks")
- Travel style selector
- Dietary restrictions checkboxes
- Save/Cancel buttons

**Empty state:** "No saved templates yet. Create a trip template to speed up future trip creation."

### 6. Notification Settings

Three email notification toggles:

- **Deletion Reminders:** Email notifications before trip auto-deletion (default: ON)
- **Report Completion:** Email when travel intelligence report is ready (default: ON)
- **Product Updates:** Occasional emails about new features (default: OFF)

Each toggle includes description text explaining what it controls.

### 7. Privacy & Data Deletion

**Privacy Section displays:**
- Data deletion policy: "Your trip data is automatically deleted 7 days after your trip end date to protect your privacy."
- Link to full privacy policy (opens in new tab)
- Privacy controls (optional toggles for data usage)

### 8. Account Deletion

**Account Section:**
- "Delete Account" button with red destructive styling
- Warning text: "This action is permanent and cannot be undone. All your trips and data will be permanently deleted."
- Click opens confirmation dialog
- Dialog message: "Are you sure you want to delete your account? This will permanently delete all your trip data."
- "Cancel" and "Confirm Delete" buttons
- On confirm, account deleted and user logged out, redirected to signup page

### 9. Change Password Link

If user is authenticated via email/password (not OAuth):
- Display "Change Password" link in Profile section
- Clicking navigates to change password flow (implemented in auth section)

If user is authenticated via Google OAuth:
- Hide "Change Password" link (password managed by Google)

## Files to Reference

- `sections/user-profile-settings/spec.md` — Complete specification
- `sections/user-profile-settings/README.md` — Implementation guide
- `sections/user-profile-settings/types.ts` — TypeScript interfaces
- `sections/user-profile-settings/sample-data.json` — Example profile data
- `sections/user-profile-settings/components/` — Reference components
- `sections/user-profile-settings/*.png` — Screenshots
- `sections/user-profile-settings/tests.md` — Test instructions

## Expected User Flows

### Flow 1: User updates profile information
1. User navigates to Profile settings page
2. Page loads with all sections displayed in single scrollable view
3. User clicks on name field and changes from "John Doe" to "John Smith"
4. Auto-save triggers after 2 seconds
5. "Saved" indicator appears next to name field
6. User scrolls to email field (read-only if OAuth, shows Google icon)
7. User clicks "Change Password" link (if email/password auth)
8. Navigates to password change flow

**Expected outcome:** Profile updates save automatically without explicit "Save" button.

### Flow 2: User sets default traveler details
1. User scrolls to Traveler Details section
2. Selects nationality from dropdown: "United States"
3. Auto-save triggers, "Saved" indicator appears
4. Selects residence country: "United States"
5. Selects residency status: "Citizen"
6. Enters date of birth: "January 15, 1990"
7. Each field auto-saves as it's updated
8. "Saved" indicators appear and fade after 2-3 seconds
9. These defaults will pre-fill future trip creation forms

**Expected outcome:** Default traveler details are saved and will speed up future trip creation.

### Flow 3: User manages travel preferences
1. User scrolls to Travel Preferences section
2. Selects travel style radio button: "Balanced"
3. Auto-save triggers
4. Checks dietary restrictions: "Vegetarian", "Gluten-free"
5. Each selection auto-saves
6. Enters accessibility needs: "Wheelchair accessible accommodations preferred"
7. Auto-save triggers after typing stops
8. "Saved" indicator appears

**Expected outcome:** Preferences are saved and will customize future itinerary generation.

### Flow 4: User creates trip template
1. User scrolls to Saved Templates section
2. Clicks "Create Template" button
3. Template modal opens
4. User enters:
   - Template name: "Weekend Getaway"
   - Destinations: "San Francisco"
   - Date pattern: "3 days / 2 nights"
   - Travel style: "Relaxed"
   - Dietary restrictions: "Vegetarian"
5. Clicks "Save Template" button
6. Modal closes, new template card appears in grid
7. Success message: "Template saved successfully"

**Expected outcome:** User can reuse this template for quick trip creation.

### Flow 5: User edits and deletes template
1. User views Saved Templates section with 3 templates
2. Clicks "Edit" on "Business Trip" template
3. Template modal opens with fields pre-filled
4. User changes date pattern from "1 week" to "5 days"
5. Clicks "Save" button
6. Modal closes, template card updates
7. User clicks "Delete" on "Old Template" card
8. Confirmation dialog: "Delete this template? This action cannot be undone."
9. User confirms
10. Template card is removed from grid
11. Success message: "Template deleted"

**Expected outcome:** User maintains organized template library.

### Flow 6: User configures notifications
1. User scrolls to Notifications section
2. Sees three toggle switches:
   - Deletion Reminders: ON
   - Report Completion: ON
   - Product Updates: OFF
3. User toggles "Product Updates" to ON
4. Auto-save triggers
5. "Saved" indicator appears
6. User will now receive product update emails

**Expected outcome:** User controls which emails they receive.

### Flow 7: User reviews privacy policy
1. User scrolls to Privacy section
2. Reads data deletion policy: "Your trip data is automatically deleted 7 days after your trip end date to protect your privacy."
3. Clicks "View Full Privacy Policy" link
4. Privacy policy opens in new tab
5. User reviews policy and returns to settings page

**Expected outcome:** User understands data retention practices.

### Flow 8: User deletes account
1. User scrolls to Account section
2. Sees red "Delete Account" button with warning text
3. Clicks button
4. Confirmation dialog appears: "Are you sure you want to delete your account? This will permanently delete all your trip data. This action cannot be undone."
5. User clicks "Confirm Delete"
6. Account deletion process starts
7. User is logged out
8. Redirected to signup page
9. All user data and trips are permanently deleted

**Expected outcome:** Account is fully deleted with clear warnings at each step.

### Flow 9: User uploads profile photo
1. User clicks on profile photo upload area
2. File picker opens
3. User selects photo file (JPG, PNG)
4. Photo preview displays immediately
5. Upload starts automatically
6. Loading spinner shows during upload
7. Upload completes, "Saved" indicator appears
8. New photo displays in profile section and user menu

**Expected outcome:** Profile photo updates and displays throughout app.

## Done When

- [ ] Profile section displays name, email, and photo upload
- [ ] Email field is read-only for OAuth users with provider icon
- [ ] "Change Password" link appears only for email/password users
- [ ] Photo upload works with preview and loading state
- [ ] Traveler Details section includes nationality, residence, residency status, DOB dropdowns/pickers
- [ ] Travel Preferences section has travel style radio buttons and dietary restrictions checkboxes
- [ ] Accessibility needs textarea allows free-form input
- [ ] Auto-save triggers after user stops typing/selecting (debounced)
- [ ] "Saved" indicator appears briefly (2-3 seconds) after successful save
- [ ] Saved Templates section displays templates as cards in grid
- [ ] Template cards show name, destinations, date pattern, preferences summary
- [ ] "Create Template" button opens template modal
- [ ] Template modal includes all fields and Save/Cancel buttons
- [ ] "Edit" button on template card opens modal with pre-filled data
- [ ] "Delete" button on template card shows confirmation before deletion
- [ ] Empty state displays when no templates exist
- [ ] Notifications section has three toggle switches with descriptions
- [ ] Privacy section displays data deletion policy and link to full policy
- [ ] Account section has red "Delete Account" button with warning text
- [ ] Account deletion shows confirmation dialog before execution
- [ ] All sections use single scrollable page layout within app shell
- [ ] Loading states show during photo upload and save operations
- [ ] Error messages display if save fails with retry option
- [ ] Mobile layout uses single column with touch-friendly controls
- [ ] Light and dark mode styles work across all sections
- [ ] Tests cover profile updates, traveler details, preferences, templates, notifications, and account deletion
- [ ] Visual appearance matches screenshots in section directory
