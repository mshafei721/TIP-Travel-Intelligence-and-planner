# Authentication & Account Management - Test Specifications

## Overview

This document defines comprehensive test cases for the Authentication & Account Management section. All tests must pass before the feature is considered complete.

## Test Strategy

- **Unit Tests**: Individual component behavior and validation logic
- **Integration Tests**: Auth flows with Supabase
- **E2E Tests**: Complete user journeys
- **Accessibility Tests**: ARIA, keyboard navigation, screen readers

## 1. Password Validation Tests

### Unit Tests: `lib/auth/validation.ts`

```typescript
describe('validatePassword', () => {
  it('rejects passwords under 8 characters', () => {
    const result = validatePassword('Pass1!')
    expect(result.isValid).toBe(false)
    expect(result.feedback).toContain('Password must be at least 8 characters')
  })

  it('rejects passwords without uppercase', () => {
    const result = validatePassword('password123!')
    expect(result.isValid).toBe(false)
    expect(result.feedback).toContain('Include at least one uppercase letter')
  })

  it('rejects passwords without lowercase', () => {
    const result = validatePassword('PASSWORD123!')
    expect(result.isValid).toBe(false)
    expect(result.feedback).toContain('Include at least one lowercase letter')
  })

  it('rejects passwords without numbers', () => {
    const result = validatePassword('Password!')
    expect(result.isValid).toBe(false)
    expect(result.feedback).toContain('Include at least one number')
  })

  it('rejects passwords without special characters', () => {
    const result = validatePassword('Password123')
    expect(result.isValid).toBe(false)
    expect(result.feedback).toContain('Include at least one special character')
  })

  it('accepts valid password with all requirements', () => {
    const result = validatePassword('Password123!')
    expect(result.isValid).toBe(true)
    expect(result.feedback).toHaveLength(0)
  })

  it('rates 8-char password as weak', () => {
    const result = validatePassword('Pass123!')
    expect(result.strength).toBe('weak')
  })

  it('rates 10-char password as medium', () => {
    const result = validatePassword('Password12!')
    expect(result.strength).toBe('medium')
  })

  it('rates 12+ char password as strong', () => {
    const result = validatePassword('SecurePassword123!')
    expect(result.strength).toBe('strong')
  })
})

describe('validateEmail', () => {
  it('accepts valid email addresses', () => {
    expect(validateEmail('user@example.com')).toBe(true)
    expect(validateEmail('test.user+tag@domain.co.uk')).toBe(true)
  })

  it('rejects invalid email addresses', () => {
    expect(validateEmail('notanemail')).toBe(false)
    expect(validateEmail('@example.com')).toBe(false)
    expect(validateEmail('user@')).toBe(false)
    expect(validateEmail('user @example.com')).toBe(false)
  })

  it('rejects emails over 255 characters', () => {
    const longEmail = 'a'.repeat(250) + '@test.com'
    expect(validateEmail(longEmail)).toBe(false)
  })
})

describe('validateName', () => {
  it('accepts names between 2-100 characters', () => {
    expect(validateName('Jo')).toBe(true)
    expect(validateName('Sarah Chen')).toBe(true)
  })

  it('rejects names under 2 characters', () => {
    expect(validateName('J')).toBe(false)
    expect(validateName('')).toBe(false)
  })

  it('rejects names over 100 characters', () => {
    expect(validateName('a'.repeat(101))).toBe(false)
  })

  it('trims whitespace before validation', () => {
    expect(validateName('  Jo  ')).toBe(true)
  })
})
```

## 2. Rate Limiting Tests

### Unit Tests: `lib/auth/rate-limit.ts`

```typescript
describe('Rate Limiting', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('starts with zero attempts', () => {
    const state = getRateLimitState('test@example.com')
    expect(state.attempts).toBe(0)
    expect(state.isLocked).toBe(false)
  })

  it('increments attempts on failed login', () => {
    recordFailedAttempt('test@example.com')
    const state = getRateLimitState('test@example.com')
    expect(state.attempts).toBe(1)
  })

  it('locks account after 5 failed attempts', () => {
    for (let i = 0; i < 5; i++) {
      recordFailedAttempt('test@example.com')
    }
    const state = getRateLimitState('test@example.com')
    expect(state.isLocked).toBe(true)
    expect(state.lockedUntil).toBeTruthy()
  })

  it('sets lockout duration to 15 minutes', () => {
    for (let i = 0; i < 5; i++) {
      recordFailedAttempt('test@example.com')
    }
    const state = getRateLimitState('test@example.com')
    const lockoutDuration = state.lockedUntil!.getTime() - Date.now()
    expect(lockoutDuration).toBeGreaterThan(14 * 60 * 1000) // At least 14 minutes
    expect(lockoutDuration).toBeLessThan(16 * 60 * 1000) // At most 16 minutes
  })

  it('clears attempts after successful login', () => {
    recordFailedAttempt('test@example.com')
    clearRateLimit('test@example.com')
    const state = getRateLimitState('test@example.com')
    expect(state.attempts).toBe(0)
  })

  it('normalizes email to lowercase', () => {
    recordFailedAttempt('Test@Example.COM')
    const state = getRateLimitState('test@example.com')
    expect(state.attempts).toBe(1)
  })
})
```

## 3. SignupForm Component Tests

### Component Tests: `components/auth/SignupForm.tsx`

```typescript
describe('SignupForm', () => {
  it('renders Google OAuth button prominently', () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)
    const googleButton = screen.getByRole('button', { name: /continue with google/i })
    expect(googleButton).toBeInTheDocument()
    expect(googleButton).toBeVisible()
  })

  it('renders email/password form below OAuth', () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
  })

  it('shows real-time password strength indicator', async () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)
    const passwordInput = screen.getByLabelText(/^password$/i)

    await userEvent.type(passwordInput, 'weak')
    expect(screen.getByText(/weak/i)).toBeInTheDocument()

    await userEvent.clear(passwordInput)
    await userEvent.type(passwordInput, 'StrongPass123!')
    expect(screen.getByText(/strong/i)).toBeInTheDocument()
  })

  it('validates email format on blur', async () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)
    const emailInput = screen.getByLabelText(/email/i)

    await userEvent.type(emailInput, 'invalidemail')
    await userEvent.tab()

    expect(screen.getByText(/invalid email/i)).toBeInTheDocument()
  })

  it('shows error when passwords do not match', async () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)

    await userEvent.type(screen.getByLabelText(/^password$/i), 'Password123!')
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'Different123!')
    await userEvent.tab()

    expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
  })

  it('disables submit button when form is invalid', () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)
    const submitButton = screen.getByRole('button', { name: /sign up/i })
    expect(submitButton).toBeDisabled()
  })

  it('enables submit button when form is valid', async () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)

    await userEvent.type(screen.getByLabelText(/name/i), 'Sarah Chen')
    await userEvent.type(screen.getByLabelText(/email/i), 'sarah@example.com')
    await userEvent.type(screen.getByLabelText(/^password$/i), 'SecurePass123!')
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'SecurePass123!')

    const submitButton = screen.getByRole('button', { name: /sign up/i })
    expect(submitButton).toBeEnabled()
  })

  it('calls onSignup with credentials on submit', async () => {
    const onSignup = jest.fn()
    render(<SignupForm onSignup={onSignup} onGoogleAuth={jest.fn()} />)

    await userEvent.type(screen.getByLabelText(/name/i), 'Sarah Chen')
    await userEvent.type(screen.getByLabelText(/email/i), 'sarah@example.com')
    await userEvent.type(screen.getByLabelText(/^password$/i), 'SecurePass123!')
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'SecurePass123!')
    await userEvent.click(screen.getByRole('button', { name: /sign up/i }))

    expect(onSignup).toHaveBeenCalledWith({
      name: 'Sarah Chen',
      email: 'sarah@example.com',
      password: 'SecurePass123!',
    })
  })

  it('shows loading state during signup', async () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} isLoading={true} />)
    expect(screen.getByRole('button', { name: /signing up/i })).toBeDisabled()
  })

  it('displays error message from prop', () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} error="Email already exists" />)
    expect(screen.getByText(/email already exists/i)).toBeInTheDocument()
  })

  it('has show/hide password toggle', async () => {
    render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)
    const passwordInput = screen.getByLabelText(/^password$/i)
    expect(passwordInput).toHaveAttribute('type', 'password')

    const toggleButton = screen.getAllByRole('button', { name: /show password/i })[0]
    await userEvent.click(toggleButton)

    expect(passwordInput).toHaveAttribute('type', 'text')
  })
})
```

## 4. LoginForm Component Tests

```typescript
describe('LoginForm', () => {
  it('renders Google OAuth button prominently', () => {
    render(<LoginForm onLogin={jest.fn()} onGoogleAuth={jest.fn()} />)
    expect(screen.getByRole('button', { name: /continue with google/i })).toBeInTheDocument()
  })

  it('renders email and password fields', () => {
    render(<LoginForm onLogin={jest.fn()} onGoogleAuth={jest.fn()} />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('renders "Forgot password?" link', () => {
    render(<LoginForm onLogin={jest.fn()} onGoogleAuth={jest.fn()} />)
    expect(screen.getByRole('link', { name: /forgot password/i })).toHaveAttribute('href', '/forgot-password')
  })

  it('renders "Remember me" checkbox', () => {
    render(<LoginForm onLogin={jest.fn()} onGoogleAuth={jest.fn()} />)
    expect(screen.getByLabelText(/remember me/i)).toBeInTheDocument()
  })

  it('calls onLogin with credentials', async () => {
    const onLogin = jest.fn()
    render(<LoginForm onLogin={onLogin} onGoogleAuth={jest.fn()} />)

    await userEvent.type(screen.getByLabelText(/email/i), 'sarah@example.com')
    await userEvent.type(screen.getByLabelText(/password/i), 'Password123!')
    await userEvent.click(screen.getByRole('button', { name: /log in/i }))

    expect(onLogin).toHaveBeenCalledWith({
      email: 'sarah@example.com',
      password: 'Password123!',
      rememberMe: false,
    })
  })

  it('includes rememberMe in login credentials', async () => {
    const onLogin = jest.fn()
    render(<LoginForm onLogin={onLogin} onGoogleAuth={jest.fn()} />)

    await userEvent.type(screen.getByLabelText(/email/i), 'sarah@example.com')
    await userEvent.type(screen.getByLabelText(/password/i), 'Password123!')
    await userEvent.click(screen.getByLabelText(/remember me/i))
    await userEvent.click(screen.getByRole('button', { name: /log in/i }))

    expect(onLogin).toHaveBeenCalledWith({
      email: 'sarah@example.com',
      password: 'Password123!',
      rememberMe: true,
    })
  })

  it('shows rate limit lockout message', () => {
    render(
      <LoginForm
        onLogin={jest.fn()}
        onGoogleAuth={jest.fn()}
        rateLimited={true}
        lockoutEndsAt={new Date(Date.now() + 15 * 60 * 1000).toISOString()}
      />
    )
    expect(screen.getByText(/too many failed attempts/i)).toBeInTheDocument()
  })

  it('disables login button when rate limited', () => {
    render(
      <LoginForm
        onLogin={jest.fn()}
        onGoogleAuth={jest.fn()}
        rateLimited={true}
      />
    )
    expect(screen.getByRole('button', { name: /log in/i })).toBeDisabled()
  })
})
```

## 5. Password Reset Flow Tests

```typescript
describe('PasswordResetRequestForm', () => {
  it('renders email input field', () => {
    render(<PasswordResetRequestForm onRequestReset={jest.fn()} />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
  })

  it('calls onRequestReset with email', async () => {
    const onRequestReset = jest.fn()
    render(<PasswordResetRequestForm onRequestReset={onRequestReset} />)

    await userEvent.type(screen.getByLabelText(/email/i), 'sarah@example.com')
    await userEvent.click(screen.getByRole('button', { name: /send reset link/i }))

    expect(onRequestReset).toHaveBeenCalledWith('sarah@example.com')
  })

  it('shows success message after email sent', () => {
    render(<PasswordResetRequestForm onRequestReset={jest.fn()} emailSent={true} />)
    expect(screen.getByText(/check your email/i)).toBeInTheDocument()
  })

  it('provides link back to login', () => {
    render(<PasswordResetRequestForm onRequestReset={jest.fn()} />)
    expect(screen.getByRole('link', { name: /back to login/i })).toHaveAttribute('href', '/login')
  })
})

describe('PasswordResetForm', () => {
  it('renders new password fields', () => {
    render(<PasswordResetForm token="test-token" onResetPassword={jest.fn()} />)
    expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
  })

  it('shows password strength indicator', async () => {
    render(<PasswordResetForm token="test-token" onResetPassword={jest.fn()} />)
    await userEvent.type(screen.getByLabelText(/new password/i), 'SecurePass123!')
    expect(screen.getByText(/strong/i)).toBeInTheDocument()
  })

  it('calls onResetPassword with new password', async () => {
    const onResetPassword = jest.fn()
    render(<PasswordResetForm token="test-token" onResetPassword={onResetPassword} />)

    await userEvent.type(screen.getByLabelText(/new password/i), 'SecurePass123!')
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'SecurePass123!')
    await userEvent.click(screen.getByRole('button', { name: /reset password/i }))

    expect(onResetPassword).toHaveBeenCalledWith('SecurePass123!')
  })

  it('shows success message and redirects', () => {
    render(<PasswordResetForm token="test-token" onResetPassword={jest.fn()} success={true} />)
    expect(screen.getByText(/password updated successfully/i)).toBeInTheDocument()
  })
})
```

## 6. Integration Tests (with Supabase)

```typescript
describe('Authentication Integration', () => {
  it('successfully signs up new user', async () => {
    const result = await signUp({
      name: 'Test User',
      email: `test-${Date.now()}@example.com`,
      password: 'SecurePass123!',
    })

    expect(result.error).toBeNull()
    expect(result.data?.user).toBeTruthy()
  })

  it('creates user profile on signup', async () => {
    const email = `test-${Date.now()}@example.com`
    const result = await signUp({
      name: 'Test User',
      email,
      password: 'SecurePass123!',
    })

    const supabase = createClient()
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('id', result.data!.user!.id)
      .single()

    expect(profile).toBeTruthy()
    expect(profile?.display_name).toBe('Test User')
  })

  it('successfully signs in existing user', async () => {
    // First create user
    const email = `test-${Date.now()}@example.com`
    await signUp({
      name: 'Test User',
      email,
      password: 'SecurePass123!',
    })

    // Then sign in
    const result = await signIn({
      email,
      password: 'SecurePass123!',
    })

    expect(result.error).toBeNull()
    expect(result.data?.session).toBeTruthy()
  })

  it('rejects invalid credentials', async () => {
    const result = await signIn({
      email: 'nonexistent@example.com',
      password: 'WrongPass123!',
    })

    expect(result.error).toBeTruthy()
  })

  it('sends password reset email', async () => {
    const result = await requestPasswordReset('test@example.com')
    expect(result.error).toBeNull()
  })
})
```

## 7. E2E Tests (Full User Journeys)

```typescript
describe('E2E: Complete Signup Flow', () => {
  it('allows user to sign up and access dashboard', async () => {
    // Navigate to signup
    await page.goto('/signup')

    // Fill form
    await page.fill('[name="name"]', 'Test User')
    await page.fill('[name="email"]', `test-${Date.now()}@example.com`)
    await page.fill('[name="password"]', 'SecurePass123!')
    await page.fill('[name="confirmPassword"]', 'SecurePass123!')

    // Submit
    await page.click('button[type="submit"]')

    // Should redirect to dashboard
    await page.waitForURL('/')
    expect(await page.textContent('h1')).toContain('Dashboard')
  })
})

describe('E2E: Complete Login Flow', () => {
  it('allows user to login and access dashboard', async () => {
    await page.goto('/login')
    await page.fill('[name="email"]', 'existing@example.com')
    await page.fill('[name="password"]', 'Password123!')
    await page.click('button[type="submit"]')

    await page.waitForURL('/')
    expect(await page.textContent('h1')).toContain('Dashboard')
  })
})

describe('E2E: Password Reset Flow', () => {
  it('completes full password reset journey', async () => {
    // Request reset
    await page.goto('/forgot-password')
    await page.fill('[name="email"]', 'test@example.com')
    await page.click('button[type="submit"]')

    // Verify success message
    expect(await page.textContent('.success-message')).toContain('Check your email')

    // TODO: In real e2e, would check email and click link
    // For now, manually navigate to reset page
    await page.goto('/reset-password?token=test-token')
    await page.fill('[name="newPassword"]', 'NewSecurePass123!')
    await page.fill('[name="confirmPassword"]', 'NewSecurePass123!')
    await page.click('button[type="submit"]')

    // Should show success and redirect
    await page.waitForURL('/login')
  })
})
```

## 8. Accessibility Tests

```typescript
describe('Accessibility', () => {
  it('has proper ARIA labels on all form fields', () => {
    const { container } = render(<SignupForm onSignup={jest.fn()} onGoogleAuth={jest.fn()} />)
    const inputs = container.querySelectorAll('input')
    inputs.forEach(input => {
      expect(input).toHaveAccessibleName()
    })
  })

  it('announces errors to screen readers', async () => {
    render(<LoginForm onLogin={jest.fn()} onGoogleAuth={jest.fn()} error="Invalid credentials" />)
    const errorElement = screen.getByRole('alert')
    expect(errorElement).toHaveTextContent('Invalid credentials')
  })

  it('supports keyboard navigation', async () => {
    render(<LoginForm onLogin={jest.fn()} onGoogleAuth={jest.fn()} />)

    // Tab through form
    await userEvent.tab()
    expect(screen.getByLabelText(/email/i)).toHaveFocus()

    await userEvent.tab()
    expect(screen.getByLabelText(/password/i)).toHaveFocus()
  })

  it('submits form on Enter key', async () => {
    const onLogin = jest.fn()
    render(<LoginForm onLogin={onLogin} onGoogleAuth={jest.fn()} />)

    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com')
    await userEvent.type(screen.getByLabelText(/password/i), 'Password123!{Enter}')

    expect(onLogin).toHaveBeenCalled()
  })
})
```

## Test Coverage Requirements

- **Unit Tests**: ≥90% code coverage
- **Component Tests**: 100% of user-facing components
- **Integration Tests**: All critical auth flows
- **E2E Tests**: All user journeys from spec
- **Accessibility**: WCAG 2.1 AA compliance

## Running Tests

```bash
# Unit and component tests
npm test

# Integration tests (requires Supabase)
npm run test:integration

# E2E tests
npm run test:e2e

# Coverage report
npm run test:coverage

# Watch mode
npm run test:watch
```

## Success Criteria

All tests must pass before marking authentication section as complete:

- [ ] All unit tests passing
- [ ] All component tests passing
- [ ] All integration tests passing
- [ ] All E2E tests passing
- [ ] All accessibility tests passing
- [ ] Code coverage ≥90%
- [ ] No console errors or warnings
- [ ] Manual QA checklist completed
