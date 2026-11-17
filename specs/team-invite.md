---
intent: "Let a workspace admin invite teammates by email and give each a role (save the spec as specs/team-invite.md)"
slug: team-invite
status: draft
---

# Spec: Team invitations with roles

## Intent
A workspace admin can invite people to the workspace by email address and choose a role for each invitee. The invitee accepts through the emailed link and joins with that role.

## Assumptions
- Only users with the Admin role can send invitations.
- The available roles are Admin, Member and Viewer.
- An invitation is sent to one email address and is valid for 7 days.
- Invitees without an account create one when they accept; invitees with an account join with the existing one.
- A workspace holds at most 100 pending invitations.

## Open questions
- Which roles exist, and can an admin invite another admin?
- Is there a seat or plan limit on the number of members, and what happens when it is reached?
- Should invitations be restricted to specific email domains?
- Should an admin be able to change a member's role after they have joined? (Out of scope here unless confirmed.)
- Is an invitation still valid at exactly 7 days (168 hours) after sending, or does it expire at that instant? AC 2.1.5 and 2.1.6 cover only 1 hour either side.
- If a pending invitation exists for an address and the admin invites it again with a different role, is it rejected (as AC 1.1.2 assumes), or does it update the role?
- Is the duplicate check case-insensitive ("Ana@Example.com" vs "ana@example.com")? AC 1.1.4 assumes yes.
- If a user opens the link while signed in as a different email address than the one invited, what happens? (No criterion written.)
- When an invitation is resent, does the earlier link stop working? (No criterion written.)
- What does the admin see when the email provider fails to send? AC 1.1.7 needs the exact message and whether the invitation stays pending.
- What does a new invitee (no account) see on accept: which fields, and what are the password rules? AC 2.1.1 only covers the existing-account path.
- Can an admin invite an address that already belongs to a workspace member? (No criterion written.)

## Unit 1: Send invitations

### Story 1.1: Invite one teammate with a role
As a workspace admin, I want to enter an email address and pick a role, so that the teammate is invited with the right access from the start.

#### Acceptance criteria
- **AC 1.1.1** Given I am an admin on the Invite form, when I enter "ana@example.com", select the role Member and click Send, then the invitation appears in the pending list as "ana@example.com – Member" and one email is sent to ana@example.com.
- **AC 1.1.2** [edge] Given "ana@example.com" already has a pending invitation, when I invite that address again, then no second email is sent and the form shows "An invitation is already pending for this email".
- **AC 1.1.3** [edge] Given I enter "ana@example" (no top-level domain), when I click Send, then the form shows "Enter a valid email address" and the pending list count is unchanged.
- **AC 1.1.4** [edge] Given "ana@example.com" has a pending invitation, when I enter "Ana@Example.com" and click Send, then no email is sent and the form shows "An invitation is already pending for this email".
- **AC 1.1.5** [edge] Given the email field is empty, when I click Send, then the form shows "Enter a valid email address", no email is sent and the pending list count is unchanged.
- **AC 1.1.6** [edge] Given I am an admin and have entered "ana@example.com" with no role selected, when I click Send, then the form shows "Select a role" and no invitation is created.
- **AC 1.1.7** [edge] Given the email provider rejects the send request, when I click Send for "ana@example.com" with role Member, then the form shows the error message decided in Open questions and the pending list count is unchanged. (Blocked: message and pending-state decision are open.)

### Story 1.2: Invite several teammates at once
As a workspace admin, I want to paste multiple email addresses and assign one role to them, so that I can onboard a team quickly.

#### Acceptance criteria
- **AC 1.2.1** Given I paste 5 valid, distinct addresses separated by commas and select Viewer, when I click Send, then 5 invitations with role Viewer appear in the pending list and 5 emails are sent.
- **AC 1.2.2** [edge] Given I paste 3 valid addresses and 1 invalid one, when I click Send, then the 3 valid invitations appear in the pending list, 3 emails are sent, and the form lists the invalid address with "Enter a valid email address".
- **AC 1.2.3** [edge] Given the workspace has 98 pending invitations, when I submit 5 valid distinct addresses, then no invitations are created, no emails are sent, the pending count stays 98 and the form shows "Limit of 100 pending invitations exceeded".
- **AC 1.2.4** [edge] Given the workspace has 95 pending invitations, when I submit 5 valid distinct addresses, then 5 invitations are created and the pending count is 100.
- **AC 1.2.5** [edge] Given the workspace has 96 pending invitations, when I submit 5 valid distinct addresses, then no invitations are created and the form shows "Limit of 100 pending invitations exceeded".
- **AC 1.2.6** [edge] Given I paste "ana@example.com,ana@example.com" and select Viewer, when I click Send, then 1 invitation appears in the pending list and 1 email is sent.
- **AC 1.2.7** [edge] Given the workspace has 100 pending invitations, when I submit 1 valid address, then no invitation is created and the form shows "Limit of 100 pending invitations exceeded".

## Unit 2: Accept an invitation

### Story 2.1: Join the workspace from the email
As an invitee, I want to accept through the link in my email, so that I join the workspace with the role I was given.

#### Acceptance criteria
- **AC 2.1.1** Given I have an existing account and a pending, unexpired invitation as Member, when I click Accept on the invitation page, then I land on the workspace home page (path /home) and my profile shows the role "Member".
- **AC 2.1.5** [edge] Given the invitation was sent 6 days 23 hours ago, when I click Accept on the invitation page, then I am added to the workspace with the invited role.
- **AC 2.1.6** [edge] Given the invitation was sent 7 days 1 hour ago, when I open the link, then the page shows "This invitation has expired" and I am not added to the workspace.
- **AC 2.1.2** [edge] Given the invitation was sent 8 days ago, when I open the link, then the page shows "This invitation has expired" and I am not added to the workspace.
- **AC 2.1.3** [edge] Given an admin revoked the invitation, when I open the link, then the page shows "This invitation is no longer valid" and I am not added to the workspace.
- **AC 2.1.4** [edge] Given the invitation was already accepted, when I open the link a second time, then the page shows "This invitation has already been used" and the member count does not change.

## Unit 3: Manage pending invitations

### Story 3.1: Revoke or resend an invitation
As a workspace admin, I want to revoke or resend a pending invitation, so that I can fix mistakes and nudge people who have not responded.

#### Acceptance criteria
- **AC 3.1.1** Given a pending invitation for "ana@example.com", when I click Revoke and then click Confirm in the dialog, then it disappears from the pending list and its link shows "This invitation is no longer valid".
- **AC 3.1.2** Given a pending invitation sent 3 days ago, when I click Resend, then exactly one new email is sent to the address and the expiry date shown in the pending list is the resend time plus 7 days.
- **AC 3.1.3** [edge] Given I am signed in as a Member, when I open the Invite page, then I see "Only admins can invite teammates" and no invitation form is shown.
- **AC 3.1.4** [edge] Given I am signed in as a Viewer, when I open the Invite page, then I see "Only admins can invite teammates" and no invitation form is shown.
- **AC 3.1.5** [edge] Given I am signed in as a Member, when I send an invitation request directly to the invite API, then the response status is 403 and no invitation is created.
- **AC 3.1.6** [edge] Given a pending invitation for "ana@example.com", when I click Revoke and then click Cancel in the dialog, then the invitation remains in the pending list and its link is still valid.

## Review
- **Verdict:** draft. Not approved.
- **Rewritten:** 5 (AC 1.2.2, 1.2.3, 2.1.1, 3.1.1, 3.1.2).
- **Added:** 13 (AC 1.1.4 to 1.1.7, 1.2.4 to 1.2.7, 2.1.5, 2.1.6, 3.1.4 to 3.1.6).
- **Unresolved:**
  - AC 1.1.7 is blocked: the failure message and whether the invitation stays pending are undecided.
  - The roles and the admin-invites-admin question in Open questions contradict the Assumptions list and remain unconfirmed.
  - Exact 7-day expiry boundary is undecided.
  - The home page path "/home" in AC 2.1.1 is my placeholder and must be confirmed.
  - The no-account accept path has no criterion until the sign-up fields are decided.
  - Seat or plan limit, domain restriction, wrong-account sign-in, resend invalidating the old link, and inviting an existing member are undecided with no criteria.
  - Duplicate with a different role (AC 1.1.2) and case-insensitive duplicates (AC 1.1.4) rest on stated assumptions.
