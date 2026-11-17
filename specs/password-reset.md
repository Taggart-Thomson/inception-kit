---
intent: "Let users reset a forgotten password by email (save the spec as specs/password-reset.md)"
slug: password-reset
status: draft
---

# Spec: Password reset by email

## Intent
A registered user who has forgotten their password can request a reset link by email and use it to set a new password, without contacting support.

## Assumptions
- Users already have accounts with a unique, verified email address and a password login.
- The system can send transactional email.
- Reset links are single-use and expire 60 minutes after issue.
- Passwords must be 12 to 128 characters.
- The response to a reset request is identical whether or not the email has an account, to prevent account enumeration.
- Resetting a password signs out all existing sessions for that account.

## Open questions
- Is 60 minutes the right link lifetime, and is 12 characters the right minimum password length?
- Should accounts with two-factor authentication need to pass a second factor after reset?
- What request rate limit does the business accept per email address and per IP address?
- Should the user be notified by email when their password is changed?
- Is the 3-per-60-minutes per-email limit in AC 1.2.1 and AC 1.2.3 the accepted value, is the window rolling or fixed, and what is the per-IP limit? (Blocks Story 1.2.)
- Is an email address matched case-insensitively? (Blocks AC 1.1.6.)
- Is a link still valid at exactly 60 minutes 0 seconds after issue? (AC 2.1.2 and AC 2.1.5 cover only 61 and 59 minutes.)
- What is the exact message for mismatched confirmation (AC 2.1.10)?

## Unit 1: Request a reset link

### Story 1.1: Request a reset email
As a user who forgot my password, I want to enter my email address and receive a reset link, so that I can regain access to my account.

#### Acceptance criteria
- **AC 1.1.1** Given a registered email address, when the user submits it on the forgot-password form, then an email containing a reset link is sent to that address within 60 seconds and the page shows "If an account exists, we have sent a reset link."
- **AC 1.1.2** [edge] Given an email address with no account, when the user submits it, then no email is sent and the page shows the same message "If an account exists, we have sent a reset link." as for a registered address.
- **AC 1.1.3** [edge] Given the string "not-an-email" (no "@"), when the user submits it on the forgot-password form, then the page shows "Enter a valid email address." and no email is sent.
- **AC 1.1.4** [edge] Given an empty email field on the forgot-password form, when the user submits it, then the page shows "Enter a valid email address." and no email is sent.
- **AC 1.1.5** [edge] Given a registered email address and the email service returns an error on send, when the user submits the address, then the page shows "If an account exists, we have sent a reset link." and the failure is written to the error log.
- **AC 1.1.6** [edge] Given a registered email address stored as "User@Example.com", when the user submits "user@example.com", then an email containing a reset link is sent to that account. (Depends on open question on case handling.)

### Story 1.2: Limit repeated requests
As a system owner, I want reset requests rate limited, so that the feature cannot be used to spam users or guess accounts.

#### Acceptance criteria
- **AC 1.2.1** Given a registered email address that has requested 3 reset links in the last 60 minutes, when it requests a 4th, then no email is sent and the page shows "If an account exists, we have sent a reset link." (Limit values are provisional; see open question on rate limits.)
- **AC 1.2.2** [edge] Given an account with an unused reset link A and a newer reset link B issued for the same account, when the user opens link A, then the page shows "This link is invalid or has expired." and no password form is shown.
- **AC 1.2.3** [edge] Given a registered email address that has requested exactly 2 reset links in the last 60 minutes, when it requests a 3rd, then an email containing a reset link is sent.

## Unit 2: Complete the reset

### Story 2.1: Set a new password from the link
As a user with a reset link, I want to choose a new password, so that I can sign in again.

#### Acceptance criteria
- **AC 2.1.1** Given a valid unexpired link, when the user submits a new 20-character password that matches its confirmation, then the password is changed, the page shows "Your password has been reset.", and signing in with the new password succeeds.
- **AC 2.1.2** [edge] Given a link issued 61 minutes ago, when the user opens it, then the page shows "This link is invalid or has expired." and no password form is shown.
- **AC 2.1.5** [edge] Given a link issued 59 minutes ago and not used, when the user opens it, then the password form is shown.
- **AC 2.1.6** [edge] Given a link whose token has been altered by changing its last character, when the user opens it, then the page shows "This link is invalid or has expired." and no password form is shown.
- **AC 2.1.3** [edge] Given a link that has already been used once, when the user opens it again, then the page shows "This link is invalid or has expired." and the password is unchanged.
- **AC 2.1.4** [edge] Given a valid link, when the user submits a password of 11 characters, then the page shows "Password must be 12 to 128 characters." and the password is unchanged.
- **AC 2.1.7** [edge] Given a valid link, when the user submits a password of exactly 12 characters that matches its confirmation, then the password is changed and the page shows "Your password has been reset."
- **AC 2.1.8** [edge] Given a valid link, when the user submits a password of exactly 128 characters that matches its confirmation, then the password is changed and the page shows "Your password has been reset."
- **AC 2.1.9** [edge] Given a valid link, when the user submits a password of 129 characters, then the page shows "Password must be 12 to 128 characters." and the password is unchanged.
- **AC 2.1.10** [edge] Given a valid link, when the user submits a 12-character password with a confirmation that differs, then the page shows "Passwords do not match." and the password is unchanged. (Message text is proposed; confirm.)
- **AC 2.1.11** [edge] Given a valid link, when the user submits an empty password, then the page shows "Password must be 12 to 128 characters." and the password is unchanged.
- **AC 2.1.12** [edge] Given a valid link and a failed first submission (11 characters), when the user then submits a valid 12-character password with matching confirmation, then the password is changed (the link was not consumed by the failed attempt).

### Story 2.2: Revoke old access after reset
As a user whose account may be compromised, I want existing sessions ended when the password is reset, so that anyone holding the old session loses access.

#### Acceptance criteria
- **AC 2.2.1** Given an account with 2 active sessions, when a password reset completes, then a request to the account page from each of those sessions returns the sign-in page instead of account content.
- **AC 2.2.3** Given an account whose password was just reset, when someone signs in with the old password, then sign-in fails with the standard invalid-credentials message.
- **AC 2.2.2** [edge] Given an account with 2 active sessions, when the user submits an 11-character password on a valid reset link, then a request to the account page from each session still returns account content.

## Review
Verdict: draft (not approved). Open questions block several criteria.
- Rewritten: 6 (AC 1.1.3, 1.2.1, 1.2.2, 2.1.1, 2.2.1, 2.2.2). Added: 13 (AC 1.1.4, 1.1.5, 1.1.6, 1.2.3, 2.1.5 to 2.1.12, 2.2.3).
- Unresolved: rate limit value, window type and per-IP limit (blocks AC 1.2.1, 1.2.3).
- Unresolved: email case handling (blocks AC 1.1.6).
- Unresolved: validity at exactly 60 minutes (no AC possible at the boundary).
- Unresolved: mismatch message text (AC 2.1.10 is proposed, not confirmed).
- Unresolved: 2FA after reset, change-notification email, and whether 60 minutes and 12 characters are the right values.
