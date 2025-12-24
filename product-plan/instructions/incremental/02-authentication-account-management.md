# Milestone 2: Authentication & Account Management

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

This milestone implements the complete authentication system with separate pages for login, signup, password reset, and email verification. The authentication layer is the gateway to the entire application and must be secure, user-friendly, and reliable.

## Overview

Key functionality in this section:

- User signup with email/password and Google OAuth (primary method)
- Login with session management and rate limiting
- Password reset flow with email verification
- Account deletion with data cleanup
- Change password functionality
- Real-time password strength validation
- Session expiry warnings and extension
- Mobile-responsive standalone auth pages (no app shell)

## Recommended Approach: Test-Driven Development

Before writing implementation code, write tests for each component and feature. This ensures:

- Your code meets the requirements from the start
- You have confidence when refactoring
- Edge cases and error states are handled
- The UI behaves correctly across different states

Refer to the `tests.md` file in this section's directory for detailed test instructions.

## What to Implement

### 1. Core Components

**Files:** `sections/authentication-account-management/components/`

Build the following components based on the provided references:

- **LoginForm.tsx** — Email/password login with Google OAuth button at top
- **SignupForm.tsx** — User registration with real-time validation and auto-login
- **PasswordResetRequestForm.tsx** — Email input to request password reset
- **PasswordResetForm.tsx** — New password entry with strength validation
- **EmailVerificationPage.tsx** — Success page after email verification
- **SessionExpiryWarning.tsx** — Banner warning about session expiry
- **AccountDeletionDialog.tsx** — Confirmation dialog for account deletion
- **ChangePasswordForm.tsx** — Current password + new password fields

### 2. Data Layer

**Files:** `sections/authentication-account-management/types.ts`

Use the TypeScript interfaces provided:

```typescript
interface User {
  id: string;
  email: string;
  name: string;
  authProvider: 'email' | 'google';
  emailVerified: boolean;
  createdAt: string;
}

interface AuthSession {
  userId: string;
  token: string;
  expiresAt: string;
}

interface PasswordStrength {
  score: 'weak' | 'medium' | 'strong';
  feedback: string[];
}
```

### 3. Callbacks and Integration

Implement these callback props for each component:

- `onLogin(email: string, password: string): Promise<void>`
- `onGoogleLogin(): Promise<void>`
- `onSignup(email: string, password: string, name: string): Promise<void>`
- `onPasswordResetRequest(email: string): Promise<void>`
- `onPasswordReset(token: string, newPassword: string): Promise<void>`
- `onAccountDelete(): Promise<void>`
- `onChangePassword(currentPassword: string, newPassword: string): Promise<void>`
- `onExtendSession(): Promise<void>`

### 4. Empty States and Error Handling

- **Rate limit lockout:** Display "Too many failed attempts. Try again in 15 minutes or reset your password."
- **Invalid credentials:** Display "Incorrect email or password. Please try again."
- **Email not verified:** Display "Please verify your email address. Check your inbox for a verification link."
- **Session expired:** Redirect to login with message "Your session has expired. Please log in again."
- **Network errors:** Display "Unable to connect. Please check your internet connection and try again."

### 5. Validation Rules

Implement real-time password strength validation:

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 number
- At least 1 special character

Display validation feedback as user types:
- Red border and error message for invalid fields
- Green checkmark for valid fields
- Password strength indicator (weak/medium/strong) with color coding

### 6. Page Routes

Create standalone pages (without app shell) at these routes:

- `/login` — LoginForm
- `/signup` — SignupForm
- `/forgot-password` — PasswordResetRequestForm
- `/reset-password?token=...` — PasswordResetForm
- `/verify-email?token=...` — EmailVerificationPage

## Files to Reference

- `sections/authentication-account-management/spec.md` — Complete specification
- `sections/authentication-account-management/README.md` — Implementation guide
- `sections/authentication-account-management/types.ts` — TypeScript interfaces
- `sections/authentication-account-management/sample-data.json` — Example user data
- `sections/authentication-account-management/components/` — Reference components
- `sections/authentication-account-management/*.png` — Screenshots
- `sections/authentication-account-management/tests.md` — Test instructions

## Expected User Flows

### Flow 1: New user signs up with Google OAuth
1. User lands on `/signup` page
2. Sees "Continue with Google" button prominently displayed
3. Clicks Google OAuth button
4. Google authorization popup/redirect appears
5. User authorizes the app
6. Returns to app, auto-logged in
7. Redirected to dashboard

**Expected outcome:** User is authenticated and has an active session without entering email/password.

### Flow 2: New user signs up with email/password
1. User lands on `/signup` page
2. Scrolls past Google OAuth button to email/password form
3. Enters email address (validated for format)
4. Enters password (real-time strength indicator updates)
5. Password shows "weak" → user adds uppercase → shows "medium" → user adds number → shows "strong"
6. Enters password confirmation (matches original)
7. Clicks "Sign Up" button
8. Account created, verification email sent
9. User auto-logged in and redirected to dashboard

**Expected outcome:** User account is created, and user is immediately logged in without needing to verify email first (verification is optional background task).

### Flow 3: Returning user logs in
1. User lands on `/login` page
2. Sees Google OAuth button and email/password form
3. Enters email and password
4. Clicks "Login" button
5. Credentials validated
6. Redirected to dashboard or last visited page

**Expected outcome:** User is authenticated and sees their previous content.

### Flow 4: User forgets password
1. User clicks "Forgot password?" link on login page
2. Navigates to `/forgot-password`
3. Enters email address
4. Clicks "Send Reset Link" button
5. Success message appears: "Check your email for a password reset link"
6. User receives email with reset link
7. Clicks link, navigates to `/reset-password?token=...`
8. Enters new password (validated for strength)
9. Clicks "Reset Password" button
10. Password updated, success message shown
11. Redirected to `/login` after 3 seconds

**Expected outcome:** User successfully resets password and can log in with new credentials.

### Flow 5: User hits rate limit
1. User attempts login 5 times with incorrect password
2. After 5th attempt, lockout message appears
3. "Too many failed attempts. Try again in 15 minutes or reset your password."
4. Login button is disabled
5. User can click "Forgot password?" to bypass lockout

**Expected outcome:** Account is temporarily protected from brute force attacks.

### Flow 6: User session expires (with warning)
1. User is logged in and actively using the app
2. 5 minutes before session expires, warning banner appears at top
3. "Your session will expire soon. Extend session?"
4. User clicks "Extend Session" button
5. Session extended, warning disappears
6. User continues using the app

**Expected outcome:** User maintains active session without losing work or being logged out unexpectedly.

### Flow 7: User deletes account
1. User navigates to profile settings (implemented in later milestone)
2. Scrolls to Account section
3. Clicks "Delete Account" button
4. Confirmation dialog appears with warning
5. "This will permanently delete your account and all trip data. This action cannot be undone."
6. User clicks "Confirm Delete" button
7. Account and all associated data deleted
8. User logged out and redirected to `/signup`

**Expected outcome:** Account is permanently deleted with no remaining user data.

## Done When

- [ ] Signup page renders with Google OAuth button prominently at top
- [ ] Email/password signup form includes real-time validation
- [ ] Password strength indicator updates as user types (weak/medium/strong)
- [ ] Login page includes Google OAuth and email/password options
- [ ] "Forgot password?" link navigates to password reset request page
- [ ] Password reset flow sends email and allows password update
- [ ] Email verification page displays success message
- [ ] Rate limiting displays lockout message after 5 failed login attempts
- [ ] Session expiry warning appears 5 minutes before expiry with "Extend Session" button
- [ ] Account deletion dialog warns user of permanent data loss
- [ ] Change password form validates current password and new password strength
- [ ] All auth pages are mobile-responsive and work without app shell
- [ ] Light and dark mode styles are applied
- [ ] Show/hide password toggle works on all password fields
- [ ] Auto-focus on first form field improves UX
- [ ] Tests cover all user flows including edge cases (rate limiting, session expiry, validation errors)
- [ ] Visual appearance matches screenshots in section directory
