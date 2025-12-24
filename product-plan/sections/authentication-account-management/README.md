# Authentication & Account Management

## Overview

Complete authentication system providing user signup, login, password management, and account lifecycle operations. Features Google OAuth as the primary authentication method with email/password as an alternative, real-time form validation, session management, and comprehensive security measures including rate limiting and account deletion.

## User Flows

### Primary Flows

**Signup Flow**
1. User navigates to `/signup`
2. Sees Google OAuth button prominently displayed
3. Can choose OAuth or email/password signup
4. If email/password: enters credentials with real-time validation
5. Password strength indicator shows requirements (8+ chars, uppercase, number, special char)
6. Submits form
7. Verification email sent
8. Auto-login occurs immediately
9. Redirected to dashboard or trip creation

**Login Flow**
1. User navigates to `/login`
2. Sees Google OAuth button prominently
3. Can choose OAuth or email/password login
4. If email/password: enters credentials
5. Submits form
6. Session established
7. Redirected to dashboard or last visited page

**Google OAuth Flow**
1. User clicks "Continue with Google"
2. Google popup/redirect appears
3. User authorizes the application
4. Returns to app with OAuth token
5. Auto-login completes
6. Redirected to dashboard

**Password Reset Flow**
1. User clicks "Forgot password?" on login page
2. Enters email address on `/forgot-password`
3. Receives reset email
4. Clicks link in email → `/reset-password?token=...`
5. Enters new password (validated for strength)
6. Password updated successfully
7. Redirected to login page

**Email Verification Flow**
1. After signup, verification email sent automatically
2. User receives email with verification link
3. Clicks link → `/verify-email?token=...`
4. Email confirmed
5. Success message displayed
6. "Continue to Login" button appears

### Secondary Flows

**Logout Flow**
1. User clicks logout from user menu
2. Confirmation (optional)
3. Session terminated
4. Local storage cleared
5. Redirected to `/login`

**Delete Account Flow**
1. User navigates to account settings
2. Clicks "Delete Account" button
3. Confirmation dialog appears with explicit warning
4. User confirms deletion
5. Account and all trip data permanently deleted
6. Session terminated
7. Redirected to `/signup`

**Change Password Flow**
1. User navigates to profile/settings
2. Clicks "Change Password"
3. Enters current password
4. Enters new password (validated for strength)
5. Confirms new password
6. Password updated
7. Success message displayed

**Rate Limit Handling**
1. User attempts 5+ failed logins
2. Account temporarily locked (15 minutes)
3. Lockout message displayed
4. User can wait or use password reset

**Session Expiry Handling**
1. Session expires after inactivity
2. Warning banner appears 5 minutes before expiry
3. User can click "Extend Session" to continue
4. Or let session expire → redirect to login

## Design Decisions

### Authentication Strategy
- **Google OAuth First**: Prominently displayed as primary method for faster signup/login
- **Email/Password Alternative**: Available below OAuth with clear "Or" separator
- **Auto-Login After Signup**: Reduces friction, immediate value delivery
- **No 2FA/MFA**: Explicitly out of scope for V1, can be added later
- **Social Providers**: Only Google for now (Facebook, Apple, Twitter excluded)

### Security Measures
- **Password Strength**: Enforced requirements (8+ chars, uppercase, number, special)
- **Rate Limiting**: 5 failed attempts = 15-minute lockout
- **Session Management**: Token-based with configurable expiration
- **Session Warnings**: 5-minute advance warning before expiry
- **Email Verification**: Optional but recommended for production

### UX Decisions
- **Standalone Pages**: No app shell (focused auth experience)
- **Real-Time Validation**: Field-level errors as user types
- **Password Visibility Toggle**: Show/hide password button
- **Auto-Focus**: First field automatically focused
- **Mobile Optimization**: Large touch targets, responsive design
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support

## Data Used

### Authentication Data (`data.json`)

```json
{
  "user": {
    "id": "user-001",
    "email": "sarah@example.com",
    "name": "Sarah Chen",
    "authProvider": "google",
    "emailVerified": true,
    "createdAt": "2025-12-01T10:00:00Z"
  },
  "session": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2025-12-23T18:00:00Z",
    "lastActivity": "2025-12-23T15:30:00Z"
  },
  "loginAttempts": {
    "count": 2,
    "lastAttempt": "2025-12-23T15:00:00Z",
    "lockedUntil": null
  }
}
```

## Components

### SignupPage.tsx
Full-page signup form with Google OAuth and email/password options.

**Props:**
```typescript
interface SignupPageProps {
  onSignup: (credentials: SignupCredentials) => Promise<void>;
  onGoogleAuth: () => Promise<void>;
  isLoading?: boolean;
  error?: string;
}

interface SignupCredentials {
  email: string;
  password: string;
  name: string;
}
```

**Features:**
- Google OAuth button (prominently displayed)
- Email/password form with validation
- Real-time password strength indicator
- Confirm password field
- Link to login page
- Error message display
- Loading states

### LoginPage.tsx
Full-page login form with Google OAuth and email/password options.

**Props:**
```typescript
interface LoginPageProps {
  onLogin: (credentials: LoginCredentials) => Promise<void>;
  onGoogleAuth: () => Promise<void>;
  isLoading?: boolean;
  error?: string;
  rateLimited?: boolean;
  lockoutEndsAt?: string;
}

interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}
```

**Features:**
- Google OAuth button (prominently displayed)
- Email/password form
- "Forgot password?" link
- "Remember me" checkbox
- Link to signup page
- Rate limit lockout message
- Error message display

### PasswordResetRequestPage.tsx
Page for initiating password reset.

**Props:**
```typescript
interface PasswordResetRequestPageProps {
  onRequestReset: (email: string) => Promise<void>;
  isLoading?: boolean;
  emailSent?: boolean;
}
```

**Features:**
- Email input field
- Submit button
- Success message after email sent
- Link back to login

### PasswordResetPage.tsx
Page for setting new password after clicking email link.

**Props:**
```typescript
interface PasswordResetPageProps {
  token: string;
  onResetPassword: (password: string) => Promise<void>;
  isLoading?: boolean;
  success?: boolean;
  error?: string;
}
```

**Features:**
- New password field with strength indicator
- Confirm password field
- Submit button
- Success message
- Auto-redirect to login after 3 seconds

### EmailVerificationPage.tsx
Page displayed after clicking verification link in email.

**Props:**
```typescript
interface EmailVerificationPageProps {
  token: string;
  onVerify: () => Promise<void>;
  isLoading?: boolean;
  success?: boolean;
  error?: string;
}
```

**Features:**
- Loading state (auto-verifies on mount)
- Success message
- Error message (invalid/expired token)
- "Continue to Login" button

### ChangePasswordForm.tsx
Form component for changing password in settings.

**Props:**
```typescript
interface ChangePasswordFormProps {
  onChangePassword: (passwords: ChangePasswordData) => Promise<void>;
  isLoading?: boolean;
  success?: boolean;
  error?: string;
}

interface ChangePasswordData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}
```

**Features:**
- Current password field
- New password field with strength indicator
- Confirm new password field
- Submit button
- Success/error messages

### DeleteAccountDialog.tsx
Confirmation dialog for account deletion.

**Props:**
```typescript
interface DeleteAccountDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  isLoading?: boolean;
}
```

**Features:**
- Warning message
- Explicit confirmation
- Cancel button
- Delete button (destructive style)
- Loading state

### SessionExpiryBanner.tsx
Warning banner shown before session expires.

**Props:**
```typescript
interface SessionExpiryBannerProps {
  expiresAt: string;
  onExtendSession: () => Promise<void>;
  onDismiss: () => void;
}
```

**Features:**
- Countdown timer
- "Extend Session" button
- Dismiss button
- Auto-dismiss after extension

## Callback Props

| Prop | Type | Description |
|------|------|-------------|
| `onSignup` | `(credentials: SignupCredentials) => Promise<void>` | Handle user signup with email/password |
| `onLogin` | `(credentials: LoginCredentials) => Promise<void>` | Handle user login with email/password |
| `onGoogleAuth` | `() => Promise<void>` | Initiate Google OAuth flow |
| `onRequestReset` | `(email: string) => Promise<void>` | Send password reset email |
| `onResetPassword` | `(password: string) => Promise<void>` | Update password with reset token |
| `onVerify` | `() => Promise<void>` | Verify email with token |
| `onChangePassword` | `(data: ChangePasswordData) => Promise<void>` | Change user password |
| `onDeleteAccount` | `() => Promise<void>` | Permanently delete user account |
| `onExtendSession` | `() => Promise<void>` | Extend current session |
| `onLogout` | `() => Promise<void>` | End user session |

## States

### Loading States
- Form submission in progress
- OAuth redirect in progress
- Email verification check
- Password reset processing
- Account deletion in progress

### Success States
- Signup completed (auto-login)
- Login successful
- Password reset email sent
- Password updated
- Email verified
- Account deleted

### Error States
- Invalid credentials
- Email already exists
- Weak password
- Password mismatch
- Rate limited (too many attempts)
- Invalid/expired token
- Network error
- Server error

## Validation Rules

### Email Validation
- Required field
- Valid email format (regex check)
- Maximum 255 characters

### Password Validation
- Required field
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character
- Maximum 128 characters

### Password Strength Calculation
- **Weak**: Meets minimum requirements only
- **Medium**: 10+ characters with variety
- **Strong**: 12+ characters with high variety

### Name Validation
- Required for signup
- Minimum 2 characters
- Maximum 100 characters

## Security Considerations

1. **Password Storage**: Never store passwords in plain text (hash with bcrypt/argon2)
2. **Token Security**: Use secure, random tokens for reset/verification
3. **HTTPS Only**: All auth endpoints must use HTTPS in production
4. **CSRF Protection**: Implement CSRF tokens for state-changing operations
5. **Rate Limiting**: Enforce at API level (5 attempts per 15 minutes)
6. **Session Security**: HTTPOnly cookies, secure flags, SameSite attribute
7. **OAuth Security**: Validate state parameter, verify redirect URI

## Accessibility

- All form fields have proper `<label>` elements
- ARIA labels on buttons and interactive elements
- Keyboard navigation fully supported (Tab, Enter, Escape)
- Focus indicators visible on all interactive elements
- Screen reader announcements for errors and success messages
- Color not used as only indicator (icons + text for status)
- Sufficient color contrast (WCAG AA minimum)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari (iOS 14+)
- Chrome Mobile (Android 10+)

## Future Enhancements

- Two-factor authentication (2FA/MFA)
- Additional OAuth providers (Facebook, Apple, Twitter)
- Passwordless authentication (magic links)
- Biometric authentication (WebAuthn)
- Security keys support
- Login history/activity log
- Device management
- Account recovery questions
