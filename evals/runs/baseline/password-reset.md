---
intent: "Let users reset a forgotten password by email"
slug: password-reset-by-email
status: draft
---

# Spec: Password reset by email

## Intent
Users who have forgotten their password can request a reset link sent to their registered email address and use it to set a new password, regaining access to their account without contacting support.

## Assumptions
- Users already have accounts with a verified email address and a password-based login.
- Reset links are single-use and expire after 60 minutes.
- Password rules for a reset are the same as those for registration.
- Existing sessions are signed out when a password is changed.
- Outbound email delivery infrastructure already exists.

## Open questions
- What should the minimum password rules be, and should reuse of recent passwords be blocked?
- Should accounts with multi-factor authentication require the second factor after a reset?
- What rate limits are acceptable for reset requests per email address and per IP address?
- Should users be notified by email when their password has been changed?

## Unit 1: Request a reset link

### Story 1.1: Request a reset email
As a user who forgot my password, I want to enter my email address and receive a reset link, so that I can start recovering my account.

#### Acceptance criteria
- **AC 1.1.1** Given I am on the login page, when I choose "Forgot password" and submit the email of an existing account, then I see a confirmation that instructions were sent and an email with a reset link arrives at that address.
- **AC 1.1.2** [edge] Given I submit an email address that matches no account, when I submit the form, then I see the same confirmation message as for a real account and no email is sent.
- **AC 1.1.3** [edge] Given I submit a malformed email address, when I submit the form, then I see a validation error and no request is created.

### Story 1.2: Limit reset requests
As a site operator, I want reset requests to be rate limited, so that the feature cannot be used to spam users or probe accounts.

#### Acceptance criteria
- **AC 1.2.1** Given an email address has made fewer requests than the limit, when a new request is submitted, then it is accepted normally.
- **AC 1.2.2** [edge] Given an email address or IP address has reached the request limit, when another request is submitted, then no additional email is sent and the user sees the same generic confirmation message.

## Unit 2: Set a new password

### Story 2.1: Choose a new password from the link
As a user with a reset link, I want to set a new password, so that I can log in again.

#### Acceptance criteria
- **AC 2.1.1** Given I open a valid, unexpired reset link, when I enter a new password that meets the rules and confirm it, then my password is changed and I can log in with it.
- **AC 2.1.2** [edge] Given I open a reset link that has expired, when the page loads, then I see an expiry message and an option to request a new link, and no password can be set.
- **AC 2.1.3** [edge] Given a reset link has already been used, when I open it again, then I see that the link is no longer valid and cannot change the password.
- **AC 2.1.4** [edge] Given I enter a password that fails the rules or the confirmation does not match, when I submit, then I see a specific error and the password is unchanged.

### Story 2.2: Invalidate older links and sessions
As a user, I want a successful reset to secure my account, so that anyone else with old links or sessions loses access.

#### Acceptance criteria
- **AC 2.2.1** Given I have a signed-in session on another device, when I complete a password reset, then that session is signed out.
- **AC 2.2.2** [edge] Given I requested two reset links, when I use the newer one, then the older link also stops working.

## Unit 3: Reset notification

### Story 3.1: Notify the user of a password change
As a user, I want an email when my password is changed, so that I can spot an unauthorised reset.

#### Acceptance criteria
- **AC 3.1.1** Given I complete a password reset, when the change is saved, then a confirmation email is sent to my registered address stating the time of the change.
- **AC 3.1.2** [edge] Given the confirmation email fails to send, when the password reset completes, then the password change still succeeds and the failure is logged.
